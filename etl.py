"""
etl.py — Spotify Data Pipeline
================================
Paso 1 del pipeline: limpia el CSV y lo carga en PostgreSQL.

Uso:
    python etl.py

Requiere:
    pip install pandas psycopg2-binary sqlalchemy python-dotenv
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# ── Configuración ─────────────────────────────────────────────────────────────
load_dotenv()                          # Lee el archivo .env si existe

DB_USER     = os.getenv("DB_USER",     "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "tu_password_aqui")
DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_PORT     = os.getenv("DB_PORT",     "5432")
DB_NAME     = os.getenv("DB_NAME",     "spotify_db")

CSV_PATH    = os.path.join(os.path.dirname(__file__), "Popular_Spotify_Songs.csv")

# ── 1. Extracción ─────────────────────────────────────────────────────────────
def extract(path: str) -> pd.DataFrame:
    """Lee el CSV original."""
    print("[EXTRACT] Leyendo CSV...")
    df = pd.read_csv(path, encoding="latin1")
    print(f"  → {len(df):,} filas cargadas | {df.shape[1]} columnas")
    return df


# ── 2. Transformación ─────────────────────────────────────────────────────────
def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y transforma el DataFrame."""
    print("[TRANSFORM] Limpiando datos...")
    original_rows = len(df)

    # --- Renombrar columnas para que sean amigables en SQL ---
    df = df.rename(columns={
        "track_name":          "track_name",
        "artist(s)_name":      "artist_name",
        "artist_count":        "artist_count",
        "released_year":       "released_year",
        "released_month":      "released_month",
        "released_day":        "released_day",
        "in_spotify_playlists":"in_spotify_playlists",
        "in_spotify_charts":   "in_spotify_charts",
        "streams":             "streams",
        "in_apple_playlists":  "in_apple_playlists",
        "in_apple_charts":     "in_apple_charts",
        "in_deezer_playlists": "in_deezer_playlists",
        "in_deezer_charts":    "in_deezer_charts",
        "in_shazam_charts":    "in_shazam_charts",
        "bpm":                 "bpm",
        "key":                 "musical_key",
        "mode":                "mode",
        "danceability_%":      "danceability",
        "valence_%":           "valence",
        "energy_%":            "energy",
        "acousticness_%":      "acousticness",
        "instrumentalness_%":  "instrumentalness",
        "liveness_%":          "liveness",
        "speechiness_%":       "speechiness",
    })

    # --- Convertir streams a número (viene como string con posibles comas) ---
    df["streams"] = pd.to_numeric(
        df["streams"].astype(str).str.replace(",", ""), errors="coerce"
    )

    # --- Convertir columnas numéricas que pueden tener strings ---
    for col in ["in_deezer_playlists", "in_shazam_charts"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # --- Eliminar filas sin streams (no tienen valor para el análisis) ---
    df = df.dropna(subset=["streams"])
    df["streams"] = df["streams"].astype("int64")

    # --- Crear columna de fecha de lanzamiento ---
    df["release_date"] = pd.to_datetime(
        dict(year=df["released_year"],
             month=df["released_month"],
             day=df["released_day"]),
        errors="coerce"
    )

    # --- Streams en millones (columna adicional útil para visualizaciones) ---
    df["streams_millions"] = (df["streams"] / 1_000_000).round(2)

    # --- Llenar nulos en musical_key con "Unknown" ---
    df["musical_key"] = df["musical_key"].fillna("Unknown")
    df["in_shazam_charts"] = df["in_shazam_charts"].fillna(0).astype(int)
    df["in_deezer_playlists"] = df["in_deezer_playlists"].fillna(0).astype(int)

    # --- Reporte de limpieza ---
    removed = original_rows - len(df)
    print(f"  → {removed} filas eliminadas (streams nulos)")
    print(f"  → {len(df):,} filas limpias listas para cargar")
    print(f"  → Nulos restantes: {df.isnull().sum().sum()}")
    return df.reset_index(drop=True)


# ── 3. Carga ──────────────────────────────────────────────────────────────────
def load(df: pd.DataFrame) -> None:
    """Crea la base de datos si no existe y carga los datos."""
    print(f"[LOAD] Conectando a PostgreSQL ({DB_HOST}:{DB_PORT})...")

    # Conectar al servidor (sin especificar base de datos) para crearla si no existe
    engine_server = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres",
        isolation_level="AUTOCOMMIT"
    )
    with engine_server.connect() as conn:
        exists = conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        ).fetchone()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{DB_NAME}"'))
            print(f"  → Base de datos '{DB_NAME}' creada.")
        else:
            print(f"  → Base de datos '{DB_NAME}' ya existe.")
    engine_server.dispose()

    # Conectar a la base de datos del proyecto
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Cargar tabla principal (reemplaza si ya existe)
    df.to_sql(
        name="songs",
        con=engine,
        if_exists="replace",
        index=True,
        index_label="id",
        method="multi",
        chunksize=500,
    )
    print(f"  → Tabla 'songs' cargada con {len(df):,} registros.")

    # Crear índices para mejorar velocidad de consultas
    with engine.connect() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_songs_artist ON songs(artist_name)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_songs_year   ON songs(released_year)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_songs_streams ON songs(streams DESC)"))
        conn.commit()
    print("  → Índices creados sobre artist_name, released_year, streams.")

    engine.dispose()


# ── 4. Validación ─────────────────────────────────────────────────────────────
def validate() -> None:
    """Confirma que la carga fue exitosa haciendo queries de validación."""
    print("[VALIDATE] Verificando carga...")
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM songs")).scalar()
        top1  = conn.execute(text(
            "SELECT track_name, artist_name, streams_millions FROM songs ORDER BY streams DESC LIMIT 1"
        )).fetchone()
        print(f"  → Total de filas en DB: {total:,}")
        print(f"  → Canción #1: '{top1[0]}' por {top1[1]} ({top1[2]:.1f}M streams)")
    engine.dispose()


# ── Runner ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  SPOTIFY ETL PIPELINE")
    print("=" * 55)

    raw_df    = extract(CSV_PATH)
    clean_df  = transform(raw_df)
    load(clean_df)
    validate()

    print("=" * 55)
    print("  Pipeline completado exitosamente.")
    print("=" * 55)

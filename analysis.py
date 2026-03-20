"""
analysis.py — Análisis con Python + conexión a PostgreSQL
==========================================================
Paso 2: Lee los datos de PostgreSQL, genera gráficos con Python
y exporta tablas limpias para Power BI.

Uso:
    python analysis.py

Requiere que etl.py haya corrido primero.
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_USER     = os.getenv("DB_USER",     "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "tu_password_aqui")
DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_PORT     = os.getenv("DB_PORT",     "5432")
DB_NAME     = os.getenv("DB_NAME",     "spotify_db")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

sns.set_theme(style="darkgrid")
plt.rcParams["figure.dpi"] = 150

# ── Conexión ──────────────────────────────────────────────────────────────────
def get_engine():
    return create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )


def query(sql: str) -> pd.DataFrame:
    engine = get_engine()
    df = pd.read_sql(sql, engine)
    engine.dispose()
    return df


# ── Gráficos ──────────────────────────────────────────────────────────────────

def plot_top_artists():
    print("  → Generando: Top artistas...")
    df = query("""
        SELECT artist_name, COUNT(*) AS canciones
        FROM songs
        GROUP BY artist_name
        ORDER BY canciones DESC
        LIMIT 15
    """)
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = sns.color_palette("viridis", len(df))
    bars = ax.barh(df["artist_name"][::-1], df["canciones"][::-1], color=colors[::-1])
    ax.bar_label(bars, padding=4, fontsize=9)
    ax.set_xlabel("Número de canciones en el top", fontsize=11)
    ax.set_title("Top 15 Artistas con Más Canciones Populares en Spotify", fontsize=13, fontweight="bold")
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "01_top_artistas.png"))
    plt.close()


def plot_streams_distribution():
    print("  → Generando: Distribución de streams...")
    df = query("SELECT streams_millions FROM songs")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].hist(df["streams_millions"], bins=40, color="#1DB954", edgecolor="white", alpha=0.85)
    axes[0].set_xlabel("Streams (millones)")
    axes[0].set_ylabel("Frecuencia")
    axes[0].set_title("Distribución Normal")

    import numpy as np
    axes[1].hist(np.log10(df["streams_millions"] + 1), bins=40, color="#191414", edgecolor="#1DB954", alpha=0.85)
    axes[1].set_xlabel("log₁₀(Streams en millones)")
    axes[1].set_title("Distribución Logarítmica (más clara)")

    plt.suptitle("¿Cómo se distribuyen los streams?", fontsize=14, fontweight="bold")
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "02_distribucion_streams.png"))
    plt.close()


def plot_audio_correlation():
    print("  → Generando: Correlación de audio features...")
    df = query("""
        SELECT bpm, danceability, valence, energy, acousticness,
               instrumentalness, liveness, speechiness, streams_millions
        FROM songs
    """)
    import numpy as np
    corr = df.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm",
                center=0, linewidths=0.5, ax=ax, square=True, cbar_kws={"shrink": 0.8})
    ax.set_title("Correlación entre Características de Audio y Streams", fontsize=13, fontweight="bold")
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "03_correlacion_audio.png"))
    plt.close()


def plot_yearly_trend():
    print("  → Generando: Tendencia anual...")
    df = query("""
        SELECT released_year,
               COUNT(*) AS canciones,
               ROUND(AVG(streams_millions)::numeric, 2) AS streams_prom
        FROM songs
        WHERE released_year >= 2010
        GROUP BY released_year
        ORDER BY released_year
    """)
    fig, ax1 = plt.subplots(figsize=(12, 5))
    color1, color2 = "#1DB954", "#FF6B6B"
    ax1.fill_between(df["released_year"], df["canciones"], alpha=0.3, color=color1)
    ax1.plot(df["released_year"], df["canciones"], "o-", color=color1, linewidth=2, label="Canciones")
    ax1.set_xlabel("Año")
    ax1.set_ylabel("Cantidad de canciones populares", color=color1)
    ax1.tick_params(axis="y", labelcolor=color1)
    ax2 = ax1.twinx()
    ax2.plot(df["released_year"], df["streams_prom"], "s--", color=color2, linewidth=2, label="Streams prom. (M)")
    ax2.set_ylabel("Streams promedio (millones)", color=color2)
    ax2.tick_params(axis="y", labelcolor=color2)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    ax1.set_title("Canciones Populares y Streams Promedio por Año (2010–2023)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "04_tendencia_anual.png"))
    plt.close()


def plot_danceability_vs_streams():
    print("  → Generando: Danceability vs Streams...")
    df = query("SELECT danceability, streams_millions, energy FROM songs")
    fig, ax = plt.subplots(figsize=(10, 6))
    sc = ax.scatter(df["danceability"], df["streams_millions"],
                    c=df["energy"], cmap="plasma", alpha=0.5, s=25)
    plt.colorbar(sc, ax=ax, label="Energy (%)")
    ax.set_xlabel("Danceability (%)")
    ax.set_ylabel("Streams (millones)")
    ax.set_title("¿Las Canciones Más Bailables Tienen Más Streams?", fontsize=13, fontweight="bold")
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "05_danceability_streams.png"))
    plt.close()


def plot_major_vs_minor():
    print("  → Generando: Major vs Minor...")
    df = query("SELECT mode, streams_millions, valence FROM songs")
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    sns.boxplot(data=df, x="mode", y="streams_millions",
                palette=["#1DB954", "#191414"], ax=axes[0])
    axes[0].set_title("Streams por Modo Musical")
    axes[0].set_xlabel("Modo")
    axes[0].set_ylabel("Streams (millones)")
    sns.violinplot(data=df, x="mode", y="valence",
                   palette=["#1DB954", "#191414"], ax=axes[1])
    axes[1].set_title("Positividad (Valence) por Modo")
    axes[1].set_xlabel("Modo")
    axes[1].set_ylabel("Valence (%)")
    plt.suptitle("Major vs Minor: ¿Importa el Modo Musical?", fontsize=14, fontweight="bold")
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "06_major_vs_minor.png"))
    plt.close()


# ── Exportar CSVs para Power BI ───────────────────────────────────────────────

def export_for_powerbi():
    """
    Exporta tablas limpias como CSV.
    Power BI puede leer CSVs directamente además de conectarse a PostgreSQL.
    """
    print("\n[EXPORT] Generando CSVs para Power BI...")

    exports = {
        "powerbi_songs.csv": "SELECT * FROM songs",
        "powerbi_artistas.csv": "SELECT * FROM vw_artistas",
        "powerbi_tendencia.csv": "SELECT * FROM vw_tendencia_anual",
        "powerbi_top100.csv": "SELECT * FROM vw_top100",
    }

    for filename, sql in exports.items():
        df = query(sql)
        path = os.path.join(OUTPUT_DIR, filename)
        df.to_csv(path, index=False, encoding="utf-8-sig")  # utf-8-sig funciona mejor en Excel/Power BI
        print(f"  → {filename} ({len(df):,} filas)")

    print("  Todos los CSVs exportados a /outputs/")


# ── Runner ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  SPOTIFY ANALYSIS — Python + PostgreSQL")
    print("=" * 55)

    print("\n[PLOTS] Generando visualizaciones...")
    plot_top_artists()
    plot_streams_distribution()
    plot_audio_correlation()
    plot_yearly_trend()
    plot_danceability_vs_streams()
    plot_major_vs_minor()
    print(f"  Gráficos guardados en /outputs/")

    export_for_powerbi()

    print("\n" + "=" * 55)
    print("  Análisis completado.")
    print("  Próximo paso: Abrir Power BI y conectar /outputs/powerbi_songs.csv")
    print("=" * 55)

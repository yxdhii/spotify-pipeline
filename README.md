# 🎵 Spotify Data Analysis — Pipeline Completo

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=flat&logo=postgresql&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Desktop-F2C811?style=flat&logo=powerbi&logoColor=black)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=flat&logo=pandas)

Pipeline de análisis de datos end-to-end sobre las 952 canciones más populares de Spotify hasta 2023. El proyecto responde preguntas de negocio reales usando Python, PostgreSQL y Power BI — exactamente como se trabaja en una empresa de datos.

---

## 🏗️ Arquitectura del Proyecto

```
CSV (datos crudos)
    ↓
Python ETL (etl.py)       ← Limpieza, transformación y carga
    ↓
PostgreSQL (spotify_db)   ← Base de datos con 15 queries SQL
    ↓
Python (analysis.py)      ← Gráficos y exportación
    ↓
Power BI                  ← Dashboard interactivo final
```

---

## ❓ Preguntas de Negocio

1. ¿Cuáles son los artistas con más canciones populares?
2. ¿Cómo se distribuyen los streams? ¿El éxito es parejo o concentrado?
3. ¿Las canciones bailables tienen más streams?
4. ¿Importa el modo musical (Major vs Minor)?
5. ¿Hay un BPM óptimo para las canciones más escuchadas?
6. ¿Cuándo se lanzan más canciones exitosas?
7. ¿Las canciones en más playlists tienen más streams?
8. ¿Qué plataforma domina en charts: Spotify, Apple o Deezer?

---

## 📁 Estructura del Proyecto

```
spotify-pipeline/
│
├── Popular_Spotify_Songs.csv    ← Dataset original
├── etl.py                       ← Limpieza y carga a PostgreSQL
├── analysis.py                  ← Gráficos Python + exportación
├── requirements.txt             ← Dependencias
├── .env.example                 ← Plantilla de credenciales
│
├── sql/
│   └── queries.sql              ← 15 consultas SQL + 4 vistas
│
└── outputs/                     ← Generado automáticamente
    ├── 01_top_artistas.png
    ├── 02_distribucion_streams.png
    ├── 03_correlacion_audio.png
    ├── 04_tendencia_anual.png
    ├── 05_danceability_streams.png
    ├── 06_major_vs_minor.png
    └── Spotify Analysis.pbix    ← Dashboard Power BI
```

---

## ⚙️ Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/spotify-pipeline.git
cd spotify-pipeline

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar credenciales
cp .env.example .env
# Editar .env con tu contraseña de PostgreSQL

# 4. Correr el pipeline
python etl.py
python analysis.py
```

---

## 📊 Dashboard Power BI

El dashboard incluye:
- 4 tarjetas KPI: Total Streams, Total Canciones, Artistas Únicos, BPM Promedio
- Gráfico de barras: Top artistas por streams
- Gráfico de dona: Major vs Minor
- Scatter plot: Danceability vs Streams
- Línea de tendencia: Streams por año
- Tabla: Top 100 canciones más escuchadas

---

## 🔍 Hallazgos Principales

| Pregunta | Hallazgo |
|----------|----------|
| Artista más prolífico | **Taylor Swift** con 34 canciones en el top |
| Canción más escuchada | **Blinding Lights** (The Weeknd) — 3,700M+ streams |
| Distribución | Fuertemente sesgada — pocos artistas acumulan la mayoría |
| Modo musical | Canciones en **Major** tienen streams ligeramente más altos |
| BPM óptimo | Entre **100–139 BPM** tienen el promedio más alto |
| Año pico | **2022** concentra más canciones populares |

---

## 🛠️ Tecnologías

| Herramienta | Uso |
|-------------|-----|
| **Python** | ETL, limpieza, visualizaciones |
| **Pandas** | Manipulación del dataset |
| **SQLAlchemy + psycopg2** | Conexión a PostgreSQL |
| **Matplotlib / Seaborn** | Gráficos exploratorios |
| **PostgreSQL** | Base de datos, queries SQL |
| **Power BI** | Dashboard interactivo |

---

## 📄 Dataset

**Fuente:** [Kaggle — Top Spotify Songs 2023](https://www.kaggle.com/datasets/nelgiriyewithana/top-spotify-songs-2023)
**Registros:** 952 canciones | **Columnas:** 24 | **Período:** 1930–2023

---

*Proyecto de portfolio — Data Analysis con Python · PostgreSQL · Power BI*

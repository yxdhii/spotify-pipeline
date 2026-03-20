-- =============================================================
-- queries.sql — Spotify Data Analysis
-- =============================================================
-- Cómo usar: Abre pgAdmin o DBeaver, conecta a spotify_db,
-- y ejecuta cada bloque de consulta individualmente.
-- =============================================================


-- =============================================================
-- SECCIÓN 1: VISIÓN GENERAL DEL DATASET
-- =============================================================

-- Q1. ¿Cuántas canciones y artistas únicos hay?
SELECT
    COUNT(*)                          AS total_canciones,
    COUNT(DISTINCT artist_name)       AS artistas_unicos,
    MIN(released_year)                AS año_mas_antiguo,
    MAX(released_year)                AS año_mas_reciente,
    ROUND(AVG(streams_millions)::numeric, 2)   AS streams_promedio_M,
    MAX(streams_millions)             AS streams_maximo_M
FROM songs;


-- Q2. ¿Cuántas canciones hay por año de lanzamiento? (tendencia)
SELECT
    released_year,
    COUNT(*)                        AS canciones,
    ROUND(AVG(streams_millions)::numeric, 2) AS streams_prom_M,
    SUM(streams)                    AS streams_total
FROM songs
GROUP BY released_year
ORDER BY released_year DESC;


-- =============================================================
-- SECCIÓN 2: ARTISTAS
-- =============================================================

-- Q3. Top 15 artistas con más canciones en el top de Spotify
SELECT
    artist_name,
    COUNT(*)                        AS canciones_en_top,
    ROUND(SUM(streams_millions)::numeric, 0) AS streams_totales_M,
    ROUND(AVG(streams_millions)::numeric, 2) AS streams_prom_por_cancion_M
FROM songs
GROUP BY artist_name
ORDER BY canciones_en_top DESC
LIMIT 15;


-- Q4. Top 10 artistas por total de streams
SELECT
    artist_name,
    COUNT(*)                           AS canciones,
    ROUND(SUM(streams_millions)::numeric, 1)    AS total_streams_M,
    ROUND(AVG(streams_millions)::numeric, 2)    AS prom_streams_M
FROM songs
GROUP BY artist_name
ORDER BY total_streams_M DESC
LIMIT 10;


-- Q5. ¿Los artistas colaborativos tienen más streams que los solistas?
SELECT
    CASE
        WHEN artist_count = 1 THEN 'Solista'
        WHEN artist_count = 2 THEN '2 artistas'
        ELSE '3+ artistas'
    END AS tipo_colaboracion,
    COUNT(*)                        AS canciones,
    ROUND(AVG(streams_millions)::numeric, 2) AS streams_prom_M,
    ROUND(MAX(streams_millions)::numeric, 2) AS streams_max_M
FROM songs
GROUP BY tipo_colaboracion
ORDER BY streams_prom_M DESC;


-- =============================================================
-- SECCIÓN 3: CARACTERÍSTICAS DE AUDIO
-- =============================================================

-- Q6. ¿Qué modo musical (Major/Minor) tiene más streams?
SELECT
    mode,
    COUNT(*)                        AS canciones,
    ROUND(AVG(streams_millions)::numeric, 2) AS streams_prom_M,
    ROUND(AVG(danceability)::numeric, 1)     AS danceability_prom,
    ROUND(AVG(energy)::numeric, 1)           AS energy_prom,
    ROUND(AVG(valence)::numeric, 1)          AS valence_prom
FROM songs
GROUP BY mode
ORDER BY streams_prom_M DESC;


-- Q7. ¿Cuál es la tonalidad (key) más común en las canciones populares?
SELECT
    musical_key,
    COUNT(*)                          AS canciones,
    ROUND(AVG(streams_millions)::numeric, 2)   AS streams_prom_M
FROM songs
WHERE musical_key != 'Unknown'
GROUP BY musical_key
ORDER BY canciones DESC;


-- Q8. Correlación visual: rangos de danceability vs streams promedio
SELECT
    CASE
        WHEN danceability < 30  THEN '0–29  (poco bailable)'
        WHEN danceability < 50  THEN '30–49'
        WHEN danceability < 70  THEN '50–69'
        WHEN danceability < 85  THEN '70–84'
        ELSE                         '85–100 (muy bailable)'
    END AS rango_danceability,
    COUNT(*)                        AS canciones,
    ROUND(AVG(streams_millions)::numeric, 2) AS streams_prom_M
FROM songs
GROUP BY rango_danceability
ORDER BY rango_danceability;


-- Q9. ¿Existe un BPM óptimo para tener más streams?
SELECT
    CASE
        WHEN bpm < 80  THEN '< 80 BPM (lento)'
        WHEN bpm < 100 THEN '80–99 BPM'
        WHEN bpm < 120 THEN '100–119 BPM'
        WHEN bpm < 140 THEN '120–139 BPM'
        WHEN bpm < 160 THEN '140–159 BPM'
        ELSE                '160+ BPM (rápido)'
    END AS rango_bpm,
    COUNT(*)                        AS canciones,
    ROUND(AVG(streams_millions)::numeric, 2) AS streams_prom_M,
    ROUND(AVG(danceability)::numeric, 1)     AS danceability_prom
FROM songs
GROUP BY rango_bpm
ORDER BY streams_prom_M DESC;


-- =============================================================
-- SECCIÓN 4: PLATAFORMAS
-- =============================================================

-- Q10. Top 10 canciones con más presencia total en playlists (todas las plataformas)
SELECT
    track_name,
    artist_name,
    in_spotify_playlists,
    in_apple_playlists,
    in_deezer_playlists,
    (in_spotify_playlists + in_apple_playlists + in_deezer_playlists) AS total_playlists,
    ROUND(streams_millions::numeric, 1) AS streams_M
FROM songs
ORDER BY total_playlists DESC
LIMIT 10;


-- Q11. ¿Las canciones en más playlists de Spotify tienen más streams?
SELECT
    CASE
        WHEN in_spotify_playlists < 1000  THEN '0–999'
        WHEN in_spotify_playlists < 5000  THEN '1K–4.9K'
        WHEN in_spotify_playlists < 10000 THEN '5K–9.9K'
        WHEN in_spotify_playlists < 20000 THEN '10K–19.9K'
        ELSE                                   '20K+'
    END AS rango_playlists_spotify,
    COUNT(*)                        AS canciones,
    ROUND(AVG(streams_millions)::numeric, 2) AS streams_prom_M
FROM songs
GROUP BY rango_playlists_spotify
ORDER BY streams_prom_M DESC;


-- Q12. Comparación entre plataformas: ¿Spotify, Apple o Deezer tienen más canciones en charts?
SELECT
    'Spotify'    AS plataforma, SUM(in_spotify_charts)    AS total_apariciones_charts FROM songs
UNION ALL
SELECT
    'Apple'      AS plataforma, SUM(in_apple_charts)      AS total_apariciones_charts FROM songs
UNION ALL
SELECT
    'Deezer'     AS plataforma, SUM(in_deezer_charts)     AS total_apariciones_charts FROM songs
UNION ALL
SELECT
    'Shazam'     AS plataforma, SUM(in_shazam_charts)     AS total_apariciones_charts FROM songs
ORDER BY total_apariciones_charts DESC;


-- =============================================================
-- SECCIÓN 5: RANKING Y TOP CANCIONES
-- =============================================================

-- Q13. Top 20 canciones más escuchadas de la historia del dataset
SELECT
    ROW_NUMBER() OVER (ORDER BY streams DESC) AS ranking,
    track_name,
    artist_name,
    released_year,
    ROUND(streams_millions::numeric, 1)              AS streams_M,
    bpm,
    danceability,
    energy,
    valence
FROM songs
ORDER BY streams DESC
LIMIT 20;


-- Q14. ¿Cuáles son los mejores lanzamientos de cada año? (top 1 por año)
SELECT DISTINCT ON (released_year)
    released_year,
    track_name,
    artist_name,
    ROUND(streams_millions::numeric, 1) AS streams_M
FROM songs
WHERE released_year >= 2015
ORDER BY released_year DESC, streams DESC;


-- Q15. ¿Qué mes del año tiene más lanzamientos populares?
SELECT
    TO_CHAR(TO_DATE(released_month::text, 'MM'), 'Month') AS mes,
    released_month,
    COUNT(*) AS canciones,
    ROUND(AVG(streams_millions)::numeric, 2) AS streams_prom_M
FROM songs
GROUP BY released_month
ORDER BY released_month;


-- =============================================================
-- SECCIÓN 6: VISTAS (para conectar con Power BI)
-- =============================================================

-- Estas vistas crean tablas virtuales que Power BI puede importar directamente.

-- Vista 1: Resumen por artista (para el gráfico de barras de Power BI)
CREATE OR REPLACE VIEW vw_artistas AS
SELECT
    artist_name,
    COUNT(*)                           AS total_canciones,
    ROUND(SUM(streams_millions)::numeric, 1)    AS total_streams_M,
    ROUND(AVG(streams_millions)::numeric, 2)    AS avg_streams_M,
    ROUND(AVG(danceability)::numeric, 1)        AS avg_danceability,
    ROUND(AVG(energy)::numeric, 1)              AS avg_energy,
    ROUND(AVG(bpm)::numeric, 0)                 AS avg_bpm
FROM songs
GROUP BY artist_name;


-- Vista 2: Resumen por año (para la línea de tendencia de Power BI)
CREATE OR REPLACE VIEW vw_tendencia_anual AS
SELECT
    released_year,
    COUNT(*)                           AS total_canciones,
    ROUND(SUM(streams_millions)::numeric, 0)    AS total_streams_M,
    ROUND(AVG(streams_millions)::numeric, 2)    AS avg_streams_M,
    ROUND(AVG(danceability)::numeric, 1)        AS avg_danceability,
    ROUND(AVG(energy)::numeric, 1)              AS avg_energy,
    ROUND(AVG(bpm)::numeric, 1)                 AS avg_bpm
FROM songs
GROUP BY released_year
ORDER BY released_year;


-- Vista 3: Características de audio promedio por modo (Major/Minor)
CREATE OR REPLACE VIEW vw_audio_por_modo AS
SELECT
    mode,
    COUNT(*)                          AS canciones,
    ROUND(AVG(streams_millions)::numeric, 2)   AS avg_streams_M,
    ROUND(AVG(danceability)::numeric, 1)       AS avg_danceability,
    ROUND(AVG(energy)::numeric, 1)             AS avg_energy,
    ROUND(AVG(valence)::numeric, 1)            AS avg_valence,
    ROUND(AVG(acousticness)::numeric, 1)       AS avg_acousticness,
    ROUND(AVG(bpm)::numeric, 1)                AS avg_bpm
FROM songs
GROUP BY mode;


-- Vista 4: Top 100 canciones (tabla principal de Power BI)
CREATE OR REPLACE VIEW vw_top100 AS
SELECT
    ROW_NUMBER() OVER (ORDER BY streams DESC) AS ranking,
    track_name,
    artist_name,
    released_year,
    released_month,
    mode,
    musical_key,
    ROUND(streams_millions::numeric, 1)    AS streams_M,
    bpm,
    danceability,
    energy,
    valence,
    in_spotify_playlists,
    in_apple_playlists,
    in_deezer_playlists
FROM songs
ORDER BY streams DESC
LIMIT 100;

import os
import requests
import pandas as pd
import streamlit as st
from google.cloud import bigquery


# =========================
# Config & Clients
# =========================

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "movie-project-453208")
MOVIES_TABLE = os.getenv("BQ_MOVIES_TABLE", f"{PROJECT_ID}.movies_dataset.movies")
RATINGS_TABLE = os.getenv("BQ_RATINGS_TABLE", f"{PROJECT_ID}.ratings_dataset.ratings")

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")  # ne pas hardcoder une clé dans GitHub
TMDB_LANG = os.getenv("TMDB_LANG", "fr-FR")

# Support optionnel d'un fichier local bigquery-key.json sans l'imposer
if os.path.exists("bigquery-key.json") and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath("bigquery-key.json")

try:
    bq_client = bigquery.Client()
except Exception:
    bq_client = None


# =========================
# Data access
# =========================

@st.cache_data(ttl=300, show_spinner=False)
def search_movies(query: str, language: str, genre: str, min_year: int, min_rating: float) -> pd.DataFrame:
    """
    Safe BigQuery search using query parameters (avoids SQL injection).
    Returns top 20 matches sorted by avg rating.
    """
    if bq_client is None:
        return pd.DataFrame()

    sql = f"""
    SELECT
      m.movieId,
      m.title,
      m.genres,
      m.release_year,
      m.language,
      m.country,
      COALESCE(AVG(r.rating), 0) AS avg_rating
    FROM `{MOVIES_TABLE}` AS m
    LEFT JOIN `{RATINGS_TABLE}` AS r
      ON m.movieId = r.movieId
    WHERE m.release_year >= @min_year
    """

    params = [
        bigquery.ScalarQueryParameter("min_year", "INT64", int(min_year)),
        bigquery.ScalarQueryParameter("min_rating", "FLOAT64", float(min_rating)),
    ]

    if query:
        sql += " AND LOWER(m.title) LIKE CONCAT('%', LOWER(@query), '%')"
        params.append(bigquery.ScalarQueryParameter("query", "STRING", query))

    if language:
        sql += " AND m.language = @language"
        params.append(bigquery.ScalarQueryParameter("language", "STRING", language))

    if genre:
        sql += " AND m.genres LIKE CONCAT('%', @genre, '%')"
        params.append(bigquery.ScalarQueryParameter("genre", "STRING", genre))

    sql += """
    GROUP BY m.movieId, m.title, m.genres, m.release_year, m.language, m.country
    HAVING avg_rating >= @min_rating
    ORDER BY avg_rating DESC
    LIMIT 20
    """

    job_config = bigquery.QueryJobConfig(query_parameters=params)
    return bq_client.query(sql, job_config=job_config).to_dataframe()


@st.cache_data(ttl=3600, show_spinner=False)
def get_movie_details(movie_id: int) -> dict | None:
    """
    Fetch movie details from TMDB. Returns None if no API key or request fails.
    """
    if not TMDB_API_KEY:
        return None

    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": TMDB_API_KEY, "language": TMDB_LANG}

    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException:
        pass

    return None


def poster_url(details: dict | None, size: str = "w500") -> str | None:
    if not details:
        return None
    path = details.get("poster_path")
    return f"https://image.tmdb.org/t/p/{size}{path}" if path else None


# =========================
# UI helpers
# =========================

def show_bigquery_status():
    if bq_client is None:
        st.error(
            "BigQuery n'est pas accessible (credentials/dataset manquants). "
            "Le projet dépend d'un dataset BigQuery (non inclus dans le repo). "
            "Voir README pour les détails."
        )
        st.stop()

def safe_slice_circular(df: pd.DataFrame, start: int, count: int) -> pd.DataFrame:
    """Circular slice to always return up to `count` rows even if we wrap around."""
    if df.empty:
        return df
    n = len(df)
    start = start % n
    end = start + count
    if end <= n:
        return df.iloc[start:end]
    return pd.concat([df.iloc[start:], df.iloc[: end - n]], axis=0)


# =========================
# Streamlit App
# =========================

st.set_page_config(page_title="Movie Explorer", page_icon="🎬", layout="wide")

st.title("🎬 Movie Explorer")
st.write("Recherche de films (BigQuery) + détails (TMDB).")

with st.sidebar:
    st.title("Navigation")
    page = st.radio("Aller à :", ["Accueil", "Rechercher un film"])
    st.markdown("---")
    if not TMDB_API_KEY:
        st.info("TMDB_API_KEY non défini → affiches/détails TMDB peuvent manquer.")


# -------- Accueil --------
if page == "Accueil":
    show_bigquery_status()

    st.header("🎥 Films les mieux notés (exemple)")
    top_movies = search_movies(query="", language="", genre="", min_year=1900, min_rating=4.0).head(10)

    if top_movies.empty:
        st.warning("Aucun résultat (dataset BigQuery indisponible ou vide).")
        st.stop()

    if "carousel_index" not in st.session_state:
        st.session_state.carousel_index = 0
    if "selected_movie" not in st.session_state:
        st.session_state.selected_movie = None

    nav_cols = st.columns([1, 8, 1])
    with nav_cols[0]:
        if st.button("⬅️", key="prev"):
            st.session_state.carousel_index -= 1
    with nav_cols[2]:
        if st.button("➡️", key="next"):
            st.session_state.carousel_index += 1

    visible_movies = safe_slice_circular(top_movies, st.session_state.carousel_index, 5)

    cols = st.columns(5, gap="medium")
    for col, (_, movie_data) in zip(cols, visible_movies.iterrows()):
        movie_id = int(movie_data["movieId"])
        movie_title = str(movie_data["title"])

        details = get_movie_details(movie_id)
        cover = poster_url(details, "w342")

        with col:
            if cover:
                st.image(cover, use_container_width=True, caption=movie_title)
            else:
                st.markdown(f"**{movie_title}**")
                st.caption("Pas d'affiche TMDB")

            if st.button("ℹ️ Détails", key=f"details-{movie_id}"):
                st.session_state.selected_movie = movie_id

    if st.session_state.selected_movie:
        details = get_movie_details(int(st.session_state.selected_movie))
        if details:
            st.markdown("---")
            st.subheader(details.get("title", "Détails du film"))
            cover = poster_url(details, "w500")
            if cover:
                st.image(cover, width=300)
            st.markdown(f"**Résumé :** {details.get('overview', 'Pas de résumé disponible.')}")
            st.markdown(f"**Date de sortie :** {details.get('release_date', '—')}")
            st.markdown(f"**Note moyenne (TMDB) :** {details.get('vote_average', '—')} ⭐")
        else:
            st.info("Détails TMDB indisponibles (clé manquante ou film non trouvé).")


# -------- Recherche --------
elif page == "Rechercher un film":
    show_bigquery_status()

    st.header("🔍 Rechercher un film")

    search_query = st.text_input("🔎 Titre du film :", "")
    language = st.selectbox("🌎 Langue :", ["", "en", "fr", "xx", "de", "es", "it"])
    genre = st.selectbox(
        "🎭 Genre :",
        ["", "(no genres listed)", "Action", "Adventure", "Comedy", "Crime", "Documentary",
         "Drama", "Fantasy", "Horror", "Musical", "Romance", "Sci-Fi", "Thriller", "Western"],
    )
    min_year = st.slider("📅 Année de sortie minimum :", 1900, 2026, 2000)
    min_rating = st.slider("⭐ Note minimum :", 0.0, 5.0, 3.0)

    if st.button("🔎 Rechercher"):
        results = search_movies(search_query, language, genre, min_year, min_rating)

        if results.empty:
            st.warning("Aucun film trouvé ! 🚨")
            st.stop()

        st.write("### 🎬 Résultats de la recherche")

        for _, row in results.iterrows():
            movie_id = int(row["movieId"])
            title = str(row["title"])
            year = row.get("release_year", "—")
            genres = row.get("genres", "—")
            lang = row.get("language", "—")
            rating = float(row.get("avg_rating", 0.0))

            details = get_movie_details(movie_id)
            cover = poster_url(details, "w342")
            overview = (details.get("overview") if details else None) or "Pas de description disponible."

            with st.container():
                c1, c2 = st.columns([1, 3], gap="large")

                with c1:
                    if cover:
                        st.image(cover, width=150)
                    else:
                        st.write("🎬 Pas d'affiche disponible")

                with c2:
                    st.markdown(f"## {title} ({year})")
                    st.markdown(f"**Genres :** {genres}")
                    st.markdown(f"**Langue :** {lang}")
                    st.markdown(f"**Note moyenne (BigQuery) :** {rating:.2f} ⭐")
                    st.markdown(f"**Résumé :** {overview}")

                st.markdown("---")

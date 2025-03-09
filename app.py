import streamlit as st
from google.cloud import bigquery
import pandas as pd
import requests
import os

# Authentification avec Google Cloud BigQuery
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "bigquery-key.json"
client = bigquery.Client()

# Clé API TMDB
TMDB_API_KEY = "045cfc313f4083174f4bad214f648341"

# --- 🔍 Fonction pour récupérer les films selon les filtres ---
def search_movies(query, language, genre, min_year, min_rating):
    sql = f"""
    SELECT m.movieId, m.title, m.genres, m.release_year, m.language, m.country, 
           COALESCE(AVG(r.rating), 0) AS avg_rating
    FROM `movie-project-453208.movies_dataset.movies` AS m
    LEFT JOIN `movie-project-453208.ratings_dataset.ratings` AS r
    ON m.movieId = r.movieId
    WHERE m.release_year >= {min_year}
    """

    if query:
        sql += f" AND LOWER(m.title) LIKE LOWER('%{query}%')"
    if language:
        sql += f" AND m.language = '{language}'"
    if genre:
        sql += f" AND m.genres LIKE '%{genre}%'"

    sql += f"""
    GROUP BY m.movieId, m.title, m.genres, m.release_year, m.language, m.country
    HAVING avg_rating >= {min_rating}
    ORDER BY avg_rating DESC
    LIMIT 20;
    """

    df = client.query(sql).to_dataframe()
    return df

# --- 🔍 Fonction pour récupérer les détails d’un film via TMDB ---
def get_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=fr-FR"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    return None

# --- 🎬 Interface Streamlit ---
st.title("🎬 Movie Explorer")
st.write("Bienvenue sur votre application de recherche de films !")

# Sidebar pour la navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller à :", ["Accueil", "Rechercher un film"])

# 🎬 **Page d'accueil**
if page == "Accueil":
    st.header("🎥 Films les plus populaires")

    top_movies = search_movies("", "", "", 1900, 4.0).head(10)

    if "carousel_index" not in st.session_state:
        st.session_state.carousel_index = 0

    nav_cols = st.columns([1, 8, 1])
    with nav_cols[0]:
        if st.button("⬅️", key="prev"):
            st.session_state.carousel_index = (st.session_state.carousel_index - 1) % len(top_movies)
    with nav_cols[2]:
        if st.button("➡️", key="next"):
            st.session_state.carousel_index = (st.session_state.carousel_index + 1) % len(top_movies)

    start_idx = st.session_state.carousel_index
    visible_movies = top_movies.iloc[start_idx:start_idx + 5]

    cols = st.columns(5, gap="medium")
    for idx, (col, row) in enumerate(zip(cols, visible_movies.iterrows())):
        movie_data = row[1]
        movie_title = movie_data["title"]
        movie_id = movie_data["movieId"]

        movie_details = get_movie_details(movie_id)
        cover_url = f"https://image.tmdb.org/t/p/w500{movie_details['poster_path']}" if movie_details and "poster_path" in movie_details else None

        with col:
            if cover_url:
                st.image(cover_url, use_container_width=True, caption=f"**{movie_title}**")
            if st.button(f"ℹ️ {movie_title[:10]}", key=f"details-{movie_id}"):
                st.session_state.selected_movie = movie_id

    if "selected_movie" in st.session_state:
        selected_movie_id = st.session_state.selected_movie
        movie_details = get_movie_details(selected_movie_id)

        if movie_details:
            with st.container():
                st.markdown("---")
                st.markdown(f"## {movie_details['title']}")
                st.image(f"https://image.tmdb.org/t/p/w500{movie_details['poster_path']}", width=300)
                st.markdown(f"**Résumé :** {movie_details['overview']}")
                st.markdown(f"**Date de sortie :** {movie_details['release_date']}")
                st.markdown(f"**Note moyenne :** {movie_details['vote_average']} ⭐")

# 🔎 **Page de recherche**
elif page == "Rechercher un film":
    st.header("🔍 Rechercher un film")

    search_query = st.text_input("🔎 Titre du film :", "")
    language = st.selectbox("🌎 Langue :", ["", "en", "fr", "xx", "de", "es", "it"])
    genre = st.selectbox("🎭 Genre :", ["", "(no genres listed)", "Action", "Adventure", "Comedy", "Crime", "Documentary",
                                        "Drama", "Fantasy", "Horror", "Musical", "Romance", "Sci-Fi", "Thriller", "Western"])
    min_year = st.slider("📅 Année de sortie minimum :", 1900, 2024, 2000)
    min_rating = st.slider("⭐ Note minimum :", 0.0, 5.0, 3.0)

    if st.button("🔎 Rechercher"):
        results = search_movies(search_query, language, genre, min_year, min_rating)
        
        if not results.empty:
            st.write("### 🎬 Résultats de la recherche")
            
            for _, row in results.iterrows():
                movie_id = row["movieId"]
                movie_title = row["title"]
                movie_year = row["release_year"]
                movie_genres = row["genres"]
                movie_language = row["language"]
                movie_rating = row["avg_rating"]

                movie_details = get_movie_details(movie_id)
                cover_url = f"https://image.tmdb.org/t/p/w500{movie_details['poster_path']}" if movie_details and "poster_path" in movie_details else None
                overview = movie_details["overview"] if movie_details and "overview" in movie_details else "Pas de description disponible."

                with st.container():
                    cols = st.columns([1, 3])
                    with cols[0]:
                        if cover_url:
                            st.image(cover_url, width=150)
                        else:
                            st.write("🎬 Pas d'affiche disponible")
                    with cols[1]:
                        st.markdown(f"## {movie_title} ({movie_year})")
                        st.markdown(f"**Genres :** {movie_genres}")
                        st.markdown(f"**Langue :** {movie_language}")
                        st.markdown(f"**Note moyenne :** {movie_rating} ⭐")
                        st.markdown(f"**Résumé :** {overview}")
                        st.markdown("---")

        else:
            st.warning("Aucun film trouvé ! 🚨")

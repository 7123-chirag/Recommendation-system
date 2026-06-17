import streamlit as st
import pickle
import requests
import pandas as pd

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

# =====================================
# LOAD DATA
# =====================================

movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
search_data = pickle.load(open('search_data.pkl', 'rb'))

# =====================================
# OMDB API
# =====================================

API_KEY = "7e4a34de"

def fetch_movie_details(movie_name):

    url = f"https://www.omdbapi.com/?apikey={API_KEY}&t={movie_name}"

    data = requests.get(url).json()

    poster = data.get("Poster", "")
    year = data.get("Year", "N/A")
    rating = data.get("imdbRating", "N/A")

    return poster, year, rating

# =====================================
# MOVIE RECOMMENDATION
# =====================================

def recommend(movie):

    movie_index = movies[
        movies['original_title'] == movie
    ].index[0]

    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []
    recommended_years = []
    recommended_ratings = []

    for i in movie_list:

        movie_name = movies.iloc[i[0]].original_title

        poster, year, rating = fetch_movie_details(movie_name)

        recommended_movies.append(movie_name)
        recommended_posters.append(poster)
        recommended_years.append(year)
        recommended_ratings.append(rating)

    return (
        recommended_movies,
        recommended_posters,
        recommended_years,
        recommended_ratings
    )

# =====================================
# GENRE + YEAR SEARCH
# =====================================

def search_movies(year, genre):

    genre = genre.lower()

    result = search_data[
        (search_data['release_year'] == year)
        &
        (
            search_data['genres'].apply(
                lambda x: genre in [g.lower() for g in x]
            )
        )
    ]

    result = result.sort_values(
        by='popularity',
        ascending=False
    )

    return result[
        [
            'original_title',
            'release_year',
            'popularity'
        ]
    ].head(10)

# =====================================
# TITLE
# =====================================

st.title("🎬 Movie Recommendation System")

# =====================================
# RECOMMENDER SECTION
# =====================================

st.header("Recommend Similar Movies")

selected_movie = st.selectbox(
    "Select a movie",
    movies['original_title'].values
)

if st.button("Recommend"):

    names, posters, years, ratings = recommend(
        selected_movie
    )

    cols = st.columns(5)

    for i in range(5):

        with cols[i]:

            st.image(posters[i])

            st.write(f"**{names[i]}**")

            st.caption(f"Year: {years[i]}")

            st.caption(f"IMDb: ⭐ {ratings[i]}")

# =====================================
# SEARCH SECTION
# =====================================

# =====================================
# SEARCH SECTION
# =====================================

st.divider()

st.header("Search Movies By Genre & Year")

genre = st.text_input(
    "Genre (Action, Comedy, Drama...)"
)

year = st.number_input(
    "Year",
    min_value=1900,
    max_value=2025,
    value=2005
)

if st.button("Search Movies"):

    result = search_movies(
        year,
        genre
    )

    if len(result) > 0:

        st.subheader(
            f"Top {genre.title()} Movies of {year}"
        )

        # Display movies in rows of 5
        for start in range(0, len(result), 5):

            cols = st.columns(5)

            batch = result.iloc[start:start+5]

            for col, (_, row) in zip(cols, batch.iterrows()):

                movie_name = row['original_title']

                poster, movie_year, rating = fetch_movie_details(
                    movie_name
                )

                with col:

                    if poster and poster != "N/A":

                        st.image(
                            poster,
                            use_container_width=True
                        )

                    st.markdown(
                        f"**{movie_name}**"
                    )

                    st.caption(
                        f"📅 {movie_year}"
                    )

                    st.caption(
                        f"⭐ IMDb {rating}"
                    )

    else:

        st.warning(
            "No movies found."
        )
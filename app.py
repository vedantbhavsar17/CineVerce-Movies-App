import streamlit as st
import pandas as pd
import requests
import os

st.set_page_config(page_title='CineVerse',layout='wide')

st.sidebar.title("Explore Manu")
choice = st.sidebar.selectbox("Options", ["Home", "By Genre", "Trending", "Watch Movie/Tv"])
with st.sidebar:
    st.markdown("---")
    st.subheader("👨‍💻 About Me")
    st.write(
        "Hi, I'm Vedant Bhavsar, the creator of CineVerse 🎬.\n\n"
        "Check out my projects on GitHub:\n"
        "[vedantbhavsar17](https://github.com/vedantbhavsar17)"
    )

API_KEY = st.secrets["API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"
IMG_BASE_URL = "https://image.tmdb.org/t/p/w500"
BASE_STREAM = st.secrets["MOVIE_BASE"]
genres = [{"id":28,"name":"Action"}, {"id":12,"name":"Adventure"}, {"id":16,"name":"Animation"}, {"id":35,"name":"Comedy"}, {"id":80,"name":"Crime"}, {"id":99,"name":"Documentary"}, {"id":18,"name":"Drama"}, {"id":10751,"name":"Family"}, {"id":14,"name":"Fantasy"}, {"id":36,"name":"History"}, {"id":27,"name":"Horror"}, {"id":10402,"name":"Music"}, {"id":9648,"name":"Mystery"}, {"id":10749,"name":"Romance"}, {"id":878,"name":"Science Fiction"}, {"id":10770,"name":"TV Movie"}, {"id":53,"name":"Thriller"}, {"id":10752,"name":"War"}, {"id":37,"name":"Western"}]

def tmdb_search_poster(movie_name):

    url = f"{BASE_URL}/search/movie"
    r = requests.get(url, params={"api_key": API_KEY, "query": movie_name}, timeout=10)
    if r.status_code == 200:
        results = r.json().get("results", [])
        if results:
            return results
        else:
            return None
        

def somePapularGanres():
    top4 = ['Action','Comedy','Mystery','Science Fiction']
    genre_map = {g["name"]: g["id"] for g in genres}
    genre_code = [(g, genre_map[g]) for g in top4 if g in genre_map]

    for genre_name, genre_id in genre_code:
        st.markdown(f"**:blue-background[{genre_name}]**")  # Genre name on top
        
        movies = fetch_top_by_genre(genre_id, k=5, use_rating=True, min_votes=500)

        movie_cols = st.columns(len(movies))
        for j, m in enumerate(movies):
            response = tmdb_search_poster(m['title'])
            if response:
                best = max(response, key=lambda x: x.get("popularity", 0))
                poster_path = best.get("poster_path")
                if poster_path:
                    path = IMG_BASE_URL + poster_path
                    with movie_cols[j]:
                        st.markdown(
                            f"""
                                <img src="{path}" style="width:180px; height:300px; object-fit:cover; border-radius:8px;">
                                <div style="max-width:120px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; "margin-top:10px;">
                                    <small>{m['title']}</small>
                                </div>                            """,
                            unsafe_allow_html=True
                        )

def fetch_top_tranding(n=50):
    movies = []
    page = 1
    per_page = 20
    while len(movies) < n:
        resp = requests.get(f"{BASE_URL}/discover/movie", params={
            "api_key": str(f"{os.getenv('API_KEY')}"),
            "language": "en-US",
            "sort_by": "popularity.desc",
            "page": page,
        })
        resp.raise_for_status()
        data = resp.json()
        movies.extend(data.get("results", []))
        if page >= data.get("total_pages", 1):
            break
        page += 1
    return movies[:n]

def homepage():
    st.title("CineVerse")
    with st.container(gap='medium'): 
        st.caption('Discover, Search & Enjoy Movies with CineVerse')
        st.subheader('Your ultimate movie recommendation hub. Search by title, explore genres, and never miss upcoming releases.')
        with st.container():
            st.text('Search Movie')
            movie = st.text_input("Search Movie",label_visibility="collapsed")
            search_btn = st.button("Search")

            if movie and search_btn:
                response = tmdb_search_poster(movie)
                if response:
                    best = max(response, key=lambda x: x.get("popularity", 0))
                    poster_path = best.get("poster_path")
                    if poster_path:
                        path = IMG_BASE_URL + poster_path
                        st.image(path, width=250)

                        if response[0]['title']:
                            st.header(response[0]['title'])
                        else:
                            st.header(movie)

                        if pd.to_datetime(response[0]['release_date']).normalize() > (pd.Timestamp.now()).normalize():
                            st.markdown(f":blue-background[Releasing Date] : {response[0]['release_date']}")
                        else:
                            st.markdown(f":blue-background[Release Date] : {response[0]['release_date']}")

                        if response[0]['overview']:
                            st.markdown(f"**:green[Overview]** : {response[0]['overview']}")
                        else:
                            st.markdown("**Overview:** _Not available_")
                        
                        if response[0]['genre_ids']:
                            genre_map = {g["id"]: g["name"] for g in genres}
                            genre_names = [genre_map[g] for g in response[0]['genre_ids'] if g in genre_map]
                            genre_string = ", ".join(genre_names)
                            st.markdown(f"**:violet[Gener(s)]** {genre_string}")
                        else:
                            st.markdown("**Genre(s):** Not available")

                        if response[0]['popularity'] is not None:
                            if pd.to_datetime(response[0]['release_date']).normalize() > (pd.Timestamp.now()).normalize():
                                st.markdown(f"**:orange[Popularity] :** {'Not Released Yet'}")
                            else:
                                try:
                                    pop_val = float(response[0]['popularity'])
                                    if pop_val <= 20:
                                        review = "Ok ok"
                                    elif pop_val <= 45:
                                        review = "Good to go"
                                    elif pop_val <= 70:
                                        review = "Watch it!!!"
                                    else:
                                        review = "Excellent!!!"
                                    st.markdown(f"**:orange[Popularity] :** {pop_val} — **{review}**")
                                except Exception:
                                    st.markdown(f"**:orange[Popularity] :** {response[0]['popularity']}")
                        else:
                            st.markdown("**Popularity:** _Not available_")

                        if response[0]['original_language']:
                            st.markdown(f"**:gray[Language] :** {response[0]['original_language']}")
                        else:
                            st.markdown("**Language:** _Not available_")
                else:
                    st.error(f"❌ {movie} not found")

def fetch_top_by_genre(genre_id, k=20, use_rating=False, min_votes=1000):
    movies = []
    page = 1
    sort_by = "vote_average.desc" if use_rating else "popularity.desc"
    while len(movies) < k:
        params = {
            "api_key": API_KEY,
            "language": "en-US",
            "with_genres": genre_id,
            "sort_by": sort_by,
            "page": page,
        }
        # apply min votes when sorting by rating to avoid obscure films
        if use_rating:
            params["vote_count.gte"] = min_votes
        resp = requests.get(f"{BASE_URL}/discover/movie", params=params)
        resp.raise_for_status()
        data = resp.json()
        movies.extend(data.get("results", []))
        if page >= data.get("total_pages", 1):
            break
        page += 1
    return movies[:k]

def Bygenre():
    st.title("CineVerse")
    genre = st.selectbox(
        "Select Genre",( "Some Papular Ganres",
        "Action", "Adventure", "Animation", "Comedy", "Crime",
        "Drama", "Family", "Fantasy", "History", "Horror", "Music", "Mystery",
        "Romance", "Science Fiction", "TV Movie", "Thriller", "War", "Western"
    ))

    if genre == "Some Papular Ganres":
        somePapularGanres()

    else:
        genre_map = {g["name"]: g["id"] for g in genres}
        genre_code = genre_map[genre]
        movies = fetch_top_by_genre(genre_code, k=10, use_rating=True, min_votes=500)

        cols = st.columns(5)
        for i, movie in enumerate(movies):
            with cols[i % 5]:
                poster_url = IMG_BASE_URL + movie['poster_path']
                if poster_url:
                    st.image(poster_url, caption=movie['title'], width=180)
                else:
                    st.text(f"{movie} (No Poster)")

def topmovies():
    url = f"{BASE_URL}/movie/popular"
    page = 1
    r = requests.get(url, params={
            "api_key": API_KEY,
            "language": "en-US",
            "page": page,
    }, timeout=10)
    if r.status_code == 200:
        results = r.json().get("results", [])
        if results:
            return results
        else:
            return None


def trending_movies():
    st.title("CineVerse")
    st.markdown(":red[Top Trending Movies] :fire:")
    responce = topmovies()
    if responce:
        cols = st.columns(5)
        for i,info in enumerate(responce):
            with cols[i % 5]:
                poster_url = IMG_BASE_URL + info['poster_path']
                if poster_url:
                    st.markdown(f"""
                                <img src="{poster_url}" style="width:180px; border-radius:8px; margin-top:20px">
                                <div style="max-width:165px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; "margin-top:20px;">
                                    <small>{info['title']}</small>
                                </div>                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.text(f"{info['title']} (No Poster)")   

def watch_now():
    st.title("CineVerse")
    st.markdown(":red[Search Your Fav] :fire:")

    if "watch_data" not in st.session_state:
        st.session_state.watch_data = None
    if "play_now" not in st.session_state:
        st.session_state.play_now = False

    search_query = st.text_input("Search Movie or TV Series", label_visibility="collapsed")
    search_btn = st.button("Search")

    if search_query and search_btn:
        url = f"{BASE_URL}/search/multi"
        r = requests.get(
            url,
            params={
                "api_key": API_KEY,
                "query": search_query
            },
            timeout=10
        )

        if r.status_code == 200:
            results = r.json().get("results", [])
            results = [x for x in results if x.get("media_type") in ["movie", "tv"]]

            if results:
                best = max(results, key=lambda x: x.get("popularity", 0))
                st.session_state.watch_data = best
                st.session_state.play_now = False
            else:
                st.error("Not Found")

    if st.session_state.watch_data:
        data = st.session_state.watch_data
        media_type = data.get("media_type")
        tmdb_id = data.get("id")
        poster_path = data.get("poster_path")

        col1, col2 = st.columns([1, 2])

        with col1:
            if poster_path:
                st.image(IMG_BASE_URL + poster_path, width=250)

        with col2:

            if media_type == "movie":
                st.header(data.get("title", "Unknown Title"))
                st.markdown("**Type:** Movie")

                if data.get("release_date"):
                    st.markdown(f"**Release Date:** {data.get('release_date')}")

                if data.get("overview"):
                    st.markdown(f"**Overview:** {data.get('overview')}")

                if st.button("▶ Watch Now"):
                    st.session_state.play_now = True

                if st.session_state.play_now:
                    embed_url = f"{BASE_STREAM}/movie/{tmdb_id}?autoPlay=true"

                    st.markdown(
                        f"""
                        <div style="display:flex; justify-content:center; margin-top:30px;">
                            <div style="
                                width:100%;
                                max-width:1000px;
                                aspect-ratio:16/9;
                                border-radius:12px;
                                overflow:hidden;
                                box-shadow:0 10px 30px rgba(0,0,0,0.6);
                            ">
                                <iframe 
                                    src="{embed_url}" 
                                    width="100%" 
                                    height="100%" 
                                    frameborder="0"
                                    allowfullscreen
                                    sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
                                    style="border:none;"
                                ></iframe>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            elif media_type == "tv":
                st.header(data.get("name", "Unknown Series"))

                if data.get("first_air_date"):
                    st.markdown(f"**First Air Date:** {data.get('first_air_date')}")

                if data.get("overview"):
                    st.markdown(f"**Overview:** {data.get('overview')}")

                tv_details = requests.get(
                    f"{BASE_URL}/tv/{tmdb_id}",
                    params={"api_key": API_KEY},
                    timeout=10
                )

                if tv_details.status_code == 200:
                    tv_data = tv_details.json()
                    total_seasons = tv_data.get("number_of_seasons", 1)
                else:
                    total_seasons = 1

                season = st.number_input(
                    "Season",
                    min_value=1,
                    max_value=total_seasons,
                    step=1,
                    value=1
                )

                season_details = requests.get(
                    f"{BASE_URL}/tv/{tmdb_id}/season/{season}",
                    params={"api_key": API_KEY},
                    timeout=10
                )

                episode = st.number_input(
                    "Episode",
                    min_value=1,
                    step=1,
                    value=1
                )

                if st.button("▶ Watch Episode"):
                    st.session_state.play_now = True

                if st.session_state.play_now:
                    embed_url = f"{BASE_STREAM}/tv/{tmdb_id}/{season}/{episode}?autoPlay=true&nextEpisode=true&episodeSelector=true"

                    st.markdown(
                        f"""
                        <div style="display:flex; justify-content:center; margin-top:30px;">
                            <div style="
                                width:100%;
                                max-width:1000px;
                                aspect-ratio:16/9;
                                border-radius:12px;
                                overflow:hidden;
                                box-shadow:0 10px 30px rgba(0,0,0,0.6);
                            ">
                                <iframe 
                                    src="{embed_url}" 
                                    width="100%" 
                                    height="100%" 
                                    frameborder="0"
                                    allowfullscreen
                                    sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
                                    style="border:none;"
                                ></iframe>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

if choice == "Home":
    try:
        homepage()
    except Exception as e:
        st.error(f"Network Slow Please Check Your Internet Connection")
elif choice == "By Genre":
    try:
        Bygenre()
    except Exception as e:
        st.error(f"Network Slow Please Check Your Internet Connection")
elif choice == "Trending":
    try:
        trending_movies()
    except Exception as e:
        st.error(f"Network Slow Please Check Your Internet Connection")
elif choice == "Watch Movie/Tv":
    try:
        watch_now()
    except Exception as e:
        st.error(f"Network Slow Please Check Your Internet Connection")

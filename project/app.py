import streamlit as st
import pickle
import requests
import time
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", message="missing ScriptRunContext")

# Load the movies and similarity data
movies = pickle.load(open("movies_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# Extract the movie titles
movie_list = movies['title'].values

# Set the page configuration
st.set_page_config(page_title="OnlyScreen", layout="wide")

# Custom CSS for styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@700&display=swap');
    body {
        background-color: #e0f7fa;
        color: #333;
        font-family: 'Roboto', sans-serif;
    }
    .centered-title {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 10vh;
        font-size: 4em;
        font-weight: bold;
        color: #333;
        margin: 0;
        padding: 20px;
    }
    .sidebar .sidebar-content {
        background-color: #ffffff;
        padding: 20px;
    }
    .main-content {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .carousel-item {
    margin: 10px;
    border-radius: 15px; /* Simple curve for borders */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    text-align: center;
    width: 50%;
    border: 2px solid #00796b; /* Thin border with a specific color */
    padding: 10px;
    background-color: #f9f9f9; /* Light background for a clean look */
    }

    .carousel-item img {
    border-radius: 15px; /* Match the border curvature */
    width: 100%;
    height: auto; /* Preserve the image's aspect ratio */
    }

    .carousel-item p {
    margin-top: 15px;
    font-size: 1.2em;
    font-weight: bold;
    color: #00796b; /* Stylish color for the title */
    background-color: #e0f7fa; /* Light contrasting background */
    padding: 10px;
    border-radius: 10px; /* Rounded corners for title background */
    font-family: 'Roboto', sans-serif; /* Stylish and modern font */
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Subtle shadow to elevate the text */
    text-transform: uppercase; /* Makes the title uppercase for a bold look */
    letter-spacing: 1px; /* Adds spacing between characters for elegance */
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Define fetch_poster function
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=395138abae1aa6b0739ec5505cd06128"
    retries = 3
    for _ in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()
            poster_path = data['poster_path']
            full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
            return full_path
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}. Retrying in 5 seconds...")
            time.sleep(5)
    st.error("Failed to fetch poster after multiple attempts.")
    return None


# Centered title
st.markdown('<div class="centered-title">OnlyScreen</div>', unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Recommendations", "About"])

if page == "Home":
    st.header("Welcome to OnlyScreen")
    st.write("Your Ultimate Guide to Must-Watch Movies")

    # Movie Carousels
    st.markdown('<div class="carousel">', unsafe_allow_html=True)
    for i, movie in enumerate(movie_list):  # Display all movies in the carousel
        movie_id = movies[movies['title'] == movie].iloc[0].id
        poster_url = fetch_poster(movie_id)
        if poster_url:
            st.markdown(f'''
                <div class="carousel-item">
                    <img src="{poster_url}" alt="{movie}">
                    <p>{movie}</p>
                </div>
            ''', unsafe_allow_html=True)
        if (i + 1) % 3 == 0:
            st.markdown('</div><div class="carousel">', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Recommendations":
    st.header("Movie Recommendations")
    st.write("Get personalized movie recommendations based on your preferences.")

    # Dropdown for selecting a movie
    selectvalue = st.selectbox("Select movie from dropdown", movie_list)


    # Recommend function
    def recommend(selectvalue):
        try:
            # Find the index of the selected movie
            index = movies[movies['title'] == selectvalue].index[0]
            # Calculate the similarity distances
            distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
            recommend_movie = []
            recommend_poster = []
            # Get the top 5 recommended movies
            for i in distance[1:6]:
                movie_id = movies.iloc[i[0]].id
                recommend_movie.append(movies.iloc[i[0]].title)
                poster = fetch_poster(movie_id)
                if poster:
                    recommend_poster.append(poster)
                else:
                    recommend_poster.append("https://via.placeholder.com/500")  # Placeholder image if fetch fails
            return recommend_movie, recommend_poster
        except IndexError:
            st.error("Movie not found in the dataset.")
            return [], []


    # Show recommendations when the button is clicked
    if st.button("Show Recommendations"):
        movie_name, movie_poster = recommend(selectvalue)
        if movie_name:
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.text(movie_name[0])
                st.image(movie_poster[0])
            with col2:
                st.text(movie_name[1])
                st.image(movie_poster[1])
            with col3:
                st.text(movie_name[2])
                st.image(movie_poster[2])
            with col4:
                st.text(movie_name[3])
                st.image(movie_poster[3])
            with col5:
                st.text(movie_name[4])
                st.image(movie_poster[4])

elif page == "About":
    st.header("About OnlyScreen")
    st.write("""
    OnlyScreen is a movie recommendation system that helps you discover the best movies tailored to your taste. 
    Our advanced algorithms analyze your preferences and provide personalized recommendations to enhance your movie-watching experience.

    **Features:**
    - Personalized movie recommendations based on your preferences.
    - Easy-to-use interface with a clean and modern design.
    - Access to movie posters and detailed information about each movie.
    - Regular updates to ensure you always have the latest recommendations.

    **How It Works:**
    1. Select a movie from the dropdown list.
    2. Click on the "Show Recommendations" button.
    3. Get a list of recommended movies along with their posters.

    **Contact Us:**
    If you have any questions or feedback, feel free to reach out to us at support@onlyscreen.com.
    """)

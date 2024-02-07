from flask import (
    Blueprint, render_template, request
)

from .tools.data_tool import *

from surprise import Reader
from surprise import KNNBasic
from surprise import Dataset

bp = Blueprint('main', __name__, url_prefix='/')

movies, genres, rates, users = loadData()


@bp.route('/', methods=('GET', 'POST'))
def index():

    # Default Genres List
    default_genres = genres.to_dict('records')

    # User Genres
    user_genres = request.cookies.get('user_genres')
    if user_genres:
        user_genres = user_genres.split(",")
    else:
        user_genres = []

    # User Rates
    user_rates = request.cookies.get('user_rates')
    if user_rates:
        user_rates = user_rates.split(",")
    else:
        user_rates = []

    # User Likes
    user_likes = request.cookies.get('user_likes')
    if user_likes:
        user_likes = user_likes.split(",")
    else:
        user_likes = []

    default_genres_movies = getMoviesByGenres(user_genres)
    recommendations_movies, recommendations_message = getRecommendationBy(user_rates)
    likes_similar_movies, likes_similar_message = getLikedSimilarBy(user_likes)
    likes_movies = getUserLikesBy(user_likes)

    return render_template('index.html',
                           genres=default_genres,
                           user_genres=user_genres,
                           user_rates=user_rates,
                           user_likes=user_likes,
                           default_genres_movies=default_genres_movies,
                           recommendations=recommendations_movies,
                           recommendations_message=recommendations_message,
                           likes_similars=likes_similar_movies,
                           likes_similar_message=likes_similar_message,
                           likes=likes_movies,
                           )


def getUserLikesBy(user_likes):
    results = []

    if len(user_likes) > 0:
        mask = movies['movie_id'].isin([int(movie_id) for movie_id in user_likes])
        results = movies.loc[mask]

        original_orders = pd.DataFrame()
        for _id in user_likes:
            original_orders = pd.concat([results.loc[[int(_id) - 1]], original_orders])
        results = original_orders

    # return the result
    if len(results) > 0:
        return results.to_dict('records')
    return results


def getMoviesByGenres(user_genres):
    results = []

    # ====  Do some operations ====

    if len(user_genres) > 0:
        genres_mask = genres['id'].isin([int(id) for id in user_genres])
        user_genres = [1 if has is True else 0 for has in genres_mask]
        user_genres_df = pd.DataFrame(user_genres)
        user_genres_df.index = genres['name']
        movies_genres = movies.iloc[:, 5:]
        mask = (movies_genres.dot(user_genres_df) > 0).squeeze()
        results = movies.loc[mask][:30]

    # ==== End ====

    # return the result
    if len(results) > 0:
        return results.to_dict('records')
    return results


# Modify this function
def getRecommendationBy(user_rates):
    results = []

    # ==== Do some operations ====

    # Check if there are any user_rates
    if len(user_rates) > 0:
        # Initialize a reader with rating scale from 1 to 5
        reader = Reader(rating_scale=(1, 5))

        algo = KNNBasic(sim_options={'name': 'pearson', 'user_based': True})

        # Convert user_rates to rates from the user
        user_rates = ratesFromUser(user_rates)

        # Combine rates and user_rates into training_rates
        training_rates = pd.concat([rates, user_rates], ignore_index=True)

        # Load the training data from the training_rates DataFrame
        training_data = Dataset.load_from_df(training_rates, reader=reader)

        # Build a full training set from the training data
        trainset = training_data.build_full_trainset()

        # Fit the algorithm using the trainset
        algo.fit(trainset)

        # Convert the raw user id to the inner user id using algo.trainset
        inner_id = trainset.to_inner_uid(944)

        # Get the nearest neighbors of the inner_id
        neighbors = algo.get_neighbors(inner_id, k=1)

        # Convert the inner user ids of the neighbors back to raw user ids
        neighbors_uid = [algo.trainset.to_raw_uid(x) for x in neighbors]

        # Filter out the movies this neighbor likes.
        results_movies = rates[rates['userId'].isin(neighbors_uid)]
        moviesIds = results_movies[results_movies['rating'] > 2.5]['movieId']

        # Convert the movie ids to details.
        results = movies[movies['movie_id'].isin(moviesIds)][:12]

    # Return the result
    if len(results) > 0:
        return results.to_dict('records'), "These movies are recommended based on your ratings."
    return results, "No recommendations."
    # ==== End ====


# Modify this function
def getLikedSimilarBy(user_likes):
    results = []

    # ==== Do some operations ====
    if len(user_likes) > 0:
        results = movies[:12]

    # Return the result
    if len(results) > 0:
        return results.to_dict('records'), "The movies are similar to your liked movies."
    return results, "No similar movies found."

    # ==== End ====

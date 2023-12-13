from flask import (
    Blueprint, render_template, request
)
import pandas as pd
from .tools.data_tool import *

from surprise import Reader
from surprise import KNNBasic
from surprise import Dataset

bp = Blueprint('main', __name__, url_prefix='/')

movies, genres, rates, users = loadData()

algo = KNNBasic(sim_options={'name': 'pearson', 'user_based': False})


@bp.route('/', methods=('GET', 'POST'))
def index():
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
    recommendations_movies = getRecommendationBy(user_rates)
    likes_similar_movies = getLikedSimilarBy(user_likes)
    likes_movies = getUserLikesBy(user_likes)

    return render_template('index.html',
                           genres=genres.to_dict('records'),
                           user_genres=user_genres,
                           user_rates=user_rates,
                           user_likes=user_likes,
                           default_genres_movies=default_genres_movies,
                           recommendations=recommendations_movies,
                           likes_similars=likes_similar_movies,
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

    # Convert user_rates to rates from the user
    user_rates = ratesFromUser(user_rates)

    # Combine rates and user_rates into training_rates
    training_rates = pd.concat([rates, user_rates])

    # Check if there are any user_rates
    if len(user_rates) > 0:
        # Initialize a reader with rating scale from 1 to 5
        reader = Reader(rating_scale=(1, 5))

        # Load the training data from the training_rates DataFrame
        training_data = Dataset.load_from_df(training_rates, reader=reader)

        # Build a full training set from the training data
        trainset = training_data.build_full_trainset()

        # Fit the algorithm using the trainset
        algo.fit(trainset)

        # Generate predictions using the testset from the trainset (limited to the first 100)
        predictions = algo.test(trainset.build_testset()[:100])

        # Sort the predictions based on the 'est' values in descending order
        sorted_predictions = sorted(predictions, key=lambda x: x.est, reverse=True)

        # Specify the number of top-K predictions to retrieve
        top_K = 12

        # Extract the 'iid' values of the top-K predictions
        top_K_iids = [p.iid for p in sorted_predictions[:top_K]]

        # Filter the movies DataFrame based on the top-K iids
        results = movies[movies['movie_id'].isin(top_K_iids)]

    # ==== End ====

    # Return the result
    if len(results) > 0:
        return results.to_dict('records')
    return results

# Modify this function
def getLikedSimilarBy(user_likes):
    results = []

    # ==== Do some operations ====

    # Check if there are any user_likes
    if len(user_likes) > 0:
        # Get the last item from the user_likes list and convert it to an integer
        user_like_last = int(user_likes[-1])

        # Convert the raw item id to the inner item id using algo.trainset
        inner_id = algo.trainset.to_inner_iid(user_like_last)

        # Get the k nearest neighbors of the inner_id
        neighbors = algo.get_neighbors(inner_id, k=12)

        # Convert the inner item ids of the neighbors back to raw item ids
        neighbors_iid = [algo.trainset.to_raw_iid(x) for x in neighbors]

        # Filter the movies DataFrame based on the neighbors' item ids
        results = movies[movies['movie_id'].isin(neighbors_iid)]

    # ==== End ====

    # Return the result
    if len(results) > 0:
        return results.to_dict('records')
    return results
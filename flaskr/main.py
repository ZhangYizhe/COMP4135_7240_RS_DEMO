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

    # Default Genres List
    default_genres = genres.to_dict('records')[:2]

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

    default_genres_movies = getMoviesByGenres(user_genres)[:1]
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

    results = movies[:12]

    # Return the result
    if len(results) > 0:
        return results.to_dict('records'), "These movies are recommended based on your interested genres."
    return results, "No recommendations."
    # ==== End ====


# Modify this function
def getLikedSimilarBy(user_likes):
    results = []

    # ==== Do some operations ====

    # Check if there are any user_likes
    if hasattr(algo, 'trainset') and len(user_likes) > 0:
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

    # Return the result
    if len(results) > 0:
        return results.to_dict('records'), "The movies are similar to your liked movies."
    return results, "No similar movies found."

    # ==== End ====

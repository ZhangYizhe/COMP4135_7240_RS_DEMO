from flask import (
    Blueprint, render_template, request
)
import pandas as pd

from .tools.data_tool import *

bp = Blueprint('main', __name__, url_prefix='/')

movies, genres, rates, users = loadData()


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


def getRecommendationBy(user_rates):
    results = []

    # ====  Do some operations ====

    if len(user_rates) > 0:
        results = movies[20:30]

    # ==== End ====


    # return the result
    if len(results) > 0:
        return results.to_dict('records')
    return results


def getUserLikesBy(user_likes):
    results = []

    # ====  Do some operations ====

    if len(user_likes) > 0:
        mask = movies['movie_id'].isin([int(movie_id) for movie_id in user_likes])
        results = movies.loc[mask]

    # ==== End ====

    # return the result
    if len(results) > 0:
        return results.to_dict('records')
    return results


def getLikedSimilarBy(user_likes):
    results = []

    # ====  Do some operations ====

    if len(user_likes) > 0:
        results = movies[40:50]

    # ==== End ====


    # return the result
    if len(results) > 0:
        return results.to_dict('records')
    return results


import os
import pandas as pd
from flask import current_app


def loadData():
    return getMovies(), getGenre(), getRates(), getUsers()


# movie id | movie title | release date | video release date |
#               Cover URL | unknown | Action | Adventure | Animation |
#               Children's | Comedy | Crime | Documentary | Drama | Fantasy |
#               Film-Noir | Horror | Musical | Mystery | Romance | Sci-Fi |
#               Thriller | War | Western |
def getMovies():
    rootPath = os.path.abspath(os.getcwd())
    path = f"{rootPath}/flaskr/static/ml-100k/u.item"
    df = pd.read_csv(path, delimiter="|", names=["movie_id", "movie_title", "release_date", "video_release_date",
                                                 "cover_url", "unknown", "Action", "Adventure", "Animation",
                                                 "Children's", "Comedy", "Crime", "Documentary", "Drama", "Fantasy",
                                                 "Film-Noir", "Horror", "Musical", "Mystery", "Romance", "Sci-Fi",
                                                 "Thriller", "War", "Western"])
    df.set_index('movie_id')
    return df


# A list of the genres.
def getGenre():
    rootPath = os.path.abspath(os.getcwd())
    path = f"{rootPath}/flaskr/static/ml-100k/u.genre"
    df = pd.read_csv(path, delimiter="|", names=["name", "id"])
    df.set_index('id')
    return df


# user id | item id | rating | timestamp
def getRates():
    rootPath = os.path.abspath(os.getcwd())
    path = f"{rootPath}/flaskr/static/ml-100k/u.data"
    df = pd.read_csv(path, delimiter="\t", names=["user_id", "movie_id", "rating", "timestamp"])

    df = df.drop(columns='timestamp')
    df = df.rename(columns={'movie_id': 'itemID', 'user_id': 'userID'})
    df = df[['itemID', 'userID', 'rating']]

    return df


# itemID | userID | rating
def ratesFromUser(rates):
    itemID = []
    userID = []
    rating = []

    for rate in rates:
        items = rate.split("|")
        userID.append(items[0])
        itemID.append(items[1])
        rating.append(items[2])

    ratings_dict = {
        "itemID": itemID,
        "userID": userID,
        "rating": rating,
    }

    return pd.DataFrame(ratings_dict)


# user id | age | gender | occupation | zip code
def getUsers():
    rootPath = os.path.abspath(os.getcwd())
    path = f"{rootPath}/flaskr/static/ml-100k/u.user"
    df = pd.read_csv(path, delimiter="|", names=["user_id", "age", "gender", "occupation", "zip_code"])
    df.set_index('user_id')
    return df
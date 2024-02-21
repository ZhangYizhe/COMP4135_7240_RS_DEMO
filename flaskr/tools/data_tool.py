import os
import pandas as pd


def loadData():
    return getMovies(), getGenre(), getRates()


# movieId,title,year,overview,cover_url,genres
def getMovies():
    rootPath = os.path.abspath(os.getcwd())
    path = f"{rootPath}/flaskr/static/ml_data_lab2/movie_info.csv"
    # df = pd.read_csv(path, delimiter=",", names=["movieId", "title", "year", "overview", "cover_url", "genres"])
    df = pd.read_csv(path, delimiter="|")
    df.set_index('movieId')

    return df


# A list of the genres.
def getGenre():
    rootPath = os.path.abspath(os.getcwd())
    path = f"{rootPath}/flaskr/static/ml_data_lab2/genre.csv"
    df = pd.read_csv(path, delimiter="|", names=["name", "id"])
    df.set_index('id')
    return df


# user id | item id | rating | timestamp
def getRates():
    rootPath = os.path.abspath(os.getcwd())
    path = f"{rootPath}/flaskr/static/ml_data_lab2/ratings.csv"
    df = pd.read_csv(path, delimiter=",", names=["userId", "movieId", "rating", "timestamp"])
    df = df.drop(columns='timestamp')
    df = df[['userId', 'movieId', 'rating']]

    return df


# itemID | userID | rating
def ratesFromUser(rates):
    itemID = []
    userID = []
    rating = []

    for rate in rates:
        items = rate.split("|")
        userID.append(int(items[0]))
        itemID.append(int(items[1]))
        rating.append(int(items[2]))

    ratings_dict = {
        "userId": userID,
        "movieId": itemID,
        "rating": rating,
    }

    return pd.DataFrame(ratings_dict)
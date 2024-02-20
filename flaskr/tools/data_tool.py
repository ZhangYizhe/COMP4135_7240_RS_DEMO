import os
import pandas as pd


def loadData():
    return getMovies(), getGenre(), getRates(), getUsers()


def changeData():
    rootPath = os.path.abspath(os.getcwd())
    path = f"{rootPath}/flaskr/static/ml_data_lab2/movie_info_new.csv"

    file1 = open(path, 'r')
    lines = file1.readlines()

    final_lines = [lines[0]]

    array = []
    for line in lines[1:]:
        array += line.split(",")

        if "https" not in array[-2]:
            continue

        array_len = len(array)

        sub = ','.join(array[3:(array_len - 2)]).replace('"', "").replace("\n", "")

        new_line = ','.join(array[:3]) + ',"' + sub + '",' + ','.join(array[-2:])
        final_lines.append(new_line)

        array = []

    for line in final_lines:
        file = open(f"{rootPath}/flaskr/static/ml_data_lab2/movie_info_new_2.csv", "a")
        file.write(line)
        file.close()


# movieId,title,year,overview,cover_url,genres
def getMovies():
    rootPath = os.path.abspath(os.getcwd())
    path = f"{rootPath}/flaskr/static/ml_data_lab2/movie_info_new_2.csv"
    print(path)
    # df = pd.read_csv(path, delimiter=",", names=["movieId", "title", "year", "overview", "cover_url", "genres"])
    df = pd.read_csv(path)
    df.set_index('movieId')

    df['genres'] = df.genres.str.split('|')

    print(df.head())

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
    df = df.rename(columns={'movie_id': 'movieId', 'user_id': 'userId'})
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


# user id | age | gender | occupation | zip code
def getUsers():
    rootPath = os.path.abspath(os.getcwd())
    path = f"{rootPath}/flaskr/static/ml-100k/u.user"
    df = pd.read_csv(path, delimiter="|", names=["user_id", "age", "gender", "occupation", "zip_code"])
    df.set_index('user_id')
    return df
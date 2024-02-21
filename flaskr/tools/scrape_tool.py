import csv
import os
import urllib.request as urllib2

from flask import current_app
from pyquery import PyQuery as pq
import urllib.parse as urlParse
import re
import pandas as pd

def scrape_api(url):
    try:
        urllib2.urlcleanup()
        req = urllib2.Request(url)
        req.add_header('Cache-Control', 'max-age=0')
        req.add_header('User-Agent',
                       'Mozilla/5.0')
        req.add_header('Connection', 'close')
        response = urllib2.urlopen(req)
        data = response.read().decode("utf-8")
        return data
    except urllib2.HTTPError:
        return None


def get_movie_png(movie_name):
    search_url = f"https://www.imdb.com/find/?q={urlParse.quote(movie_name)}&exact=true"
    response = scrape_api(search_url)
    if response is None:
        return None

    doc = pq(response)
    href = doc('.ipc-image').attr('src')

    try:
        href = re.sub(r"_.*", "_UX512.jpg", href)
    except:
        return None

    return href


# movie id | movie title | release date | video release date |
#               IMDb URL | unknown | Action | Adventure | Animation |
#               Children's | Comedy | Crime | Documentary | Drama | Fantasy |
#               Film-Noir | Horror | Musical | Mystery | Romance | Sci-Fi |
#               Thriller | War | Western |
def getOriginalItems():
    file = open(f"{current_app.root_path}/static/ml_data_lab2/movie_info.csv", encoding="ISO-8859-1")
    data = list(csv.reader(file, delimiter=","))
    file.close()
    return data


def covertMovieDataWithOverview():
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

    rootPath = os.path.abspath(os.getcwd())
    path = f"{rootPath}/flaskr/static/ml_data_lab2/movie_info_new_3.csv"
    # df = pd.read_csv(path, delimiter=",", names=["movieId", "title", "year", "overview", "cover_url", "genres"])
    df = pd.read_csv(path)
    df.set_index('movieId')

    df['genres'] = df.genres.str.split('|')

    genre_list = []  # store the occurred genres

    for index, row in df.iterrows():
        for genre in row['genres']:
            df.at[index, genre] = 1
            if genre not in genre_list:
                genre_list.append(genre)

    df = df.fillna(0)

    lines = ["movieId" + "|title" + "|year" + "|overview" + "|cover_url" + "|genres" + '|'.join(genre_list) + '\n']

    for index, row in df.iterrows():
        line = str(row['movieId']) + '|' + str(row['title']) + '|' + str(row['year']) + '|"' + str(
            row['overview']) + '"|' + str(row['cover_url']) + '|' + '|'.join(
            str(int(x)) for x in list(row.iloc[6:])) + '\n'
        lines.append(line)

    for line in lines:
        file = open(f"{rootPath}/flaskr/static/ml_data_lab2/movie_info_new_3.csv", "a")
        file.write(line)
        file.close()
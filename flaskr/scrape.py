from .tools.scrape_tool import *

from flask import (
    Blueprint, current_app
)

bp = Blueprint('scrape', __name__, url_prefix='/scrape')


# This function aims to re-scrape the cover of the movies. Do not run it without supervisor!!.
@bp.route('/', methods=('GET', 'POST'))
def index():
    movies = getOriginalItems()

    totalNum = len(movies)
    current = 0

    file = open(f"{current_app.root_path}/static/ml_data_lab2/movie_info_new.csv", "a")
    titles = movies[0]
    genres = titles.pop(2)
    titles.append("cover_url")
    titles.append(genres)
    file.write(','.join(titles) + "\n")
    file.close()

    for movie in movies[1:]:
        print(f"{(current / totalNum) * 100 : .2f} %")
        image_url = get_movie_png(movie[1])
        print(image_url)
        genres = movie.pop(2)
        if image_url is not None:
            movie.append(image_url)
        else:
            movie.append("")
        movie.append(genres)
        file = open(f"{current_app.root_path}/static/ml_data_lab2/movie_info_new.csv", "a")
        file.write(','.join(movie) + "\n")
        file.close()
        current += 1

    file.close()

    return "Complete!"




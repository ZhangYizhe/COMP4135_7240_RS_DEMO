from .tools.scrape_tool import *

from flask import (
    Blueprint, current_app
)

bp = Blueprint('scrape', __name__, url_prefix='/scrape')


# This function aims to re-scrape the cover of the movies. Do not run it without supervisor!!.
@bp.route('/', methods=('GET', 'POST'))
def index():
    movies = getOriginalItems()

    file = open(f"{current_app.root_path}/static/ml-100k/u.item", "w").close()

    totalNum = len(movies)
    current = 0

    for movie in movies:
        print(f"{(current / totalNum) * 100 : .2f} %")
        image_url = get_movie_png(movie[1])
        print(image_url)
        if image_url is not None:
            movie[4] = image_url
        else:
            movie[4] = ""
        file = open(f"{current_app.root_path}/static/ml-100k/u.item", "a")
        file.write('|'.join(movie) + "\n")
        file.close()
        current += 1

    file.close()

    return "Complete!"




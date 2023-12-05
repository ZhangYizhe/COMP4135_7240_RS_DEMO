import urllib.request as urllib2
from pyquery import PyQuery as pq
import urllib.parse as urlParse
import re

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
    file = open(f"{current_app.root_path}/static/ml-100k/u.item.new", encoding="ISO-8859-1")
    data = list(csv.reader(file, delimiter="|"))
    file.close()
    return data
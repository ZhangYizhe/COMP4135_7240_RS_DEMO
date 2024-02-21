from flask import (
    Blueprint, render_template, request
)

from .tools.data_tool import *

from surprise import Reader
from surprise import KNNBasic
from surprise import Dataset
from sklearn.metrics.pairwise import cosine_similarity

bp = Blueprint('main', __name__, url_prefix='/')

movies, genres, rates = loadData()


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
    likes_similar_movies, likes_similar_message = getLikedSimilarBy([int(numeric_string) for numeric_string in user_likes])
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
        mask = movies['movieId'].isin([int(movieId) for movieId in user_likes])
        results = movies.loc[mask]

        original_orders = pd.DataFrame()
        for _id in user_likes:
            movie = results.loc[results['movieId'] == int(_id)]
            if len(original_orders) == 0:
                original_orders = movie
            else:
                original_orders = pd.concat([movie, original_orders])
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

    # Check if there are any user_rates
    if len(user_rates) > 0:
        # Initialize a reader with rating scale from 1 to 5
        reader = Reader(rating_scale=(1, 5))

        algo = KNNBasic(sim_options={'name': 'pearson', 'user_based': True})

        # Convert user_rates to rates from the user
        user_rates = ratesFromUser(user_rates)

        # Combine rates and user_rates into training_rates
        training_rates = pd.concat([rates, user_rates], ignore_index=True)

        # Load the training data from the training_rates DataFrame
        training_data = Dataset.load_from_df(training_rates, reader=reader)

        # Build a full training set from the training data
        trainset = training_data.build_full_trainset()

        # Fit the algorithm using the trainset
        algo.fit(trainset)

        # Convert the raw user id to the inner user id using algo.trainset
        inner_id = trainset.to_inner_uid(611)

        # Get the nearest neighbors of the inner_id
        neighbors = algo.get_neighbors(inner_id, k=1)

        # Convert the inner user ids of the neighbors back to raw user ids
        neighbors_uid = [algo.trainset.to_raw_uid(x) for x in neighbors]

        # Filter out the movies this neighbor likes.
        results_movies = rates[rates['userId'].isin(neighbors_uid)]
        moviesIds = results_movies[results_movies['rating'] > 2.5]['movieId']

        # Convert the movie ids to details.
        results = movies[movies['movieId'].isin(moviesIds)][:12]

    # Return the result
    if len(results) > 0:
        return results.to_dict('records'), "These movies are recommended based on your ratings."
    return results, "No recommendations."
    # ==== End ====


# Modify this function
def getLikedSimilarBy(user_likes):
    results = []

    # ==== Do some operations ====
    if len(user_likes) > 0:

        # One-hot By Genres
        # Step 1: Representing items with one-hot vectors
        item_rep_matrix, item_rep_vector, feature_list = item_representation_based_movie_genres(movies)

        # Step 2: Building user profile
        user_profile = build_user_profile(user_likes, item_rep_vector, feature_list)

        # Step 3: Predicting user interest in items
        results = generate_recommendation_results(user_profile, item_rep_matrix, item_rep_vector, 12)

        # TF-IDF By Overview
        # Step 1: Representing TF-IDF Vectors
        movie_TF_IDF_vector, tfidf_feature_list = build_tfidf_vectors()
        # Step 2: Building user profile
        ifidf_user_profile = build_tfidf_user_profile(user_likes, movie_TF_IDF_vector, tfidf_feature_list)
        # Step 3: Predicting user interest in items
        results = generate_tf_idf_recommendation_results(ifidf_user_profile, movie_TF_IDF_vector, tfidf_feature_list, 12)

    # Return the result
    if len(results) > 0:
        return results.to_dict('records'), "The movies are similar to your liked movies."
    return results, "No similar movies found."

    # ==== End ====


def item_representation_based_movie_genres(movies_df):
    movies_with_genres = movies_df.copy(deep=True)

    genre_list = movies_with_genres.columns[5:]
    movies_genre_matrix = movies_with_genres[genre_list].to_numpy()
    return movies_genre_matrix, movies_with_genres, genre_list


def build_user_profile(movieIds, item_rep_vector, feature_list, normalized=True):

    ## Calculate item representation matrix to represent user profiles
    user_movie_rating_df = item_rep_vector[item_rep_vector['movieId'].isin(movieIds)]
    user_movie_df = user_movie_rating_df[feature_list].mean()
    user_profile = user_movie_df.T

    if normalized:
        user_profile = user_profile / sum(user_profile.values)

    return user_profile


def generate_recommendation_results(user_profile,item_rep_matrix, movies_data, k=12):

    u_v = user_profile.values
    u_v_matrix = [u_v]

    # Comput the cosine similarity
    recommendation_table = cosine_similarity(u_v_matrix, item_rep_matrix)

    recommendation_table_df = movies_data.copy(deep=True)
    recommendation_table_df['similarity'] = recommendation_table[0]
    rec_result = recommendation_table_df.sort_values(by=['similarity'], ascending=False)[:k]

    return rec_result

# TF-IDF by Overview
import nltk
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

stopword = stopwords.words('english')

def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return ''


def preprocessing(text):
    # lower case
    text = text.lower()
    # remove punctuation
    text_rp = "".join([char for char in text if char not in string.punctuation])
    # word tokenization
    tokens = word_tokenize(text_rp)
    # remove stopwords
    tokens_without_stopwords = [word for word in tokens if word not in stopword]

    # lemm
    tagged_tokens = nltk.pos_tag(tokens_without_stopwords)
    # print(tagged_tokens)
    tokens_processed = []

    lemmatizer = WordNetLemmatizer()
    for word, tag in tagged_tokens:
        word_net_tag = get_wordnet_pos(tag)
        if word_net_tag != '':
            tokens_processed.append(lemmatizer.lemmatize(word, word_net_tag))
        else:
            tokens_processed.append(word)
    text_processed = ' '.join(tokens_processed)

    return text_processed


def build_tfidf_vectors():
    movies_vectors = movies.copy(deep=True)
    movies_vectors['overview'] = movies_vectors['overview'].fillna('')

    # Import TfIdfVectorizer from scikit-learn
    from sklearn.feature_extraction.text import TfidfVectorizer

    # Define a TF-IDF Vectorizer Object.
    tfidf = TfidfVectorizer(
        preprocessor=preprocessing,
        ngram_range=(1, 1),
        max_features=20)

    # Construct the required TF-IDF matrix by fitting and transforming the data
    tfidf_matrix = tfidf.fit_transform(movies_vectors['overview'])

    movie_TF_IDF_vector = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf.get_feature_names_out())
    movie_TF_IDF_vector['movieId'] = movies['movieId']
    return movie_TF_IDF_vector, tfidf.get_feature_names_out()[:20]


def build_tfidf_user_profile(user_likes, movie_TF_IDF_vector, tfidf_feature_list, normalized=True):
    user_movie = movie_TF_IDF_vector[movie_TF_IDF_vector['movieId'].isin(user_likes)]

    user_movie_df = user_movie[tfidf_feature_list].mean()

    user_profile = user_movie_df.T

    if normalized:
        user_profile = user_profile / sum(user_profile.values)

    return user_profile


def generate_tf_idf_recommendation_results(user_profile, movie_TF_IDF_vector, tfidf_feature_list, k=12):

    # Compute the cosine similarity
    u_v = user_profile
    u_v_matrix = [u_v]

    recommendation_table = cosine_similarity(u_v_matrix, movie_TF_IDF_vector[tfidf_feature_list])

    recommendation_table_df = movies.copy(deep=True)
    recommendation_table_df['similarity'] = recommendation_table[0]
    rec_result = recommendation_table_df.sort_values(by=['similarity'], ascending=False)[:k]

    return rec_result
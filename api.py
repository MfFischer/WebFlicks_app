from flask import Blueprint, jsonify, request, abort
from datamanager.sqlite_data_manager import SQLiteDataManager


# Create the API blueprint
api = Blueprint('api', __name__)

# Initialize the SQLiteDataManager
data_manager = SQLiteDataManager()


@api.route('/users', methods=['GET'])
def get_users():
    """
    Get a list of all users.
    """
    users = data_manager.get_all_users()
    return jsonify(users)


@api.route('/users/<int:user_id>/movies', methods=['GET'])
def get_user_movies(user_id):
    """
    Get a list of all movies for a specific user.
    """
    movies = data_manager.get_user_movies(user_id)
    return jsonify(movies)


@api.route('/users/<int:user_id>/movies', methods=['POST'])
def add_user_movie(user_id):
    """
    Add a new movie to a user's list.
    """
    if not request.json or 'movie_name' not in request.json:
        abort(400, 'Missing movie_name in request')

    movie_data = {
        'movie_name': request.json['movie_name'],
        'poster_url': request.json.get('poster_url', ''),
        'lead_actor': request.json.get('lead_actor', ''),
        'release_date': request.json.get('release_date', ''),
        'imdb_rating': request.json.get('imdb_rating', ''),
        'imdb_url': request.json.get('imdb_url', '')
    }

    data_manager.add_movie_for_user(user_id, movie_data)
    return jsonify({'message': 'Movie added successfully!'}), 201


@api.route('/movies/<int:movie_id>/reviews', methods=['GET'])
def get_reviews(movie_id):
    """
    Get all reviews for a specific movie.
    """
    reviews = data_manager.get_reviews_for_movie(movie_id)
    return jsonify([
        {
            'id': review.id,
            'user_id': review.user_id,
            'review_text': review.review_text,
            'rating': review.rating,
            'created_at': review.created_at
        } for review in reviews
    ])


@api.route('/movies/<int:movie_id>/reviews', methods=['POST'])
def add_review(movie_id):
    """
    Add a new review for a specific movie.
    """
    if not request.json or 'review_text' not in request.json:
        abort(400, 'Missing review_text in request')

    review_data = {
        'user_id': request.json['user_id'],
        'movie_id': movie_id,
        'review_text': request.json['review_text'],
        'rating': request.json['rating']
    }

    data_manager.add_review(review_data)
    return jsonify({'message': 'Review added successfully!'}), 201


@api.route('/reviews/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    """
    Update an existing review.
    """
    if not request.json or 'review_text' not in request.json or 'rating' not in request.json:
        abort(400, 'Missing data in request')

    review_text = request.json['review_text']
    rating = int(request.json['rating'])
    data_manager.update_review(review_id, review_text, rating)
    return jsonify({'message': 'Review updated successfully!'})


@api.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    """
    Delete a review by its ID.
    """
    data_manager.delete_review(review_id)
    return jsonify({'message': 'Review deleted successfully!'})

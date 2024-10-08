from flask import Flask, render_template, redirect, url_for, flash, session, request
import requests
from flask_cors import CORS
from datamanager.data_model import Review, Base
from datamanager.sqlite_data_manager import SQLiteDataManager
from datetime import datetime
from werkzeug.security import check_password_hash
from api import api

app = Flask(__name__)
# Needed for flashing messages
app.secret_key = 'your_secret_key'

# Enable CORS for the application
CORS(app)

# Initialize the SQLiteDataManager with the database path
data_manager = SQLiteDataManager()

# Create all tables in the database if they don't exist
Base.metadata.create_all(data_manager.engine)

# Register the API blueprint with a URL prefix
app.register_blueprint(api, url_prefix='/api')

# OMDb API key
OMDB_API_KEY = 'd5ee8f11'


@app.route('/')
def home():
    """Render the home page or redirect to the dashboard
    if the user is logged in."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')


@app.route('/users')
def list_users():
    """Render the page with the list of all users."""
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        user_data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'birthdate': datetime.strptime(request.form['birthdate'],
                                           '%Y-%m-%d').date(),
            'email': request.form['email'],
            'password': request.form['password']
        }
        data_manager.add_user(user_data)
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Handle adding a new user."""
    if request.method == 'POST':
        user_data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'birthdate': request.form['birthdate'],
            'email': request.form['email'],
            'password': request.form['password']
        }
        data_manager.add_user(user_data)
        flash('User added successfully!')
        return redirect(url_for('list_users'))
    return render_template('add_user.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = data_manager.get_user_by_email(email)
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['user_name'] = user.first_name
            flash(f'Welcome, {user.first_name}!')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.')
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    """Render the dashboard page."""
    if 'user_id' not in session:
        flash('Please log in.')
        return redirect(url_for('login'))
    return render_template('dashboard.html')


@app.route('/logout')
def logout():
    """Handle user logout."""
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('home'))


@app.route('/users/<int:user_id>/movies', methods=['GET', 'POST'])
def user_movies(user_id):
    """Render the page with a user's movies and handle search functionality."""
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('login'))

    search_query = request.args.get('search_query', '')
    movies = data_manager.get_user_movies(user_id)

    if search_query:
        movies = [
            movie for movie in movies
            if search_query.lower() in movie['movie_name'].lower()
        ]

    return render_template('user_movies.html',
                           user_id=user_id, movies=movies)


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """Handle adding a new movie to a user's list."""
    if request.method == 'POST':
        movie_name = request.form['movie_name']
        omdb_url = f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDB_API_KEY}"
        response = requests.get(omdb_url)
        if response.status_code == 200:
            movie_data = response.json()
            if movie_data['Response'] == 'True':
                movie_details = {
                    'movie_name': movie_data['Title'],
                    'poster_url': movie_data['Poster'],
                    'lead_actor': movie_data['Actors'],
                    'release_date': movie_data['Released'],
                    'imdb_rating': movie_data['imdbRating'],
                    'imdb_url': f"https://www.imdb.com/title/{movie_data['imdbID']}/"
                }
                data_manager.add_movie_for_user(user_id, movie_details)
                flash('Movie added successfully!')
                return redirect(url_for('user_movies', user_id=user_id))
            else:
                flash('Movie not found. Please try again.')
        else:
            flash('Error connecting to OMDb API.')

    return render_template('add_movie.html',
                           user_id=user_id)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>',
           methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """Handle updating an existing movie."""
    if request.method == 'POST':
        updated_movie_data = {
            'movie_name': request.form['movie_name'],
            'poster_url': request.form['poster_url'],
            'lead_actor': request.form['lead_actor'],
            'release_date': request.form['release_date'],
            'imdb_rating': request.form['imdb_rating'],
            'imdb_url': request.form['imdb_url']
        }
        data_manager.update_movie(movie_id, updated_movie_data)
        return redirect(url_for('user_movies', user_id=user_id))

    movie = data_manager.get_movie_by_id(movie_id)
    return render_template('update_movie.html',
                           user_id=user_id, movie=movie)


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>',
           methods=['POST'])
def delete_movie(user_id, movie_id):
    """Handle deleting a movie from a user's list."""
    data_manager.delete_movie(movie_id)
    return redirect(url_for('user_movies', user_id=user_id))


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password functionality."""
    if request.method == 'POST':
        email = request.form['email']
        user = data_manager.get_user_by_email(email)
        if user:
            flash('Password reset link has been sent to your email.')
        else:
            flash('Email not found. Please try again.')
        return redirect(url_for('login'))
    return render_template('forgot_password.html')


@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 Not Found errors."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 Internal Server Error."""
    return render_template('500.html'), 500


@app.route('/movies/<int:movie_id>/reviews', methods=['GET', 'POST'])
def add_review(movie_id):
    """Handle adding a review to a movie."""
    if request.method == 'POST':
        review_text = request.form['review_text']
        rating = request.form['rating']
        user_id = session['user_id']

        review = Review(
            user_id=user_id,
            movie_id=movie_id,
            review_text=review_text,
            rating=rating
        )
        session_db = data_manager.Session()
        session_db.add(review)
        session_db.commit()
        session_db.close()

        flash('Review added successfully!')
        return redirect(url_for('movie_details', movie_id=movie_id))

    return render_template('add_review.html',
                           movie_id=movie_id)


@app.route('/movies/<int:movie_id>/reviews/<int:review_id>/delete',
           methods=['POST'])
def delete_review(movie_id, review_id):
    """Handle deleting a review."""
    session_db = data_manager.Session()
    review = session_db.query(Review).filter_by(id=review_id).first()

    if review:
        session_db.delete(review)
        session_db.commit()
        flash('Review deleted successfully!')

    session_db.close()
    return redirect(url_for('movie_details', movie_id=movie_id))


@app.route('/review/<int:review_id>/edit', methods=['GET', 'POST'])
def edit_review(review_id):
    """Handle editing an existing review."""
    review = data_manager.get_review_by_id(review_id)
    if request.method == 'POST':
        review_text = request.form['review_text']
        rating = int(request.form['rating'])
        data_manager.update_review(review_id, review_text, rating)
        flash('Review updated successfully!')
        return redirect(url_for('movie_details',
                                movie_id=review.movie_id))

    return render_template('edit_review.html', review=review)


@app.route('/movie/<int:movie_id>', methods=['GET', 'POST'])
def movie_details(movie_id):
    """Render movie details page with associated reviews."""
    movie = data_manager.get_movie_by_id(movie_id)
    user_id = session.get('user_id')

    if request.method == 'POST':
        rating = int(request.form['rating'])
        review_text = request.form['review_text']
        data_manager.add_review({
            'user_id': user_id,
            'movie_id': movie_id,
            'review_text': review_text,
            'rating': rating
        })
        flash('Review added successfully!')
        return redirect(url_for('movie_details', movie_id=movie_id))

    return render_template('movie_details.html',
                           movie=movie, user_id=user_id)


@app.route('/movies/<int:movie_id>/all_reviews')
def all_reviews(movie_id):
    """View function to display all reviews for a movie."""
    movie = data_manager.get_movie_by_id(movie_id)
    reviews = data_manager.get_reviews_for_movie(movie_id)

    if movie:
        return render_template('all_reviews.html',
                               movie=movie, reviews=reviews)
    else:
        flash('Movie not found.')
        return redirect(url_for('home'))


# Run the application
if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, redirect, url_for, flash, session, request
import requests
from datamanager.sqlite_data_manager import SQLiteDataManager
from datetime import datetime
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

# Initialize the SQLiteDataManager with the database path
data_manager = SQLiteDataManager('datamanager/moviwebapp.db')

OMDB_API_KEY = 'd5ee8f11'


@app.route('/')
def home():
    if 'user_id' in session:
        # Get the user's name from the session if logged in
        user_name = session.get('user_name')
        return redirect(url_for('dashboard'))
    else:
        return render_template('home.html')



@app.route('/users')
def list_users():
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'birthdate': datetime.strptime(request.form['birthdate'], '%Y-%m-%d').date(),
            'email': request.form['email'],
            'password': request.form['password']
        }
        data_manager.add_user(user_data)
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
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
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('home'))


# Protect movie-related routes by ensuring the user is logged in
@app.route('/users/<int:user_id>/movies')
def user_movies(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('login'))
    movies = data_manager.get_user_movies(user_id)
    return render_template('user_movies.html', user_id=user_id, movies=movies)


# Route for adding a new movie to a user's list
@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    if request.method == 'POST':
        movie_title = request.form['movie_title']
        # Fetch movie details from OMDb API
        omdb_url = f"http://www.omdbapi.com/?t={movie_title}&apikey={OMDB_API_KEY}"
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

                # Save to the database (pass the dictionary)
                data_manager.add_movie_for_user(user_id, movie_details)

                flash('Movie added successfully!')
                return redirect(url_for('user_movies', user_id=user_id))
            else:
                flash('Movie not found. Please try again.')
        else:
            flash('Error connecting to OMDb API.')
    return render_template('add_movie.html', user_id=user_id)


# Route for updating an existing movie
@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    if request.method == 'POST':
        new_movie_name = request.form['movie_name']
        data_manager.update_movie(movie_id, new_movie_name)
        return redirect(url_for('user_movies', user_id=user_id))
    # Pre-fill form with existing movie data (if available)
    return render_template('update_movie.html', user_id=user_id, movie_id=movie_id)


# Route for deleting a movie from a user's list
@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(user_id, movie_id):
    data_manager.delete_movie(movie_id)
    return redirect(url_for('user_movies', user_id=user_id))


# Run the application
if __name__ == '__main__':
    app.run(debug=True)

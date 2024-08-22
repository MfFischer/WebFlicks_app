from flask import Flask, request, jsonify, render_template, redirect, url_for
from datamanager.sqlite_data_manager import SQLiteDataManager

# Initialize the Flask application
app = Flask(__name__)

# Initialize the SQLiteDataManager with the database path
data_manager = SQLiteDataManager('moviwebapp.db')  # Use the appropriate path to your database


@app.route('/')
def home():
    return "Welcome to MovieWeb App!"


# Route for listing all users in HTML format
@app.route('/users')
def list_users():
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)


# Route for adding a new user via a POST request (JSON API)
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        user_name = request.form['name']
        data_manager.add_user(user_name)
        return redirect(url_for('list_users'))
    return render_template('add_user.html')


# Route for viewing a specific user's movies
@app.route('/users/<int:user_id>')
def user_movies(user_id):
    movies = data_manager.get_user_movies(user_id)
    return render_template('user_movies.html', user_id=user_id, movies=movies)


# Route for adding a new movie to a user's list
@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    if request.method == 'POST':
        movie_name = request.form['movie_name']
        data_manager.add_movie_for_user(user_id, movie_name)
        return redirect(url_for('user_movies', user_id=user_id))
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

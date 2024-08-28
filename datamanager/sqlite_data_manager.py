import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from werkzeug.security import generate_password_hash
from .data_model import Base, User, Movie, Review
from sqlalchemy.orm import joinedload

# Define the path to the database
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'moviwebapp.db')

# Create the database engine as a global variable
engine = create_engine(f'sqlite:///{DATABASE_PATH}')


class SQLiteDataManager:
    """
    A data manager class for handling SQLite database operations using SQLAlchemy.
    """

    def __init__(self):
        """
        Initialize the SQLiteDataManager.
        """
        # Assign the engine to an instance variable
        self.engine = engine

        # Bind the sessionmaker to the engine
        self.Session = scoped_session(sessionmaker(bind=engine))

        # Create all tables in the database if they don't exist
        Base.metadata.create_all(engine)

    def add_user(self, user_data: dict):
        """
        Add a new user to the SQLite database.
        """
        session = self.Session()
        try:
            hashed_password = generate_password_hash(user_data['password'])
            new_user = User(
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                birthdate=user_data['birthdate'],
                email=user_data['email'],
                password_hash=hashed_password
            )
            session.add(new_user)
            session.commit()
            return new_user.id
        finally:
            session.close()

    def get_all_users(self):
        """
        Retrieve all users from the SQLite database.
        """
        session = self.Session()
        try:
            users = session.query(User).all()
            return [{'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name} for user in users]
        finally:
            session.close()

    def get_user_by_email(self, email: str):
        """
        Retrieve a user from the database by their email.
        """
        session = self.Session()
        try:
            user = session.query(User).filter_by(email=email).first()
            return user
        finally:
            session.close()

    def get_user_movies(self, user_id: int):
        """
        Retrieve all movies associated with a specific user from the SQLite database.
        """
        session = self.Session()
        try:
            movies = session.query(Movie).filter_by(user_id=user_id).all()
            return [{
                'id': movie.id,
                'movie_name': movie.movie_name,
                'poster_url': movie.poster_url,
                'lead_actor': movie.lead_actor,
                'release_date': movie.release_date,
                'imdb_rating': movie.imdb_rating,
                'imdb_url': movie.imdb_url
            } for movie in movies]
        finally:
            session.close()

    def add_movie_for_user(self, user_id: int, movie_data: dict):
        """
        Add a movie to a specific user's movie list in the SQLite database.
        """
        session = self.Session()
        try:
            new_movie = Movie(
                user_id=user_id,
                movie_name=movie_data['movie_name'],
                poster_url=movie_data['poster_url'],
                lead_actor=movie_data['lead_actor'],
                release_date=movie_data['release_date'],
                imdb_rating=movie_data['imdb_rating'],
                imdb_url=movie_data['imdb_url']
            )
            session.add(new_movie)
            session.commit()
        finally:
            session.close()

    def update_movie(self, movie_id: int, new_movie_data: dict):
        """
        Update the details of a specific movie in the SQLite database.
        """
        session = self.Session()
        try:
            movie = session.query(Movie).filter_by(id=movie_id).one()
            movie.movie_name = new_movie_data.get('movie_name', movie.movie_name)
            movie.poster_url = new_movie_data.get('poster_url', movie.poster_url)
            movie.lead_actor = new_movie_data.get('lead_actor', movie.lead_actor)
            movie.release_date = new_movie_data.get('release_date', movie.release_date)
            movie.imdb_rating = new_movie_data.get('imdb_rating', movie.imdb_rating)
            movie.imdb_url = new_movie_data.get('imdb_url', movie.imdb_url)
            session.commit()
        finally:
            session.close()

    def delete_movie(self, movie_id: int):
        """
        Delete a specific movie from the SQLite database.
        """
        session = self.Session()
        try:
            session.query(Movie).filter_by(id=movie_id).delete()
            session.commit()
        finally:
            session.close()

    def get_movie_by_id(self, movie_id: int):
        """
        Fetch movie details by movie ID, including reviews.
        """
        session = self.Session()
        try:
            movie = session.query(Movie).options(joinedload(Movie.reviews)).filter_by(id=movie_id).one()
            movie_reviews = [{
                'id': review.id,
                'user_name': f"{review.user.first_name} {review.user.last_name}",
                'review_text': review.review_text,
                'rating': review.rating,
                'user_id': review.user_id
            } for review in movie.reviews]

            return {
                'id': movie.id,
                'movie_name': movie.movie_name,
                'poster_url': movie.poster_url,
                'lead_actor': movie.lead_actor,
                'release_date': movie.release_date,
                'imdb_rating': movie.imdb_rating,
                'imdb_url': movie.imdb_url,
                'reviews': movie_reviews
            }
        finally:
            session.close()

    def search_user_movies(self, user_id, search_query):
        """
        Search for movies belonging to a specific user that match a search query.
        """
        session = self.Session()
        try:
            # Query movies for the user, filtering by the search query in a case-insensitive manner.
            movies = session.query(Movie).filter(
                Movie.user_id == user_id,
                Movie.movie_name.ilike(f'%{search_query}%')
            ).all()

            # Return a list of dictionaries with relevant movie details.
            return [{
                'id': movie.id,
                'movie_name': movie.movie_name,
                'poster_url': movie.poster_url,
                'lead_actor': movie.lead_actor,
                'release_date': movie.release_date,
                'imdb_rating': movie.imdb_rating,
                'imdb_url': movie.imdb_url
            } for movie in movies]
        finally:
            # Ensure the session is closed after the query is executed.
            session.close()

    def add_review(self, review_data: dict):
        """
        Add a new review to the database.
        """
        session = self.Session()
        try:
            new_review = Review(**review_data)
            session.add(new_review)
            session.commit()
        finally:
            session.close()

    def update_review(self, review_id: int, review_text: str, rating: int):
        """
        Update an existing review in the database.
        """
        session = self.Session()
        try:
            # Retrieve the review to be updated
            review = session.query(Review).filter_by(id=review_id).one()
            # Update the review fields
            review.review_text = review_text
            review.rating = rating
            # Commit the changes to the database
            session.commit()
        finally:
            # Ensure the session is closed after the operation
            session.close()

    def delete_review(self, review_id: int):
        """
        Delete a review by its ID.
        """
        session = self.Session()
        try:
            review = session.query(Review).filter_by(id=review_id).one_or_none()
            if review:
                session.delete(review)
                session.commit()
        finally:
            session.close()

    def get_reviews_for_movie(self, movie_id: int, limit: int = None):
        """
        Fetch reviews for a specific movie. Optionally limit the number of reviews.
        """
        session = self.Session()
        try:
            query = session.query(Review).filter_by(movie_id=movie_id).order_by(Review.id.desc())
            if limit:
                query = query.limit(limit)
            reviews = query.all()
            return reviews
        finally:
            session.close()

    def get_review_by_id(self, review_id):
        pass


# The SQLiteDataManager can now be instantiated without needing to pass a db_path
data_manager = SQLiteDataManager()

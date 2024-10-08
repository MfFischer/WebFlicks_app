from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime


# Create the Base class that our models will inherit from
Base = declarative_base()


class User(Base):
    """
    Represents a user in the system.
    """
    __tablename__ = 'users'

    # Primary key for the user table
    id = Column(Integer, primary_key=True, autoincrement=True)

    # User's first name, cannot be null
    first_name = Column(String(50), nullable=False)

    # User's last name, cannot be null
    last_name = Column(String(50), nullable=False)

    # User's birthdate, cannot be null
    birthdate = Column(Date, nullable=False)

    # User's email, must be unique and cannot be null
    email = Column(String(100), nullable=False, unique=True)

    # User's password hash, cannot be null
    password_hash = Column(String(200), nullable=False)

    # Relationship to associate User with their Movies
    movies = relationship("Movie", back_populates="user")

    def __repr__(self):
        """
        Returns a string representation of the User object, useful for debugging.
        """
        return f"<User(id={self.id}, name={self.first_name} {self.last_name}, email={self.email})>"


class Movie(Base):
    """
    Represents a movie associated with a user in the system.
    """
    __tablename__ = 'movies'

    # Primary key for the movie table
    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_name = Column(String(150), nullable=False)

    # Name of the movie, cannot be null
    movie_name = Column(String(150), nullable=False)

    # URL of the movie's poster image, can be null
    poster_url = Column(String(250), nullable=True)

    # Name of the lead actor, can be null
    lead_actor = Column(String(100), nullable=True)

    # Release date of the movie, can be null
    release_date = Column(String(50), nullable=True)

    # IMDb rating of the movie, can be null
    imdb_rating = Column(String(10), nullable=True)

    # IMDb URL for the movie, can be null
    imdb_url = Column(String(250), nullable=True)

    # Foreign key linking the movie to a user, cannot be null
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationship to associate Movie with the User who added it
    user = relationship("User", back_populates="movies")

    # Relationship with Review
    reviews = relationship("Review", back_populates="movie", cascade="all, delete-orphan")

    def __repr__(self):
        """
        Returns a string representation of the Movie object, useful for debugging.
        """
        return f"<Movie(id={self.id}, name={self.movie_name}, user_id={self.user_id})>"


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
    review_text = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)  # Assuming a 1-10 rating scale
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='reviews')
    movie = relationship('Movie', back_populates='reviews')

    def __repr__(self):
        return f"<Review(id={self.id}, user_id={self.user_id}, movie_id={self.movie_id}, rating={self.rating})>"


# Adding back_populates in User and Movie classes
User.reviews = relationship('Review', order_by=Review.id, back_populates='user')
Movie.reviews = relationship('Review', order_by=Review.id, back_populates='movie')

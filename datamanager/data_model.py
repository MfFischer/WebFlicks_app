from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

# Create the Base class that our models will inherit from
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    birthdate = Column(Date, nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(200), nullable=False)

    movies = relationship("Movie", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, name={self.first_name} {self.last_name}, email={self.email})>"


class Movie(Base):
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_name = Column(String(150), nullable=False)
    poster_url = Column(String(250), nullable=True)
    lead_actor = Column(String(100), nullable=True)
    release_date = Column(String(50), nullable=True)
    imdb_rating = Column(String(10), nullable=True)
    imdb_url = Column(String(250), nullable=True)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="movies")

    def __repr__(self):
        return f"<Movie(id={self.id}, name={self.movie_name}, user_id={self.user_id})>"

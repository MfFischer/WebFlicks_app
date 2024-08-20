from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from typing import List, Tuple
from datamanager.data_manager_interface import DataManagerInterface

# Define the base class for ORM models
Base = declarative_base()


class User(Base):
    """
    ORM model for the users table.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)


class Movie(Base):
    """
    ORM model for the user_movies table.
    """
    __tablename__ = 'user_movies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    movie_name = Column(String, nullable=False)


class SQLiteDataManager(DataManagerInterface):
    """
    Concrete implementation of DataManagerInterface for SQLite databases using SQLAlchemy.
    """

    def __init__(self, db_path: str):
        """
        Initialize the SQLiteDataManager with the path to the database.
        """
        # Create the database engine
        self.engine = create_engine(f'sqlite:///{db_path}')

        # Bind the sessionmaker to the engine
        self.Session = scoped_session(sessionmaker(bind=self.engine))

        # Create all tables
        Base.metadata.create_all(self.engine)

    def get_all_users(self) -> List[Tuple[int, str]]:
        """
        Retrieve all users from the SQLite database.

        Returns:
            List[Tuple[int, str]]: A list of tuples, where each tuple contains user ID and name.
        """
        session = self.Session()
        try:
            users = session.query(User).all()
            # Access the actual values of the columns
            return [(user.id, user.name) for user in users]
        finally:
            session.close()

    def get_user_movies(self, user_id: int) -> List[str]:
        """
        Retrieve all movies associated with a specific user from the SQLite database.

        Args:
            user_id (int): The ID of the user.

        Returns:
            List[str]: A list of movie names associated with the user.
        """
        session = self.Session()
        try:
            movies = session.query(Movie).filter_by(user_id=user_id).all()
            # Access the actual values of the columns
            return [movie.movie_name for movie in movies]
        finally:
            session.close()

    def add_user(self, name: str) -> int:
        """
        Add a new user to the SQLite database.

        Args:
            name (str): The name of the user.

        Returns:
            int: The ID of the newly created user.
        """
        session = self.Session()
        try:
            new_user = User(name=name)
            session.add(new_user)
            session.commit()
            # Access the actual value of the primary key
            return new_user.id
        finally:
            session.close()

    def add_movie_for_user(self, user_id: int, movie_name: str):
        """
        Add a movie to a specific user's movie list in the SQLite database.

        Args:
            user_id (int): The ID of the user.
            movie_name (str): The name of the movie to add.
        """
        session = self.Session()
        try:
            new_movie = Movie(user_id=user_id, movie_name=movie_name)
            session.add(new_movie)
            session.commit()
        finally:
            session.close()

    def delete_user(self, user_id: int):
        """
        Delete a user and their associated movies from the SQLite database.

        Args:
            user_id (int): The ID of the user to delete.
        """
        session = self.Session()
        try:
            # Delete all movies for the user
            session.query(Movie).filter_by(user_id=user_id).delete()

            # Delete the user
            session.query(User).filter_by(id=user_id).delete()

            session.commit()
        finally:
            session.close()

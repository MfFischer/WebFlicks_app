from abc import ABC, abstractmethod
import sqlite3
from typing import List, Tuple


class DataManagerInterface(ABC):
    """
    Abstract base class that defines the interface for data management.
    """

    @abstractmethod
    def get_all_users(self) -> List[Tuple[int, str]]:
        """
        Retrieve all users from the data source.
        """
        pass

    @abstractmethod
    def get_user_movies(self, user_id: int) -> List[str]:
        """
        Retrieve all movies associated with a specific user.
        """
        pass

    @abstractmethod
    def add_user(self, name: str) -> int:
        """
        Add a new user to the data source.
        """
        pass

    @abstractmethod
    def add_movie_for_user(self, user_id: int, movie_name: str):
        """
        Add a movie to a specific user's movie list.
        """
        pass

    @abstractmethod
    def delete_user(self, user_id: int):
        """
        Delete a user and their associated movies from the data source.
        """
        pass


class SQLiteDataManager(DataManagerInterface):
    """
    Concrete implementation of DataManagerInterface for SQLite databases.
    """

    def __init__(self, db_path: str):
        """
        Initialize the SQLiteDataManager with the path to the database.
        """
        self.db_path = db_path

    def _connect(self):
        """
        Helper method to establish a connection to the SQLite database.
        """
        return sqlite3.connect(self.db_path)

    def get_all_users(self) -> List[Tuple[int, str]]:
        """
        Retrieve all users from the SQLite database.
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            return cursor.fetchall()

    def get_user_movies(self, user_id: int) -> List[str]:
        """
        Retrieve all movies associated with a specific user from the SQLite database.
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT movie_name FROM user_movies WHERE user_id=?", (user_id,))
            return [row[0] for row in cursor.fetchall()]

    def add_user(self, name: str) -> int:
        """
        Add a new user to the SQLite database.
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
            conn.commit()
            return cursor.lastrowid

    def add_movie_for_user(self, user_id: int, movie_name: str):
        """
        Add a movie to a specific user's movie list in the SQLite database.
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user_movies (user_id, movie_name) VALUES (?, ?)", (user_id, movie_name))
            conn.commit()

    def delete_user(self, user_id: int):
        """
        Delete a user and their associated movies from the SQLite database.
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_movies WHERE user_id=?", (user_id,))
            cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
            conn.commit()

from abc import ABC, abstractmethod
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

import unittest
from app import app, data_manager
from datamanager.data_model import Base  # Import Base directly from data_model
from datamanager.sqlite_data_manager import engine  # Import the engine

class MovieWebAppTestCase(unittest.TestCase):

    def setUp(self):
        """
        Set up the test client and initialize a clean database before each test.
        """
        # Set up the Flask test client
        app.config['TESTING'] = True
        self.client = app.test_client()

        # Set up the database
        with app.app_context():
            data_manager.Session.remove()  # Clean the session
            Base.metadata.drop_all(bind=engine)  # Use Base from data_model and engine directly
            Base.metadata.create_all(bind=engine)

    def tearDown(self):
        """
        Clean up the database after each test.
        """
        with app.app_context():
            data_manager.Session.remove()
            Base.metadata.drop_all(bind=engine)  # Use Base from data_model and engine directly

    def test_home_page(self):
        """
        Test that the home page loads correctly.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to MovieWeb App!', response.data)

    def test_registration_page(self):
        """
        Test that the registration page loads and works correctly.
        """
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

        response = self.client.post('/register', data={
            'first_name': 'Test',
            'last_name': 'User',
            'birthdate': '1990-01-01',
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful!', response.data)  # Check for the flash message

    def test_login_page(self):
        """
        Test that the login page loads and works correctly.
        """
        # First, register a user
        self.client.post('/register', data={
            'first_name': 'Test',
            'last_name': 'User',
            'birthdate': '1990-01-01',
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)

        # Now, try to log in
        response = self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome, Test!', response.data)  # Check for the flash message

    def test_dashboard_access(self):
        """
        Test that accessing the dashboard requires login.
        """
        # Attempt to access the dashboard without logging in
        response = self.client.get('/dashboard', follow_redirects=True)
        self.assertIn(b'Please log in.', response.data)  # Check for the flash message

    def test_add_movie(self):
        """
        Test adding a new movie for a user.
        """
        # Register and log in a user
        self.client.post('/register', data={
            'first_name': 'Test',
            'last_name': 'User',
            'birthdate': '1990-01-01',
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)

        self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)

        # Add a movie
        response = self.client.post('/users/1/add_movie', data={
            'movie_title': 'Inception'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Movie added successfully!', response.data)  # Check for the flash message

    def test_update_movie(self):
        """
        Test updating an existing movie.
        """
        # Register, log in, and add a movie first
        self.client.post('/register', data={
            'first_name': 'Test',
            'last_name': 'User',
            'birthdate': '1990-01-01',
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)

        self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)

        self.client.post('/users/1/add_movie', data={
            'movie_title': 'Inception'
        }, follow_redirects=True)

        # Update the movie
        response = self.client.post('/users/1/update_movie/1', data={
            'movie_name': 'Inception Updated',
            'poster_url': 'http://example.com/poster.jpg',
            'lead_actor': 'Leonardo DiCaprio',
            'release_date': '2010-07-16',
            'imdb_rating': '8.8',
            'imdb_url': 'http://www.imdb.com/title/tt1375666/'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Inception Updated', response.data)

    def test_delete_movie(self):
        """
        Test deleting a movie.
        """
        # Register, log in, and add a movie first
        self.client.post('/register', data={
            'first_name': 'Test',
            'last_name': 'User',
            'birthdate': '1990-01-01',
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)

        self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)

        self.client.post('/users/1/add_movie', data={
            'movie_title': 'Inception'
        }, follow_redirects=True)

        # Delete the movie
        response = self.client.post('/users/1/delete_movie/1', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Inception', response.data)


if __name__ == '__main__':
    unittest.main()

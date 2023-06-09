import unittest
import datetime
from app import app, db, User, Movie, allowed_file, display_image


class ModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        db.session.commit()

    def tearDown(self):
        test_user = User.query.filter_by(username='test_user').first()
        test_movie = Movie.query.filter_by(title='Test Movie').first()

        # Delete the test user if it exists
        if test_user:
            db.session.delete(test_user)

        # Delete the test movie if it exists
        if test_movie:
            db.session.delete(test_movie)

        db.session.commit()

    def test_user_model_fields(self):
        # Create a test user
        user = User(
            id=1,
            username='test_user',
            password='password123',
            email='test@example.com'
        )
        db.session.add(user)
        db.session.commit()

        # Retrieve the user from the database
        retrieved_user = User.query.filter_by(username='test_user').first()

        # Assert the fields of the user model
        self.assertEqual(retrieved_user.id, 1)
        self.assertEqual(retrieved_user.username, 'test_user')
        self.assertEqual(retrieved_user.password, 'password123')
        self.assertEqual(retrieved_user.email, 'test@example.com')

    def test_movie_model(self):
        user = User(
            id=1,
            username='test_user',
            password='password123',
            email='test@example.com'
        )
        db.session.add(user)
        db.session.commit()

        movie = Movie(
            title='Test Movie',
            genre='Action',
            director='John Doe',
            released='2022-01-01',
            synopsis='A test movie synopsis.',
            rating=4.5,
            poster='poster.jpg',
            posted_by='test_user',
            movie_id=1
        )
        db.session.add(movie)
        db.session.commit()

        # Retrieve the movie from the database
        retrieved_movie = Movie.query.filter_by(title='Test Movie').first()

        # Assert the fields of the movie model
        self.assertEqual(retrieved_movie.title, 'Test Movie')
        self.assertEqual(retrieved_movie.genre, 'Action')
        self.assertEqual(retrieved_movie.director, 'John Doe')
        self.assertEqual(retrieved_movie.released, datetime.date(2022, 1, 1))
        self.assertEqual(retrieved_movie.synopsis, 'A test movie synopsis.')
        self.assertEqual(retrieved_movie.rating, 4.5)
        self.assertEqual(retrieved_movie.poster, 'poster.jpg')
        self.assertEqual(retrieved_movie.posted_by, 'test_user')
        self.assertEqual(retrieved_movie.movie_id, 1)

        db.session.delete(movie)
        db.session.commit()
        retrieved_movie = Movie.query.filter_by(title='Test Movie').first()
        self.assertIsNone(retrieved_movie)

    def test_delete_movie(self):
        user = User(
            id=1,
            username='test_user',
            password='password123',
            email='test@example.com'
        )
        db.session.add(user)
        db.session.commit()
        movie = Movie(
            title='Test Movie',
            genre='Action',
            director='John Doe',
            released='2022-01-01',
            synopsis='A test movie synopsis.',
            rating=4.5,
            poster='poster.jpg',
            posted_by='test_user',
            movie_id=1
        )
        db.session.add(movie)
        db.session.commit()
        db.session.delete(movie)
        db.session.commit()

        retrieved_movie = Movie.query.filter_by(title='Test Movie').first()
        self.assertIsNone(retrieved_movie)

    def test_update_movie(self):
        user = User(
            id=1,
            username='test_user',
            password='password123',
            email='test@example.com'
        )
        db.session.add(user)
        db.session.commit()
        movie = Movie(
            title='Test Movie',
            genre='Action',
            director='John Doe',
            released='2022-01-01',
            synopsis='A test movie synopsis.',
            rating=4.5,
            poster='poster.jpg',
            posted_by='test_user',
            movie_id=1
        )
        db.session.add(movie)
        db.session.commit()

        movie.genre = 'New Genre'
        movie.director = 'New Director'
        movie.released = '2023-01-01'
        movie.rating = 5.0
        db.session.commit()
        retrieved_movie = Movie.query.filter_by(title='Test Movie').first()
        self.assertEqual(retrieved_movie.genre, 'New Genre')
        self.assertEqual(retrieved_movie.director, 'New Director')
        self.assertEqual(retrieved_movie.released, datetime.date(2023, 1, 1))
        self.assertEqual(retrieved_movie.rating, 5.0)

    def test_allowed_file(self):
        # Test a valid filename with an allowed extension
        filename = 'image.jpg'
        result = allowed_file(filename)
        self.assertTrue(result)

        # Test a valid filename with a non-allowed extension
        filename = 'document.pdf'
        result = allowed_file(filename)
        self.assertFalse(result)

        # Test an invalid filename without an extension
        filename = 'filewithoutextension'
        result = allowed_file(filename)
        self.assertFalse(result)

    def test_display_image(self):
        # Test redirect URL for a given filename
        filename = 'image.jpg'
        expected_url = '/static/uploads/image.jpg'
        with app.test_request_context():
            result = display_image(filename)
            self.assertEqual(result.location, expected_url)
            self.assertEqual(result.status_code, 301)



if __name__ == '__main__':
    unittest.main()

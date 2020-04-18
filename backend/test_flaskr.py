import json
import unittest

from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        # self.database_name = "triviatest"
        self.database_path = 'postgresql://postgres:pass@localhost:5432/triviatest'
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.add_question = {
            "question": "Does this unit test work",
            "answer": "Maybe",
            "category": 1,
            "difficulty": 5
        }

        self.add_question_notright = {
            "question": "should not work this unit test work",
            "answer": "opps",
            "category": 1,
            "difficulty": 5
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_paginated_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_request_beyond_valid_page(self):
        response = self.client().get('/questions?page=100')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_questions_by_category(self):
        response = self.client().get('/categories/5/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Entertainment')

    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['categories'], {'1': 'Science',
                                              '2': 'Art',
                                              '3': 'Geography',
                                              '4': 'History',
                                              '5': 'Entertainment',
                                              '6': 'Sports'})

    def test_delete_question(self):
        response = self.client().delete('/questions/25')
        data = json.loads(response.data)

        question = Question.query.filter(Question.id == 25).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 20)
        self.assertEqual(question, None)

    def test_delete_question_does_not_exist(self):
        response = self.client().delete('/questions/600')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_create_questions(self):
        response = self.client().post('/questions', json=self.add_question)
        data = json.loads(response.data)
        created_question = response.data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_create_questions_fails(self):
        response = self.client().post('/questions', json={})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_search_questions(self):
        response = self.client().post('/questions', json={'searchTerm': 'Bird'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_play(self):
        response = self.client().post('/quizzes', json={'previous_questions': [10, 11],
                                                        'quiz_category': {'type': 'History', 'id': '4'}})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'], 4)
        self.assertNotEqual(data['question']['id'], 10)
        self.assertNotEqual(data['question']['id'], 11)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

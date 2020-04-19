import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_question = questions[start:end]

    return current_question


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    CORS(app, resources={'/': {'origins': '*'}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')

        return response

    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        categories_dictionary = {}
        for category in categories:
            categories_dictionary[category.id] = category.type

        if len(categories_dictionary) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': categories_dictionary
        })

    @app.route('/questions')
    def get_questions():
        selection = Question.query.all()
        total_questions = len(selection)
        current_questions = paginate_questions(request, selection)

        categories = Category.query.all()
        categories_dictionary = {}
        for category in categories:
            categories_dictionary[category.id] = category.type

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': total_questions,
            'categories': categories_dictionary
        })

    @app.route('/questions/<int:id>', methods=['Delete'])
    def delete_question(id):
        try:
            question = Question.query.filter(Question.id == id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                'success': True,
                'deleted': id,
            })
        except:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        if body.get('searchTerm'):
            search_term = body.get('searchTerm')

            selection = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()

            if len(selection) == 0:
                abort(404)

            paginate = paginate_questions(request, selection)
            return jsonify({
                'success': True,
                'questions': paginate,
                'total_questions': len(Question.query.all())
            })
        else:
            new_question = body.get('question')
            new_answer = body.get('answer')
            new_category = body.get('category')
            new_difficulty = body.get('difficulty')

            if new_question == "" or new_answer == "":
                abort(422)

            try:

                question = Question(question=new_question, answer=new_answer, category=new_category,
                                    difficulty=new_difficulty)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'created': question.question,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })
            except:
                abort(422)

    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):
        category = Category.query.filter(Category.id == id).one_or_none()
        print(category)

        if category is None:
            abort(404)

        selection = Question.query.filter(Question.category == id).all()
        print(selection)
        current_selection = paginate_questions(request, selection)

        return jsonify({
            'success': True,
            'questions': current_selection,
            'total questions': len(Question.query.all()),
            'current_category': category.type
        })

    @app.route('/quizzes', methods=['POST'])
    def get_quizzes():

        body = request.get_json()

        previous_questions = body.get('previous_questions')

        category = body.get('quiz_category')

        if (category["type"] == '') or (previous_questions is None):
            abort(400)

        if category['id'] == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category=category['id']).all()

        total = len(questions)

        def get_random_question():
            return questions[random.randrange(0, len(questions), 1)]

        def check_if_used(question):
            used = False
            for previous_question in previous_questions:
                if previous_question == question.id:
                    used = True

            return used

        question = get_random_question()

        while check_if_used(question):
            question = get_random_question()

            if len(previous_questions) == total:
                return jsonify({
                    'success': True
                })

        return jsonify({
            'success': True,
            'question': question.format()
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"

        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method not allowed"
        }), 405

    return app


from flask import request, session, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe


class Signup(Resource):
    def post(self):
        json_data = request.get_json()
        username = json_data.get('username')
        password = json_data.get('password')
        image_url = json_data.get('image_url')
        bio = json_data.get('bio')

        try:
            user = User(
                username=username,
                password_hash=password,
                image_url=image_url,
                bio=bio
            )
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id

            return user.to_dict(), 201

        except IntegrityError:
            db.session.rollback()
            return {'error': 'Username already exists'}, 422


class CheckSession(Resource):
    def get(self):
        if 'user_id' in session:
            user_id = session['user_id']
            user = User.query.get(user_id)
            return user.to_dict(), 200
        else:
            return {}, 401


class Login(Resource):
    def post(self):
        json_data = request.get_json()
        username = json_data.get('username')
        password = json_data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200
        else:
            return {'error': 'Invalid username or password'}, 401


class Logout(Resource):
    def delete(self):
        if 'user_id' in session:
            session.pop('user_id')
            return {}, 204
        else:
            return {'error': 'Not logged in'}, 401


class RecipeIndex(Resource):
    def get(self):
        if 'user_id' in session:
            recipes = Recipe.query.all()
            recipe_data = [recipe.to_dict() for recipe in recipes]
            return recipe_data, 200
        else:
            return {'error': 'Not logged in'}, 401

    def post(self):
        if 'user_id' in session:
            json_data = request.get_json()
            title = json_data.get('title')
            instructions = json_data.get('instructions')
            minutes_to_complete = json_data.get('minutes_to_complete')
            user_id = session['user_id']

            try:
                recipe = Recipe(
                    title=title,
                    instructions=instructions,
                    minutes_to_complete=minutes_to_complete,
                    user_id=user_id
                )
                db.session.add(recipe)
                db.session.commit()

                return recipe.to_dict(), 201

            except IntegrityError:
                db.session.rollback()
                return {'error': 'Error creating recipe'}, 422

        else:
            return {'error': 'Not logged in'}, 401


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5000, debug=True)
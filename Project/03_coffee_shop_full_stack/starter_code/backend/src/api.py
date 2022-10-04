# from crypt import methods
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES


@app.route('/drinks', methods=['GET'])
def short_drink_details():
    """returns drinks with summarized details"""
    try:
        drinks = [drink.short() for drink in Drink.query.all()]
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(404)


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks')
def full_drink_details(jwt):
    """returns drinks with full details"""
    try:
        drinks = [drink.long() for drink in Drink.query.all()]
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(404)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
    """adds a new drink to database"""
    body = request.get_json()
    try:
        new_title = body.get('title')
        new_recipe = json.dumps([body.get('recipe')])
        # json.dumps() converts a python object to json string
        new_drink = Drink(title=new_title, recipe=new_recipe)
        new_drink.insert()
        return jsonify({
            'success': True,
            'drinks': new_drink.long()
        })
    except:
        abort(400)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(jwt, drink_id):
    """edits the drink title using its' id"""
    body = request.get_json()
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if not drink:
        abort(404)
    else:
        try:
            if 'title' in body:
                drink.title = body.get('title')
                drink.update()
                return jsonify({
                    'success': True,
                    'drinks': [drink.long()]
                })
            elif 'recipe' in body:
                drink.recipe = json.dumps([body.get('recipe')])
                drink.update()
                return jsonify({
                    'success': True,
                    'drinks': [drink.long()]
                })
        except:
            abort(422)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt, drink_id):
    """deletes drink from database with a given id"""
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if not drink:
        abort(404)
    else:
        try:
            drink.delete()
            return jsonify({
                'success': True,
                'delete': drink.id
            })
        except:
            abort(422)


# Error Handling

@app.errorhandler(400)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request. check request body"
    }), 400


@app.errorhandler(401)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Authorization Error"
    }), 401


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


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

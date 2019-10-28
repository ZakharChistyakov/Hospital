from flask_jwt_extended import (
    jwt_refresh_token_required, get_jwt_identity, create_access_token, create_refresh_token, jwt_required,
    set_access_cookies, set_refresh_cookies
)
from flask import Blueprint, request, jsonify, after_this_request
from flask_restplus import Api, Resource, fields

from db import mongo
import pymongo.errors
from crypt import bcrypt

api_bp = Blueprint("api", __name__)
api = Api(api_bp)

user_reg = api.model('UserReg', {
    'username': fields.String,
    'password': fields.String,
    'name': fields.String,
    'number': fields.String
})


@api.route('/register')
class UserRegister(Resource):
    @api.doc(body=user_reg)
    def post(self):
        data = request.get_json()
        if mongo.db.users.find_one({'username': data['username']}):
            return {'ok': False,
                    'message': 'User already registered'
                    }, 500
        password = bcrypt.generate_password_hash(data['password'])
        try:
            mongo.db.users.insert_one(
                {'username': data['username'], 'password': password, 'admin': False, 'worker': False,
                 'name': data['name'], 'number': data['phone']}
            )
        except pymongo.errors:
            return {'ok': False,
                    'message': 'DB error'
                    }, 500
        return {'ok': True,
                'message': 'Registration successful'
                }, 201


user_auth = api.model('UserAuth', {
    'username': fields.String,
    'password': fields.String
})


@api.route('/login')
class UserLogin(Resource):
    @api.doc(body=user_auth)
    def post(self):
        data = request.get_json()
        user = mongo.db.users.find_one({'username': data['username']})
        if not user:
            return {'ok': False,
                    'message': 'User not found'
                    }, 500
        if not bcrypt.check_password_hash(user['password'], data['password']):
            return {'ok': False,
                    'message': 'Incorrect password'
                    }, 500
        result = jsonify({'ok': True,
                          'message': 'Login successful'}, 200)
        set_access_cookies(result, create_access_token(identity=user['username']))
        set_refresh_cookies(result, create_refresh_token(identity=user['username']))
        return result


@api.route('/refresh')
class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        try:
            user = get_jwt_identity()
            result = jsonify({'ok': True,
                              'message': 'Refresh successful'}, 200)
            set_access_cookies(result, create_access_token(identity=user['username']))
            set_refresh_cookies(result, create_refresh_token(identity=user['username']))
            return result
        except:
            return {'ok': False}, 500


@api.route('/logout')
class UserLogout(Resource):
    def post(self):
        @after_this_request
        def delete_access(response):
            response.set_cookie('access_token_cookie', '', max_age=0)
            response.set_cookie('refresh_token_cookie', '', max_age=0)
            return response

        return {'ok': True}, 200


flags = api.model('UserFlags', {
    'username': fields.String,
    'worker': fields.Boolean,
    'admin': fields.Boolean
})


@api.route('/edit_flags')
class UserEditFlags(Resource):
    @api.doc(body=flags)
    def post(self):
        data = request.get_json()
        if not mongo.db.users.find_one({'username': data['username']}):
            return {'ok': False,
                    'message': 'User not found'
                    }, 500
        try:
            mongo.db.users.update(
                {'username': data['username']}, {'$set': {'worker': data['worker'], 'admin': data['admin']}}
            )
        except pymongo.errors:
            return {'ok': False,
                    'message': 'DB error'
                    }, 500
        return {'ok': True,
                'message': 'Flags updated'
                }, 200


profile = api.model('UserProfile', {
    'password': fields.String,
    'password2': fields.String,
    'phone_number': fields.String
})


@api.route('/edit_profile')
class UserEditProfile(Resource):
    @jwt_required
    @api.doc(body=profile)
    def post(self):
        data = request.get_json()
        user = mongo.db.users.find_one({'username': get_jwt_identity()})
        if data['password']:
            if data['password'] == data['password2']:
                mongo.db.users.update({'username': user['username']},
                                      {'$set': {'password': bcrypt.generate_password_hash(data['password'])}})
            else:
                return {'ok': False,
                        'message': 'Passwords don\'t match'
                        }, 500
        if data['phone_number']:
            mongo.db.users.update({'username': user['username']},
                                  {'$set': {'phone_number': data['phone_number']}})
        return {'ok': True,
                'message': 'Info updated successfully'
                }, 200


note = api.model('note', {
    'fio': fields.String,
    'sex': fields.String,
    'date': fields.String,
    'description': fields.String,
    'passport': fields.String,
    'username': fields.String
})


@api.route('/note')
class Note(Resource):
    @jwt_required
    @api.doc(body=note)
    def post(self):
        username = get_jwt_identity()
        data = request.get_json()
        mongo.db.notes.insert_one(
            {'fio': data['fio'], 'sex': data['sex'], 'date': data['date'], 'price': 0,
             'description': data['description'], 'passport': data['passport'], 'username': username, 'worker': ''})
        return {'ok': True,
                'message': 'note created!'
                }, 201

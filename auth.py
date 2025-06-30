from functools import wraps
from flask import request, jsonify
from models import User
import jwt
from config import Config

SECRET_KEY = Config.SECRET_KEY


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'error': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)

    return decorated


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        try:
            # Убираем префикс "Bearer " из токена
            if token.startswith('Bearer '):
                token = token.split(' ')[1]

            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(current_user=current_user, *args, **kwargs)

    return decorated


def get_user_by_token(token):
    try:
        # Убираем префикс "Bearer" из токена
        if token.startswith('Bearer '):
            token = token.split(' ')[1]

        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return User.query.get(data['user_id'])
    except:
        return None

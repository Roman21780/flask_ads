import jwt
from flask import Blueprint, request, jsonify
from models import db, Advertisement, User
from auth import login_required, get_user_by_token
from datetime import datetime, timedelta, timezone
from config import Config


api_bp = Blueprint('api', __name__)


# Регистрация пользователя
@api_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    new_user = User(email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


# Авторизация пользователя
@api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    # Генерация JWT-токена
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=1) # время жизни токена
    }, Config.SECRET_KEY, algorithm='HS256')

    return jsonify({'token': token}), 200


@api_bp.route('/advertisements', methods=['POST'])
@login_required
def create_advertisement(current_user):
    data = request.get_json()
    new_ad = Advertisement(
        title=data['title'],
        description=data['description'],
        owner_id=current_user.id
    )
    db.session.add(new_ad)
    db.session.commit()
    return jsonify({'message': 'Advertisement created', 'id': new_ad.id}), 201


@api_bp.route('/advertisements/<int:ad_id>', methods=['GET'])
def get_advertisements(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    return jsonify({
        'id': ad.id,
        'title': ad.title,
        'description': ad.description,
        'created_at': ad.created_at,
        'owner_id': ad.owner_id
    })


@api_bp.route('/advertisements/<int:ad_id>', methods=['PUT'])
@login_required
def update_advertisement(ad_id, current_user):
    ad = Advertisement.query.get_or_404(ad_id)
    if ad.owner_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403

    data = request.get_json()
    ad.title = data.get('title', ad.title)
    ad.description = data.get('description', ad.description)
    db.session.commit()
    return jsonify({'message': 'Advertisement updated'})


@api_bp.route('/advertisements/<int:ad_id>', methods=['DELETE'])
@login_required
def delete_advertisement(ad_id, current_user):
    ad = Advertisement.query.get_or_404(ad_id)
    if ad.owner_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403

    db.session.delete(ad)
    db.session.commit()
    return jsonify({'message': 'Advertisement deleted'})

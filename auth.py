from aiohttp import web
import jwt
from datetime import datetime, timedelta, timezone
from database import db  # Импортируем глобальный экземпляр
from models import User
import os

SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')


@web.middleware
async def auth_middleware(request, handler):
    # Разрешаем доступ без токена к этим эндпоинтам
    if request.path in ['/api/register', '/api/login']:
        return await handler(request)

    # Для всех остальных запросов проверяем токен
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return web.json_response({'error': 'Token is missing'}, status=401)

    try:
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            token = auth_header

        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        async with await db.get_session() as session:
            current_user = await session.get(User, data['user_id'])
            if not current_user:
                return web.json_response({'error': 'User not found'}, status=401)

        request['current_user'] = current_user
    except jwt.ExpiredSignatureError:
        return web.json_response({'error': 'Token has expired'}, status=401)
    except jwt.InvalidTokenError:
        return web.json_response({'error': 'Invalid token'}, status=401)

    return await handler(request)

async def generate_token(user_id):
    return jwt.encode({
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=1),
    }, SECRET_KEY, algorithm='HS256')
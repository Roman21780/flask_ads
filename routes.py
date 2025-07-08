from aiohttp import web
from sqlalchemy import select
from database import db
from models import User, Advertisement
from auth import generate_token
import logging

logger = logging.getLogger(__name__)


def setup_routes(app):
    app.router.add_post('/api/register', register)
    app.router.add_post('/api/login', login)
    app.router.add_post('/api/advertisements', create_advertisement)
    app.router.add_get('/api/advertisements/{ad_id}', get_advertisement)
    app.router.add_put('/api/advertisements/{ad_id}', update_advertisement)
    app.router.add_delete('/api/advertisements/{ad_id}', delete_advertisement)


async def register(request):
    try:
        data = await request.json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return web.json_response({'error': 'Email and password required'}, status=400)

        async with await db.get_session() as session:
            # Используем select для проверки существующего пользователя
            existing_user = await session.execute(
                select(User).where(User.email == email)
            )
            if existing_user.scalar_one_or_none():
                return web.json_response({'error': 'Email already registered'}, status=409)

            new_user = User(email=email)
            new_user.set_password(password)
            session.add(new_user)
            await session.commit()

        return web.json_response({'message': 'User registered successfully'}, status=201)

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return web.json_response({'error': 'Internal server error'}, status=500)


async def login(request):
    try:
        data = await request.json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return web.json_response({'error': 'Email and password required'}, status=400)

        async with await db.get_session() as session:
            # Используем select для поиска пользователя
            result = await session.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()

            if not user or not user.check_password(password):
                return web.json_response({'error': 'Invalid credentials'}, status=401)

            token = await generate_token(user.id)
            return web.json_response({'token': token})

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return web.json_response({'error': 'Internal server error'}, status=500)


async def create_advertisement(request):
    data = await request.json()
    current_user = request['current_user']

    async with await db.get_session() as session:
        new_ad = Advertisement(
            title=data['title'],
            description=data['description'],
            owner_id=current_user.id
        )
        session.add(new_ad)
        await session.commit()

    return web.json_response({'message': 'Advertisement created', 'id': new_ad.id}, status=201)


async def get_advertisement(request):
    ad_id = int(request.match_info['ad_id'])

    async with await db.get_session() as session:
        ad = await session.get(Advertisement, ad_id)
        if not ad:
            raise web.HTTPNotFound()

    return web.json_response({
        'id': ad.id,
        'title': ad.title,
        'description': ad.description,
        'created_at': ad.created_at.isoformat(),
        'owner_id': ad.owner_id
    })


async def update_advertisement(request):
    ad_id = int(request.match_info['ad_id'])
    current_user = request['current_user']
    data = await request.json()

    async with await db.get_session() as session:
        ad = await session.get(Advertisement, ad_id)
        if not ad:
            raise web.HTTPNotFound()

        if ad.owner_id != current_user.id:
            return web.json_response({'error': 'Permission denied'}, status=403)

        ad.title = data.get('title', ad.title)
        ad.description = data.get('description', ad.description)
        await session.commit()

    return web.json_response({'message': 'Advertisement updated'})


async def delete_advertisement(request):
    ad_id = int(request.match_info['ad_id'])
    current_user = request['current_user']

    async with await db.get_session() as session:
        ad = await session.get(Advertisement, ad_id)
        if not ad:
            raise web.HTTPNotFound()

        if ad.owner_id != current_user.id:
            return web.json_response({'error': 'Permission denied'}, status=403)

        await session.delete(ad)
        await session.commit()

    return web.json_response({'message': 'Advertisement deleted'})

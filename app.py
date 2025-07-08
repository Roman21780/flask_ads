from aiohttp import web
from routes import setup_routes
from auth import auth_middleware
from database import db
import argparse
import asyncio


async def init_app():
    app = web.Application(middlewares=[auth_middleware])

    # Инициализация базы данных
    await db.init()

    # Регистрация маршрутов
    setup_routes(app)

    # Очистка при завершении
    app.on_cleanup.append(db.close)

    return app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000, help='Port to run on')
    args = parser.parse_args()

    # Создаем event loop и запускаем приложение
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        app = loop.run_until_complete(init_app())
        web.run_app(app, port=args.port)
    finally:
        loop.close()


if __name__ == '__main__':
    main()
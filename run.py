import asyncio

from src.core import create_app


async def main() -> None:
    app = await create_app()
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())

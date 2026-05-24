"""Entry point for `python -m camarilla`."""

import asyncio

from camarilla.bot.main import main

if __name__ == "__main__":
    asyncio.run(main())

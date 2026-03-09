"""WestGame AI 全自动化团战系统 — 入口"""

import asyncio

from src.controller.loop import AIController


async def main():
    controller = AIController()
    await controller.run_loop()


if __name__ == "__main__":
    asyncio.run(main())

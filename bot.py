import os
import asyncio
import discord
from discord.ext import commands
from cogwatch import watch
from config import VERSION, DISCORD_API_TOKEN

class PACBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!')
        for filename in os.listdir("commands"):
            if filename.endswith(".py"):
                self.load_extension(f"commands.{filename[:-3]}")

    @watch(path='commands')
    async def on_ready(self):
        print(f'{self.user.name} v{VERSION} 연결')
        await self.change_presence(status=discord.Status.online, activity=None)
        #await ctx.send(f'출석봇 출석\n현재 버전: v{VERSION}')

    async def on_message(self, message):
        if message.author.bot:
            return

        await self.process_commands(message)

async def main():
    client = PACBot()
    await client.start(DISCORD_API_TOKEN)

if __name__ == '__main__':
    asyncio.run(main())

import discord
from discord.ext import commands
from config import Token

bot=commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f"봇 {bot.user.name} 연결")
    await bot.change_presence(status=discord.Status.online, activity=None)

@bot.command()
async def 출석체크(ctx):
    try:
        if ctx.author.voice is None:
            await ctx.send('음성채널에 접속한 후 사용해 주세요. :grinning:')
        else:
            channel = ctx.author.voice.channel
            members = ', '.join([x.name for x in channel.members])
            if len(channel.members) == 0:
                await ctx.send(f'**출석자 명단**\n- 없음')
            else:
                await ctx.send(f'**출석자 명단** ({len(channel.members)}명)\n>>> {members}')
    except:
            await ctx.send('오류가 발생했습니다. :disappointed_relieved:')

'''@bot.command()
async def 테스트(ctx):
    print(ctx.author.voice.channel.members)
    await ctx.send(ctx.author.voice.channel.members)
    

@bot.command()
async def 퇴장(ctx):
    await ctx.voice_client.disconnect()'''

bot.run(Token)

from discord.ext import commands
from members import Members
import time
import random

class Seminar(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command(name='세미나')
    async def seminar(self, ctx, part=None, number=None):
        await ctx.send('아직 사용할 수 없는 기능입니다.')
        return

        try:
            if ctx.author.voice is None:
                await ctx.send('음성채널에 접속한 후 사용해 주세요. :grinning:')
                return

            # 세미나 대상자 명단
            targets = Members.get_seminar_targets(part)
            num_targets = len(targets)
            if part is not None and len(targets) == 0:
                await ctx.send(f'`{part}` 소속 파트원을 찾을 수 없습니다.')
                return
            await ctx.send(f'세미나 대상자 수: {num_targets}명')
            
            # 출석자 명단
            attendees = Members.get_attendees(ctx)

            # 선발
            if number is None:
                number = random.randrange(0, len(targets))
            elif int(number)-1 not in range(0, len(targets)):
                await ctx.send(f'1~{num_targets}에 해당하는 번호를 입력해 주십시오.')
                return
            target = targets[int(number)]

            # 출력
            target_name = target['name']
            await ctx.send(f'세미나 발표자: {target_name}')
        except Exception as e:
            print(e)
            await ctx.send('오류가 발생했습니다. :disappointed_relieved:')

def setup(client):
    client.add_cog(Seminar(client))
    print('명령어 클래스 로드: Seminar')

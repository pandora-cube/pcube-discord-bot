from discord.ext import commands
from members import Members

class AttendanceCheck(commands.Cog):
    def __init__(self, client):
        self.client = client

    '''@commands.command(name='출석체크(구)')
    async def pacheck_old(self, ctx):
        try:
            if ctx.author.voice is None:
                await ctx.send('음성채널에 접속한 후 사용해 주세요. :grinning:')
            else:
                channel = ctx.author.voice.channel
                members = ', '.join([x.nick for x in channel.members])
                if len(channel.members) == 0:
                    await ctx.send(f'**출석자 명단**\n- 없음')
                else:
                    await ctx.send(f'**출석자 명단** ({len(channel.members)}명)\n>>> {members}')
        except:
            await ctx.send('오류가 발생했습니다. :disappointed_relieved:')'''
    
    @commands.command(name='출석체크')
    async def pacheck(self, ctx, part=None):
        try:
            if ctx.author.voice is None:
                await ctx.send('음성채널에 접속한 후 사용해 주세요. :grinning:')
                return
            
            # 출석 대상자 명단
            targets = Members.get_attendance_targets(part)
            if part is not None and len(targets) == 0:
                await ctx.send(f'`{part}` 소속 파트원을 찾을 수 없습니다.')
                return

            # 출석자 명단
            attendees = Members.get_attendees(ctx)
            ex_attendees = [x for x in attendees if x not in [y['name'] for y in targets]]

            # 출력
            part_text = ''
            if part is not None:
                part_text = f'{part} 파트 '

            if len(attendees) == 0:
                row = f'**{part_text}출석자 명단**\n- 없음'
                await ctx.send(row)
                return
            
            row = f'**{part_text}출석자 명단** ({len(attendees)}명)\n'
            row += textwrap('회원구분', 4) + '　|　'
            row += textwrap('이름', 4) + '　|　'
            row += textwrap('참석', 2) + '　|　'
            row += textwrap('불참', 2) + '　|　'
            row += '비고'
            await ctx.send(row)

            buffer = ''
            for member in targets:
                attended = not_attended = '　'
                if member['name'] in attendees:
                    attended = '○'
                else:
                    not_attended = '○'
                
                etc = ''
                if member['grade'] >= 4:
                    etc = '4학년'
                
                row = ''
                row += textwrap(member['rank'], 4) + '　|　'
                row += textwrap(member['name'], 4) + '　|　'
                row += textwrap(attended, 2) + '　|　'
                row += textwrap(not_attended, 2) + '　|　'
                row += etc + '\n'
                
                if len(buffer+row) >= 2000:
                    await ctx.send(buffer)
                    buffer = row
                else:
                    buffer += row
            
            if len(buffer) > 0:
                await ctx.send(buffer)
            
            if len(ex_attendees) > 0:
                buffer = f'기타 출석자: '
                buffer += ', '.join(ex_attendees)
                await ctx.send(buffer)
            
            await ctx.send(f'{part_text}출석체크 완료')
        except Exception as e:
            print(e)
            await ctx.send('오류가 발생했습니다. :disappointed_relieved:')

def setup(client):
    client.add_cog(AttendanceCheck(client))
    print('명령어 클래스 로드: AttendanceCheck')

def textwrap(text, width):
    result = text
    for i in range(width-len(text)):
        result += '　'
    return result

from discord.ext import commands
from notion import NotionDatabase

class PACheck(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='출석체크(구)')
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
            await ctx.send('오류가 발생했습니다. :disappointed_relieved:')
    
    @commands.command(name='출석체크')
    async def pacheck(self, ctx, part=None):
        try:
            if ctx.author.voice is None:
                await ctx.send('음성채널에 접속한 후 사용해 주세요. :grinning:')
                return
            
            # 출석 대상자 명단
            target_ranks = ['정회원', '수습회원']
            filter = {'or': [{'property': '분류', 'select': {'equals': rank}} for rank in target_ranks]}
            if part is not None:
                filter = {
                    'and': [
                        {
                            'property': '파트',
                            'select': {
                                'equals': part
                            }
                        },
                        { 'or': filter['or'] }
                    ]
                }

            db = NotionDatabase('920603e8762a4daebe53ff72e9e8a83e', filter)
            all_members = [
                {
                    'name': member['properties']['이름']['title'][0]['plain_text'],
                    'rank': member['properties']['분류']['select']['name'],
                    'grade': member['properties']['학년']['number']
                }
                for member in db.data
                if member['properties']['분류']['select']['name'] in target_ranks
            ]
            all_members = sorted(all_members, key=lambda x: (x['rank'], x['name']))

            if part is not None and len(all_members) == 0:
                await ctx.send(f'`{part}` 소속 파트원을 찾을 수 없습니다.')
                return

            # 출석자 명단
            channel = ctx.author.voice.channel
            attended_members = [x.name for x in channel.members]
            print(attended_members)

            # 출력
            part_text = ''
            if part is not None:
                part_text = f'{part} 파트 '

            if len(channel.members) == 0:
                row = f'**{part_text}출석자 명단**\n- 없음'
                await ctx.send(row)
                return
            
            row = f'**{part_text}출석자 명단**\n'
            row += textwrap('회원구분', 4) + '　|　'
            row += textwrap('이름', 4) + '　|　'
            row += textwrap('참석', 2) + '　|　'
            row += textwrap('불참', 2) + '　|　'
            row += '비고'
            await ctx.send(row)

            result = ''
            for member in all_members:
                attended = not_attended = '　'
                if member['name'] in attended_members:
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
                
                if len(result+row) >= 2000:
                    await ctx.send(result)
                    result = row
                else:
                    result += row
            
            if len(result) > 0:
                await ctx.send(result)
            await ctx.send(f'{part_text}출석체크 완료')
        except Exception as e:
            print(e)
            await ctx.send('오류가 발생했습니다. :disappointed_relieved:')

def setup(client):
    client.add_cog(PACheck(client))
    print('명령어 클래스 로드: PACheck')

def textwrap(text, width):
    result = text
    for i in range(width-len(text)):
        result += '　'
    return result

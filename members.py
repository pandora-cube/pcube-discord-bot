from notion import NotionDatabase
import re
from config import NOTION_DB

class Members():
    @classmethod
    def get_attendance_targets(self, part=None):
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

        db = NotionDatabase(NOTION_DB['MEMBER_LIST'], filter)
        targets = [
            {
                'name': member['properties']['이름']['title'][0]['plain_text'],
                'rank': member['properties']['분류']['select']['name'],
                'grade': member['properties']['학년']['number']
            }
            for member in db.data
            if member['properties']['분류']['select']['name'] in target_ranks
        ]
        targets = sorted(targets, key=lambda x: (x['rank'], x['name']))

        return targets
    
    @classmethod
    def get_attendees(self, ctx):
        channel = ctx.author.voice.channel
        attendees = [self.parse_name(x.nick or x.name) for x in channel.members]
        return attendees
    
    def parse_name(nickname):
        regex = re.compile('[\[|\(|\<](.*?)[\]|\)|\>]')
        search = regex.search(nickname)

        if search is not None:
            name = search.group()[1:-1]
        else:
            name = nickname

        return name

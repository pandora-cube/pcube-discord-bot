from notion import NotionDatabase
import re
from config import NOTION_DB

class Members():
    @classmethod
    def get_attendance_targets(self, part=None):
        target_ranks = ['정회원', '수습회원']
        filter = self.filter(ranks=target_ranks, part=part)

        db = NotionDatabase(NOTION_DB['MEMBER_LIST'], filter)
        targets = [
            {
                'name': member['properties']['이름']['title'][0]['plain_text'],
                'rank': member['properties']['분류']['select']['name'],
                'grade': member['properties']['학년']['number'],
                'reason': member['properties']['정기적불참사유']['rich_text'][0]['plain_text']
            }
            for member in db.data
        ]
        targets = sorted(targets, key=lambda x: (x['rank'], x['name']))

        return targets
    
    @classmethod
    def get_seminar_targets(self, part=None):
        target_ranks = ['정회원', '수습회원']
        filter = self.filter(ranks=target_ranks, part=part, seminar=True)

        db = NotionDatabase(NOTION_DB['MEMBER_LIST'], filter)
        targets = [
            {
                'name': member['properties']['이름']['title'][0]['plain_text'],
                'rank': member['properties']['분류']['select']['name'],
                'recent': self.parse_date(member['properties']['최근 세미나 일자']['date']),
            }
            for member in db.data
            if not (
                member['properties']['분류']['select']['name'] == '정회원'
                and member['properties']['학년']['number'] >= 4
            )
        ]
        targets = sorted(targets, key=lambda x: (x['recent'], x['name']))

        return targets

    @classmethod
    def get_attendees(self, ctx):
        channel = ctx.author.voice.channel
        attendees = [self.parse_name(x.nick or x.name) for x in channel.members]
        return attendees
    
    def filter(ranks=None, part=None, seminar=None):
        # 기본값, 모든 항목에 해당하는 조건
        filter_default = { 'property': '이름', 'rich_text': { 'is_not_empty': True } }
        filter_rank = filter_default.copy()
        filter_part = filter_default.copy()
        filter_seminar = filter_default.copy()

        # 분류
        if ranks is not None:
            filter_rank = {
                'or': [
                    {'property': '분류', 'select': {'equals': rank}}
                    for rank in ranks
                ]
            }
        
        # 파트
        if part is not None:
            filter_part = {
                'property': '파트',
                'select': {
                    'equals': part
                }
            }

        # 정기적불참사유
        if seminar:
            filter_seminar = {
                'property': '정기적불참사유',
                'rich_text': {
                    'is_empty': True
                }
            }
        
        return {
            'and': [
                filter_rank,
                filter_part,
                filter_seminar,
            ]
        }

    def parse_name(nickname):
        regex = re.compile('[\[|\(|\<](.*?)[\]|\)|\>]')
        search = regex.search(nickname)

        if search is not None:
            name = search.group()[1:-1]
        else:
            name = nickname

        return name
    
    def parse_date(date):
        if not date:
            return '없음'
        elif date['end']:
            return date['end']
        elif date['start']:
            return date['start']
        return '없음'

from notion import NotionDatabase

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

        db = NotionDatabase('920603e8762a4daebe53ff72e9e8a83e', filter)
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
        attendees = [x.name for x in channel.members]
        return attendees

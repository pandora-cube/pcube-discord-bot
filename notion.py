import requests
import json
from config import NOTION_API_SECRET_TOKEN

api_url = 'https://api.notion.com/v1/{api}'
api_version = '2022-02-22'

headers = {
    'Authorization': f'Bearer {NOTION_API_SECRET_TOKEN}',
    'Content-Type': 'application/json',
    'Notion-Version': api_version,
}

class NotionData():
    def __init__(self, properties):
        self.properties = properties
    
    def get_database_id(self, field):
        rich_text = self.properties[field]

        for item in rich_text['rich_text']:
            if 'mention' not in item:
                continue
            if item['mention']['type'] != 'database':
                continue
            return item['mention']['database']['id']
        return None

    def multi_select_to_list(self, field):
        return [x['name'] for x in self.properties[field]['multi_select']]

    def rich_text_to_str(self, field):
        if len(self.properties[field]['rich_text']) == 0:
            return ''
        return self.properties[field]['rich_text'][0]['plain_text']

    def rich_text_to_json(self, field):
        text = self.rich_text_to_str(field)
        
        if len(text) == 0:
            return None
        return json.loads(text)

class NotionDatabase():
    def __init__(self, id, filter=None, sorts=None):
        params = {}
        if filter is not None:
            params['filter'] = filter
        if sorts is not None:
            params['sorts'] = sorts
        
        self.id = id
        self.data = self.get_all(id, params)
    
    def get_all(self, id, params):
        data = { 'has_more': True }

        results = []
        while data['has_more']:
            if 'next_cursor' in data and data['next_cursor']:
                params['start_cursor'] = data['next_cursor']
            
            response = requests.post(
                url=api_url.format(api=f'databases/{id}/query'),
                headers=headers,
                data=json.dumps(params, ensure_ascii=False).encode('utf-8'))
            
            data = response.json()
            results.extend(data['results'])
        
        return results
    
    def push(self, data):
        properties = data['properties']

        # 불용값 제거
        for key, prop in properties.items():
            if 'id' in prop:
                del(prop['id'])

            value = prop[prop['type']]
            if type(value) == list:
                for item in value:
                    if 'id' in item:
                        del(item['id'])
            elif type(value) == dict and 'id' in value:
                del(value['id'])

        params = {
            'parent': { 'database_id': self.id },
            'properties': properties,
            #'children': data['children'],
            'icon': data['icon'],
            'cover': data['cover']
        }

        response = requests.post(
            url=api_url.format(api='pages'),
            headers=headers,
            data=json.dumps(params))
        
        '''print('')
        print('데이터 삽입')
        print('삽입 요청 파라미터:', json.dumps(params))
        print('삽입 요청 결과:', response.json())'''
    
    def get_properties(self):
        response = requests.get(
            url=api_url.format(api=f'databases/{self.id}'),
            headers=headers)
        return response.json()['properties']
    
    def set_properties(self, properties, fields):
        properties_ = properties
        for key in list(properties_.keys()):
            if key not in fields:
                del(properties_[key])
    
        params = {
            'properties': properties_
        }

        response = requests.patch(
            url=api_url.format(api=f'databases/{self.id}'),
            headers=headers,
            data=json.dumps(params))
        
        '''print('')
        print('필드 동기화')
        print('동기화 결과:', response.json())'''
    
    def filter_fields(self, fields):
        for item in self.data:
            for key in list(item['properties'].keys()):
                if key not in fields:
                    del(item['properties'][key])
    
    def sync(self, origin_col, destination_col, filter_col, sorts_col):
        row = 0
        link_data = NotionData(self.data[row]['properties'])

        origin_db_id = link_data.get_database_id(origin_col)
        destination_db_id = link_data.get_database_id(destination_col)
        filter = link_data.rich_text_to_json(filter_col)
        sorts = link_data.rich_text_to_json(sorts_col)

        origin_db = NotionDatabase(origin_db_id, filter=filter)
        destination_db = NotionDatabase(destination_db_id)
        
        fields = list(destination_db.get_properties().keys())
        origin_db.filter_fields(fields)
        destination_db.set_properties(origin_db.get_properties(), fields)

        for origin_data in origin_db.data:
            destination_db.push(origin_data)

        self.origin_db = origin_db
        self.destination_db = destination_db
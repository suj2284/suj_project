import json

# Json 컨버팅
class Converting:
    def __init__(self):
        pass

    def to_json(self, data, file_name):
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent='\t')

    def call_json(self, file_name):
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)

        return data

import json

try:
    with open('data/faq.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f'JSON is valid! Total entries: {len(data)}')
except Exception as e:
    print(f'JSON validation error: {e}')
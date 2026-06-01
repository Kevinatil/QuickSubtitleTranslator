import os
import json


def get_llm_config(model):
    with open(os.path.join('llm_api', 'api_keys.json'), 'r', encoding='utf-8') as f:
        keys = json.load(f)
    return keys['llm'][model]

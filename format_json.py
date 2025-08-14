import os
import json

def format_json_file(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        obj = json.load(f)
    # 保证所有规则字段都是数组格式
    if isinstance(obj, dict) and 'rules' in obj and isinstance(obj['rules'], list):
        for rule in obj['rules']:
            for key in list(rule.keys()):
                # 跳过空值
                if rule[key] is None:
                    continue
                # 如果不是数组，转为数组
                if not isinstance(rule[key], list):
                    rule[key] = [rule[key]]
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

for root, dirs, files in os.walk('sing-box'):
    for file in files:
        if file.endswith('.json'):
            json_path = os.path.join(root, file)
            print(f'格式化 {json_path}')
            format_json_file(json_path)

print('全部格式化完成')
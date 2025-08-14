import os
import subprocess
import yaml
import json
from collections import defaultdict

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def yaml_to_json_rule(yaml_path, json_path):
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    # 分类
    rule = defaultdict(list)
    for item in data.get('payload', []):
        if isinstance(item, str):
            if ',' not in item:
                rule['ip_cidr'].append(item)
            elif item.startswith('DOMAIN-SUFFIX,'):
                rule['domain_suffix'].append(item.split(',', 1)[1])
            elif item.startswith('DOMAIN,'):
                rule['domain'].append(item.split(',', 1)[1])
            elif item.startswith('DOMAIN-REGEX,'):
                rule['domain_regex'].append(item.split(',', 1)[1])
            # 可扩展更多类型
    json_obj = {
        "version": 3,
        "rules": [dict(rule)]
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_obj, f, ensure_ascii=False, indent=2)

# 处理 mihomo 目录下所有子目录的 *-ip.yaml 和 *-site.yaml 文件，转json到 sing-box 下对应目录
for root, dirs, files in os.walk('mihomo'):
    rel_dir = os.path.relpath(root, 'mihomo')
    singbox_target_dir = os.path.join('sing-box', rel_dir)
    ensure_dir(singbox_target_dir)
    for file in files:
        if file.endswith('-ip.yaml') or file.endswith('-site.yaml'):
            yaml_path = os.path.join(root, file)
            json_path = os.path.join(singbox_target_dir, os.path.splitext(file)[0] + '.json')
            print(f'正在将 {yaml_path} 转换为 {json_path}')
            yaml_to_json_rule(yaml_path, json_path)

# 处理 sing-box 目录下所有子目录的 .json 文件，转为 srs
for root, dirs, files in os.walk('sing-box'):
    for file in files:
        if file.endswith('.json'):
            json_path = os.path.join(root, file)
            print(f'正在转换 {json_path} 为 srs')
            subprocess.run(['sing-box.exe', 'rule-set', 'compile', json_path])

print('全部转换完成')
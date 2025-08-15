import os
import subprocess
import sys
import yaml
import json
from collections import defaultdict

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# 自动适配可执行文件名
mihomo_bin = 'mihomo.exe' if os.name == 'nt' else './mihomo'
singbox_bin = 'sing-box.exe' if os.name == 'nt' else './sing-box'

def yaml_to_json_rule(yaml_path, json_path):
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    # 分类
    rule = defaultdict(list)
    for item in data.get('payload', []):
        if isinstance(item, str):
            if ',' not in item:
                rule['ip_cidr'].append(item)
            elif item.startswith('DOMAIN,'):
                rule['domain'].append(item.split(',', 1)[1])    
            elif item.startswith('DOMAIN-SUFFIX,'):
                rule['domain_suffix'].append(item.split(',', 1)[1])
            elif item.startswith('DOMAIN-KEYWORD,'):
                rule['domain_keyword'].append(item.split(',', 1)[1]) 
            elif item.startswith('DOMAIN-REGEX,'):
                rule['domain_regex'].append(item.split(',', 1)[1])  
            # 可扩展更多类型
    json_obj = {
        "version": 3,
        "rules": [dict(rule)]
    }
    with open(json_path, 'w', encoding='utf-8', newline='\n') as f:
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
            subprocess.run([singbox_bin, 'rule-set', 'compile', json_path])

# mihomo下所有*-ip.yaml转为*-ip.mrs
for root, dirs, files in os.walk('mihomo'):
    for file in files:
        if file.endswith('-ip.yaml'):
            yaml_path = os.path.join(root, file)
            mrs_path = os.path.join(root, os.path.splitext(file)[0] + '.mrs')
            print(f'正在将 {yaml_path} 转换为 {mrs_path}')
            # 读取 yaml，写回时强制 LF
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = f.read()
            # 替换所有 CRLF 为 LF
            data = data.replace('\r\n', '\n')
            with open(yaml_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(data)
            subprocess.run([mihomo_bin, 'convert-ruleset', 'ipcidr', 'yaml', yaml_path, mrs_path])

print('全部转换完成')
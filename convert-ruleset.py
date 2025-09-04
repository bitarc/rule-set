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

def enforce_yaml_lf(yaml_path):
    """
    读取 yaml 文件，格式化为标准 yaml（缩进2空格，block风格，顺序不变，换行符LF），覆盖写回。
    """
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    class IndentDumper(yaml.SafeDumper):
        def increase_indent(self, flow=False, indentless=False):
            return super().increase_indent(flow, False)

    with open(yaml_path, 'w', encoding='utf-8', newline='\n') as f:
        yaml.dump(
            data,
            f,
            allow_unicode=True,
            indent=2,
            default_flow_style=False,
            sort_keys=False,
            width=4096,
            Dumper=IndentDumper,
            line_break='\n'
        )


# 1. 先递归格式化 mihomo 下所有 *-ip.yaml、*-site.yaml 和 *-site-classical.yaml 文件为标准 yaml
for root, dirs, files in os.walk('mihomo'):
    for file in files:
        # 支持大小写混合的后缀
        if file.lower().endswith(('-ip.yaml', '-site.yaml', '-site-classical.yaml')):
            yaml_path = os.path.join(root, file)
            print(f'格式化 {yaml_path} 为标准 yaml')
            enforce_yaml_lf(yaml_path)

# 2. 处理 mihomo 目录下所有子目录的 *-ip.yaml 和 *-site-classical.yaml 文件，转json到 sing-box 下对应目录
for root, dirs, files in os.walk('mihomo'):
    rel_dir = os.path.relpath(root, 'mihomo')
    singbox_target_dir = os.path.join('sing-box', rel_dir)
    ensure_dir(singbox_target_dir)
    for file in files:
        if file.endswith('-ip.yaml') or file.endswith('-site-classical.yaml'):
            yaml_path = os.path.join(root, file)
            # 如果是 *-site-classical.yaml，则生成 *-site.json（去掉 classical）
            if file.lower().endswith('-site-classical.yaml'):
                prefix = file[:-len('-site-classical.yaml')]
                json_name = prefix + '-site.json'
            else:
                json_name = os.path.splitext(file)[0] + '.json'
            json_path = os.path.join(singbox_target_dir, json_name)
            print(f'正在将 {yaml_path} 转换为 {json_path}')
            yaml_to_json_rule(yaml_path, json_path)

# 处理 sing-box 目录下所有子目录的 .json 文件，转为 srs
for root, dirs, files in os.walk('sing-box'):
    for file in files:
        if file.endswith('.json'):
            json_path = os.path.join(root, file)
            print(f'正在转换 {json_path} 为 srs')
            subprocess.run([singbox_bin, 'rule-set', 'compile', json_path])


# 3. mihomo下所有*-ip.yaml转为*-ip.mrs（此处不再调用 enforce_yaml_lf，直接用格式化后的 yaml）
for root, dirs, files in os.walk('mihomo'):
    for file in files:
        # 转换 *-ip.yaml 和 *-site.yaml（跳过 *-site-classical.yaml），后缀匹配不区分大小写
        lname = file.lower()
        if lname.endswith('-ip.yaml') or (lname.endswith('-site.yaml') and not lname.endswith('-site-classical.yaml')):
            yaml_path = os.path.join(root, file)
            mrs_path = os.path.join(root, os.path.splitext(file)[0] + '.mrs')
            # ip -> ipcidr, site -> domain
            mode = 'ipcidr' if lname.endswith('-ip.yaml') else 'domain'
            print(f'正在将 {yaml_path} 转换为 {mrs_path} (mode={mode})')
            subprocess.run([mihomo_bin, 'convert-ruleset', mode, 'yaml', yaml_path, mrs_path])

print('全部转换完成')
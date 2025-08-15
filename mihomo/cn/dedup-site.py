# 支持 YAML 文件去重、格式化、修复格式错误

import yaml

def fix_payload_indent(input_path, temp_path):
    """
    自动修复 payload 下所有 - 的缩进为2空格，消除缩进混乱。
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    fixed = []
    in_payload = False
    for line in lines:
        if line.strip().startswith('payload:'):
            in_payload = True
            fixed.append('payload:\n')
            continue
        if in_payload:
            if line.strip().startswith('- '):
                # 统一2空格缩进
                fixed.append('  - ' + line.strip()[2:] + '\n' if not line.startswith('  - ') else line)
            elif line.strip() == '' or line.strip().startswith('#'):
                fixed.append(line)
            else:
                in_payload = False
                fixed.append(line)
        else:
            fixed.append(line)

    with open(temp_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed)

def load_yaml_with_repair(path):
    """
    尝试多种方式加载 YAML，遇到格式错误自动修复常见问题。
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        # 尝试修复缩进、tab、非法字符等
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # 替换 tab 为空格
        lines = [line.replace('\t', '  ') for line in lines]
        # 去除行尾多余空格
        lines = [line.rstrip() + '\n' for line in lines]
        # 重新写入临时文件
        temp_path = path + '.tmp2'
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        with open(temp_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data

def dedup_and_format_yaml(input_path, output_path):
    # 先修复 payload 缩进
    temp_path = input_path + '.fixed'
    fix_payload_indent(input_path, temp_path)
    # 再尝试加载和去重
    data = load_yaml_with_repair(temp_path)
    if not data or 'payload' not in data:
        print('payload 字段不存在或文件内容为空')
        return
    seen = set()
    str_items = []
    other_items = []
    for item in data['payload']:
        if isinstance(item, str):
            if item not in seen:
                seen.add(item)
                str_items.append(item)
        else:
            other_items.append(item)
    # 排序：DOMAIN 在前，DOMAIN-SUFFIX 在后
    def sort_key(x):
        if x.startswith('DOMAIN,'):
            return (0, x)
        elif x.startswith('DOMAIN-SUFFIX,'):
            return (1, x)
        else:
            return (2, x)
    str_items_sorted = sorted(str_items, key=sort_key)
    data['payload'] = str_items_sorted + other_items
    with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
        yaml.dump(
            data,
            f,
            allow_unicode=True,
            sort_keys=False,
            indent=2,
            default_flow_style=False
        )

if __name__ == '__main__':
    dedup_and_format_yaml('cn-site.yaml', 'cn-site.yaml')
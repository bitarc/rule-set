import os
import sys
import yaml
import shutil

TEMPLATE_FILE = 'cn-site-classical.yaml'  # 默认模板文件名，可修改

def load_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def find_missing(a, b, path=None):
    """
    返回a中不被b包含的所有路径和内容
    """
    if path is None:
        path = []
    missing = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k, v in a.items():
            if k not in b:
                missing.append(('.'.join(path + [str(k)]), v))
            else:
                missing.extend(find_missing(v, b[k], path + [str(k)]))
    elif isinstance(a, list) and isinstance(b, list):
        for idx, item_a in enumerate(a):
            if not any(is_subset(item_a, item_b) for item_b in b):
                missing.append(('.'.join(path + [f'[{idx}]']), item_a))
    else:
        if a != b:
            missing.append(('.'.join(path), a))
    return missing

def is_subset(a, b):
    return not find_missing(a, b)


def merge_into_template(template, other):
    """
    把 other 中缺失的项合并进 template（就地修改 template），不会覆盖已存在的值。
    返回 True 如果 template 被修改过。
    """
    changed = False
    if other is None:
        return False

    # dict 合并
    if isinstance(other, dict):
        if template is None or not isinstance(template, dict):
            # 无法就地修改非 dict 的 template
            return False
        for k, v in other.items():
            if k not in template:
                template[k] = v
                changed = True
            else:
                # 递归合并
                if isinstance(v, dict) and isinstance(template[k], dict):
                    if merge_into_template(template[k], v):
                        changed = True
                elif isinstance(v, list) and isinstance(template[k], list):
                    for item in v:
                        if not any(is_subset(item, existing) for existing in template[k]):
                            template[k].append(item)
                            changed = True
                else:
                    # 标量或类型不匹配，不覆盖
                    pass

    # list 合并（把 other 中不在 template 的条目追加）
    elif isinstance(other, list):
        if template is None or not isinstance(template, list):
            return False
        for item in other:
            if not any(is_subset(item, existing) for existing in template):
                template.append(item)
                changed = True

    # 标量：不覆盖已有值
    else:
        # 如果 template 是 None，可以由调用方直接赋值；这里不处理标量覆盖
        return False

    return changed

if __name__ == "__main__":
    # 支持命令行参数指定模板文件名
    template_file = sys.argv[1] if len(sys.argv) > 1 else TEMPLATE_FILE
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(current_dir, template_file)

    # 如果模板不存在，先创建一个空的 dict 模板，避免报错
    if not os.path.exists(template_path):
        print(f"模板文件 {template_file} 不存在，创建空模板...")
        with open(template_path, 'w', encoding='utf-8') as tf:
            yaml.safe_dump({}, tf, allow_unicode=True, sort_keys=False)

    template = load_yaml(template_path)
    if template is None:
        template = {}
    for filename in os.listdir(current_dir):
        # 跳过模板文件以及不需要处理的两个文件 cn-site.yaml 和 cn-ip.yaml
        if filename.endswith('.yaml') and filename not in (template_file, 'cn-site.yaml', 'cn-ip.yaml'):
            file_path = os.path.join(current_dir, filename)
            try:
                data = load_yaml(file_path)
                if data is None:
                    print(f"{filename}: 内容为空，跳过")
                    continue

                missing = find_missing(data, template)
                if not missing:
                    print(f"{filename}: 全部包含在 {template_file} 中")
                else:
                    print(f"{filename}: 未全部包含在 {template_file} 中，缺失条目:")
                    for path, value in missing:
                        print(f"  - {path}: {value}")

                    # 把缺失的规则合并到模板中（去重），不覆盖已有值
                    merged = merge_into_template(template, data)
                    if merged:
                        print(f"  -> 已把 {filename} 中缺失的条目合并到 {template_file}")
            except Exception as e:
                print(f"{filename}: 解析失败 - {e}")

    # 在处理完全部文件后，写回模板（备份原模板）
    try:
        backup_path = template_path + '.bak'
        shutil.copy2(template_path, backup_path)
        with open(template_path, 'w', encoding='utf-8') as tf:
            yaml.safe_dump(template, tf, allow_unicode=True, sort_keys=False)
        print(f"已备份原模板为: {backup_path}")
        print(f"已更新模板: {template_path}")
    except Exception as e:
        print(f"写回模板失败: {e}")


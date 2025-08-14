import os
import subprocess

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# 处理 mihomo 目录下所有子目录的 *-ip.yaml 和 *-site.yaml 文件，直接输出为 sing-box 下对应目录的 .json 文件
for root, dirs, files in os.walk('mihomo'):
    rel_dir = os.path.relpath(root, 'mihomo')
    singbox_target_dir = os.path.join('sing-box', rel_dir)
    ensure_dir(singbox_target_dir)
    for file in files:
        if file.endswith('-ip.yaml'):
            yaml_path = os.path.join(root, file)
            json_path = os.path.join(singbox_target_dir, os.path.splitext(file)[0] + '.json')
            mrs_path = os.path.join(root, os.path.splitext(file)[0] + '.mrs')
            print(f'正在将 {yaml_path} 转换为 {json_path} (ipcidr)')
            subprocess.run(['mihomo.exe', 'convert-ruleset', 'ipcidr', 'yaml', yaml_path, json_path])
            print(f'正在将 {yaml_path} 转换为 {mrs_path} (ipcidr)')
            subprocess.run(['mihomo.exe', 'convert-ruleset', 'ipcidr', 'yaml', yaml_path, mrs_path])
        elif file.endswith('-site.yaml'):
            yaml_path = os.path.join(root, file)
            json_path = os.path.join(singbox_target_dir, os.path.splitext(file)[0] + '.json')
            print(f'正在将 {yaml_path} 转换为 {json_path} (domain)')
            subprocess.run(['mihomo.exe', 'convert-ruleset', 'domain', 'yaml', yaml_path, json_path])
# 处理 sing-box 目录下所有子目录的 .json 文件
for root, dirs, files in os.walk('sing-box'):
    for file in files:
        if file.endswith('.json'):
            json_path = os.path.join(root, file)
            print(f'正在转换 {json_path}')
            subprocess.run(['sing-box.exe', 'rule-set', 'compile', json_path])
print('全部转换完成')
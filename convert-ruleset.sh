#!/usr/bin/sh
export LANG="en_US.UTF-8"

echo "===== 开始执行所有规则转换 ====="

# === 处理 sing-box 目录下所有子目录 ===
for d in sing-box/*/; do
    [ -d "$d" ] || continue
    for f in "$d"*.json; do
        [ -f "$f" ] || continue
        echo "正在转换 $f"
        ./sing-box rule-set compile "$f"
    done
done

# === 处理 mihomo 目录下所有子目录 ===
for d in mihomo/*/; do
    [ -d "$d" ] || continue
    for f in "$d"*-ip.yaml; do
        [ -f "$f" ] || continue
        echo "正在转换 $f 为 ipcidr"
        ./mihomo convert-ruleset ipcidr yaml "$f" "${f%.yaml}.mrs"
    done
    for f in "$d"*-site.yaml; do
        [ -f "$f" ] || continue
        echo "正在转换 $f 为 domain"
        ./mihomo convert-ruleset domain yaml "$f" "${f%.yaml}.mrs"
    done
done

echo "===== 所有转换操作已完成！ ====="
sleep 3
exit 0
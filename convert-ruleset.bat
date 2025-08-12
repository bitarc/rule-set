@echo off
chcp 65001 >nul

REM === 处理 sing-box 目录下所有子目录 ===
for /d %%d in (sing-box\*) do (
    for %%f in (%%d\*.json) do (
        echo 正在转换 %%f
        .\sing-box.exe rule-set compile "%%f"
    )
)

REM === 处理 mihomo 目录下所有子目录 ===
for /d %%d in (mihomo\*) do (
    for %%f in (%%d\*-ip.yaml) do (
        if exist "%%f" (
            echo 正在转换 %%f 为 ipcidr
            .\mihomo.exe convert-ruleset ipcidr yaml "%%f" "%%~dpnf.mrs"
        )
    )
    for %%f in (%%d\*-site.yaml) do (
        if exist "%%f" (
            echo 正在转换 %%f 为 domain
            .\mihomo.exe convert-ruleset domain yaml "%%f" "%%~dpnf.mrs"
        )
    )
)

echo 全部转换完成
timeout /t 3 >nul
exit
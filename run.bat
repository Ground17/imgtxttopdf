@echo off
chcp 65001 > nul
echo ====================================
echo 사진 PDF 출력기
echo ====================================
echo.
echo 프로그램을 실행합니다...
echo.

python main.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 오류가 발생했습니다.
    echo.
    echo 해결 방법:
    echo 1. Python이 설치되어 있는지 확인하세요.
    echo 2. 필요한 패키지를 설치하세요: pip install -r requirements.txt
    echo.
    pause
)

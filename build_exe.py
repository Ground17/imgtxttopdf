"""
PyInstaller를 사용하여 실행 파일(.exe) 생성
"""
import os
import subprocess
import sys

def build_executable():
    """실행 파일 빌드"""
    print("=" * 60)
    print("사진 PDF 출력기 실행 파일 생성 중...")
    print("=" * 60)

    # PyInstaller 명령어
    command = [
        'pyinstaller',
        '--name=사진PDF출력기',
        '--windowed',  # 콘솔 창 숨기기
        '--onedir',  # 단일 폴더로 생성
        '--icon=NONE',  # 아이콘 없음 (원하면 .ico 파일 지정 가능)
        '--add-data=requirements.txt;.',
        '--clean',
        'main.py'
    ]

    try:
        # PyInstaller 실행
        print("\nPyInstaller 실행 중...")
        subprocess.run(command, check=True)

        print("\n" + "=" * 60)
        print("✅ 실행 파일 생성 완료!")
        print("=" * 60)
        print(f"\n실행 파일 위치: {os.path.abspath('dist/사진PDF출력기')}")
        print("\n사용 방법:")
        print("1. 'dist/사진PDF출력기' 폴더를 원하는 위치로 복사하세요.")
        print("2. '사진PDF출력기.exe' 파일을 더블클릭하여 실행하세요.")
        print("\n💡 팁: 바탕화면에 바로가기를 만들면 더 편리합니다!")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ 오류 발생: {e}")
        print("\n해결 방법:")
        print("1. PyInstaller가 설치되어 있는지 확인: pip install pyinstaller")
        print("2. 관리자 권한으로 실행해보세요.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # PyInstaller 설치 확인
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller가 설치되어 있지 않습니다.")
        print("설치 중...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)

    build_executable()

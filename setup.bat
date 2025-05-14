@echo off
setlocal

echo =====================================================
echo       페이지 오브젝트 생성기 설치 스크립트
echo =====================================================
echo.

REM Python 버전 확인
echo Python 버전 확인 중...
python --version 2>nul
if %ERRORLEVEL% neq 0 (
    echo 오류: Python을 찾을 수 없습니다. Python 3.8 이상을 설치해주세요.
    exit /b 1
)

REM Python 버전이 3.8 이상인지 확인
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"
if %ERRORLEVEL% neq 0 (
    echo 오류: Python 3.8 이상이 필요합니다.
    exit /b 1
)

echo Python 버전 확인 완료!

REM 가상환경 생성
echo 가상환경 생성 중...
python -m venv venv
if %ERRORLEVEL% neq 0 (
    echo 오류: 가상환경 생성에 실패했습니다.
    exit /b 1
)
echo 가상환경 생성 완료!

REM 가상환경 활성화
echo 가상환경 활성화 중...
call venv\Scripts\activate
if %ERRORLEVEL% neq 0 (
    echo 오류: 가상환경 활성화에 실패했습니다.
    exit /b 1
)
echo 가상환경 활성화 완료!

REM pip 업그레이드
echo pip 업그레이드 중...
python -m pip install --upgrade pip
if %ERRORLEVEL% neq 0 (
    echo 경고: pip 업그레이드에 실패했습니다. 계속 진행합니다.
)
echo pip 업그레이드 완료!

REM 패키지 설치
echo 필요한 패키지 설치 중...
pip install -e .
if %ERRORLEVEL% neq 0 (
    echo 오류: 패키지 설치에 실패했습니다.
    exit /b 1
)
echo 필요한 패키지 설치 완료!

REM .env 파일 설정 확인
echo .env 파일 확인 중...
if not exist .env (
    echo .env 파일이 없습니다. .env.example을 복사합니다...
    copy .env.example .env
    echo .env 파일 생성 완료! 필요한 정보를 입력해주세요.
) else (
    echo .env 파일이 이미 존재합니다.
)

echo.
echo =====================================================
echo       설치가 성공적으로 완료되었습니다!
echo =====================================================
echo.

echo 사용 방법:
echo 1. 가상환경 활성화: venv\Scripts\activate
echo 2. 프로그램 실행: python src\main.py --url https://example.com
echo 3. 또는 설치된 명령어 사용: po-generator --url https://example.com
echo.
echo Google Cloud Vision API 사용을 위해 .env 파일의 인증 정보를 설정해주세요.

endlocal
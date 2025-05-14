#!/bin/bash

# 가상환경 설정 및 패키지 설치 스크립트

# 색상 설정
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 로고 출력
echo -e "${BLUE}"
echo "====================================================="
echo "      페이지 오브젝트 생성기 설치 스크립트"
echo "====================================================="
echo -e "${NC}"

# 파이썬 버전 확인
echo -e "${YELLOW}Python 버전 확인 중...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
else
    echo -e "${RED}오류: Python을 찾을 수 없습니다. Python 3.8 이상을 설치해주세요.${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}오류: Python $REQUIRED_VERSION 이상이 필요합니다. 현재 버전: $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}Python $PYTHON_VERSION를 사용합니다.${NC}"

# 가상환경 생성
echo -e "${YELLOW}가상환경을 생성 중...${NC}"
$PYTHON_CMD -m venv venv
if [ $? -ne 0 ]; then
    echo -e "${RED}오류: 가상환경 생성에 실패했습니다.${NC}"
    exit 1
fi
echo -e "${GREEN}가상환경 생성 완료!${NC}"

# 가상환경 활성화
echo -e "${YELLOW}가상환경 활성화 중...${NC}"
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    source venv/bin/activate
    ACTIVATION_CMD="source venv/bin/activate"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
    ACTIVATION_CMD="venv\\Scripts\\activate"
else
    echo -e "${RED}오류: 알 수 없는 운영체제입니다.${NC}"
    exit 1
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}오류: 가상환경 활성화에 실패했습니다.${NC}"
    exit 1
fi
echo -e "${GREEN}가상환경 활성화 완료!${NC}"

# pip 업그레이드
echo -e "${YELLOW}pip 업그레이드 중...${NC}"
pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo -e "${RED}경고: pip 업그레이드에 실패했습니다. 계속 진행합니다.${NC}"
fi
echo -e "${GREEN}pip 업그레이드 완료!${NC}"

# 패키지 설치
echo -e "${YELLOW}필요한 패키지 설치 중...${NC}"
pip install -e .
if [ $? -ne 0 ]; then
    echo -e "${RED}오류: 패키지 설치에 실패했습니다.${NC}"
    exit 1
fi
echo -e "${GREEN}필요한 패키지 설치 완료!${NC}"

# .env 파일 설정 확인
echo -e "${YELLOW}.env 파일 확인 중...${NC}"
if [ ! -f .env ]; then
    echo -e "${YELLOW}.env 파일이 없습니다. .env.example을 복사합니다...${NC}"
    cp .env.example .env
    echo -e "${GREEN}.env 파일 생성 완료! 필요한 정보를 입력해주세요.${NC}"
else
    echo -e "${GREEN}.env 파일이 이미 존재합니다.${NC}"
fi

# 설치 완료 메시지
echo -e "${BLUE}"
echo "====================================================="
echo "      설치가 성공적으로 완료되었습니다!"
echo "====================================================="
echo -e "${NC}"

echo -e "${YELLOW}사용 방법:${NC}"
echo -e "1. 가상환경 활성화: ${GREEN}$ACTIVATION_CMD${NC}"
echo -e "2. 프로그램 실행: ${GREEN}python src/main.py --url https://example.com${NC}"
echo -e "3. 또는 설치된 명령어 사용: ${GREEN}po-generator --url https://example.com${NC}"
echo -e "\n${YELLOW}Google Cloud Vision API 사용을 위해 .env 파일의 인증 정보를 설정해주세요.${NC}"

exit 0
.PHONY: setup install clean test run

# 기본 목표
all: setup

# 가상환경 설정 및 패키지 설치
setup:
	@echo "가상환경 설정 및 패키지 설치 중..."
	@bash setup.sh

# 패키지만 설치 (가상환경이 이미 활성화된 경우)
install:
	@echo "패키지 설치 중..."
	pip install -e .

# 가상환경 및 생성된 파일 정리
clean:
	@echo "프로젝트 정리 중..."
	rm -rf venv
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf output/*
	find . -type d -name "__pycache__" -exec rm -rf {} +

# 테스트 실행
test:
	@echo "테스트 실행 중..."
	python -m unittest discover -s tests

# 프로그램 실행 (URL 인수 필요)
run:
	@if [ -z "$(url)" ]; then \
		echo "URL을 지정해주세요. 예: make run url=https://example.com"; \
		exit 1; \
	fi
	@echo "프로그램 실행 중... URL: $(url)"
	python src/main.py --url $(url)

# 도움말
help:
	@echo "사용 가능한 명령어:"
	@echo "  make setup    - 가상환경 설정 및 패키지 설치"
	@echo "  make install  - 패키지만 설치 (가상환경이 이미 활성화된 경우)"
	@echo "  make clean    - 가상환경 및 생성된 파일 정리"
	@echo "  make test     - 테스트 실행"
	@echo "  make run url=https://example.com - 지정된 URL에 대해 프로그램 실행"
	@echo "  make help     - 도움말 표시"
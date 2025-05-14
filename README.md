# 페이지 오브젝트 생성기 (PO Generator)

URL을 입력받아 웹페이지의 상호작용 요소를 자동으로 추출하고 Selenium 테스트를 위한 페이지 오브젝트 패턴의 함수를 자동으로 생성하는 도구입니다.

## 1. 주요 기능

- 웹페이지에서 버튼, 입력 필드, 체크박스, 선택 요소 등 자동 추출
- Google Cloud Vision OCR을 통한 이미지 버튼의 텍스트 인식
- XPath, ID, CSS 선택자 등 다양한 로케이터 자동 생성
- Selenium 웹드라이버 기반 페이지 오브젝트 패턴 클래스 자동 생성
- 다국어 요소 처리 (한글/영어 모두 지원)

## 2. 작동 원리

### 2.1 데이터 흐름

1. 사용자가 URL 제공
2. Selenium WebDriver가 페이지 로드
3. 상호작용 요소 추출 (버튼, 입력 필드, 체크박스 등)
4. 요소의 특성 분석 (텍스트, 속성, 위치 등)
5. 선택적 OCR 처리 (텍스트가 없는 이미지 버튼)
6. 최적의 로케이터 전략 결정
7. 페이지 오브젝트 클래스 코드 생성
8. 파일로 저장

### 2.2 코드 구조

```
po_generator/
├── src/                     # 소스 코드
│   ├── main.py              # 메인 실행 스크립트
│   ├── utils/               # 유틸리티 모듈
│   │   ├── web_scraper.py   # 웹 스크래핑 클래스
│   │   ├── ocr.py           # OCR 처리 클래스
│   │   └── po_generator.py  # 페이지 오브젝트 생성 클래스
│   └── templates/           # 템플릿
│       └── page_object_template.py  # 페이지 오브젝트 템플릿
├── tests/                   # 테스트 코드
├── venv/                    # 가상 환경 (git에서 제외됨)
├── .env                     # 환경 설정 (git에서 제외됨)
├── .env.example             # 환경 설정 예시
├── requirements.txt         # 의존성 정의
└── README.md                # 이 파일
```

## 3. 핵심 구성 요소 설명

### 3.1 WebScraper 클래스 (`web_scraper.py`)

웹페이지에서 상호작용 요소를 추출하는 클래스입니다.

- **핵심 기능:**
  - Selenium WebDriver를 사용하여 웹페이지 로드
  - 다양한 CSS 선택자와 XPath를 사용하여 상호작용 요소 추출
  - 요소의 속성 및 특성 정보 수집 (텍스트, ID, 클래스, 위치 등)
  - 요소 스크린샷 캡처 (OCR 처리용)

- **추출 가능한 요소:**
  - 버튼 (button 태그, input[type=button], [role=button], 클래스에 'btn' 포함된 요소 등)
  - 입력 필드 (text, password, email 등 다양한 input 요소)
  - 체크박스 및 라디오 버튼
  - 선택 요소 (select 태그)

- **로케이터 전략:**
  - ID 기반 (가장 우선시)
  - 이름(name) 기반
  - 텍스트 기반 XPath
  - CSS 선택자 기반

### 3.2 OCRProcessor 클래스 (`ocr.py`)

텍스트가 없거나 명확하지 않은 이미지 버튼에서 텍스트를 추출하는 클래스입니다.

- **핵심 기능:**
  - Google Cloud Vision API를 사용한 OCR 처리
  - 이미지에서 텍스트 인식 및 위치 정보 추출
  - 버튼 텍스트인지 판별하는 알고리즘

### 3.3 PageObjectGenerator 클래스 (`po_generator.py`)

추출된 요소 정보를 기반으로 Selenium 페이지 오브젝트 클래스를 생성하는 클래스입니다.

- **핵심 기능:**
  - 요소 유형에 따른 메서드 생성 (클릭, 입력, 선택 등)
  - 요소 식별을 위한 최적의 로케이터 전략 선택
  - 의미 있는 메서드 이름 생성
  - 주석 및 문서화 자동 생성

- **메서드 유형:**
  - `click_*`: 버튼 클릭 메서드
  - `enter_*`: 텍스트 입력 메서드
  - `select_*`: 체크박스/라디오/드롭다운 선택 메서드

- **이름 생성 전략:**
  - 요소의 텍스트 사용 (가장 우선)
  - placeholder, aria-label, title 등의 속성 사용
  - ID나 name 속성 사용
  - 한글 텍스트는 로마자 변환 또는 의미적 매핑 (로그인 → login)

### 3.4 메인 모듈 (`main.py`)

사용자 입력을 처리하고 전체 프로세스를 조정하는 모듈입니다.

- **핵심 기능:**
  - 명령줄 인수 파싱
  - 구성 요소 초기화 및 조정
  - 요소 추출 및 필터링 관리
  - 생성된 코드 파일 저장

- **사용자 옵션:**
  - `--url`: 페이지 오브젝트를 생성할 URL (필수)
  - `--output`: 출력 디렉토리 (기본값: "output")
  - `--no-ocr`: OCR 비활성화
  - `--max-elements`: 처리할 최대 요소 수
  - `--timeout`: 스크래핑 타임아웃 (초, 기본값: 60)
  - `--debug`: 디버그 모드 활성화
  - `--text-only`: 텍스트가 있는 요소만 포함
  - `--buttons-only`: 버튼 요소만 추출
  - `--inputs-only`: 입력 요소만 추출

## 4. 특수 처리 사항

### 4.1 한글 텍스트 처리

- 한글 텍스트가 포함된 요소는 자동으로 영문 함수명으로 변환
- `hangul_romanize` 라이브러리를 사용한 로마자 변환 시도
- 주요 한글 키워드는 의미적 매핑 (예: '로그인' → 'login')

### 4.2 URL 및 특수 문자 처리

- URL에서 의미 있는 부분 추출 (경로 마지막 부분)
- 특수 문자, 개행 문자 제거 및 공백 정규화
- XPath 및 CSS 선택자에서 안전하게 사용할 수 있도록 문자열 이스케이프 처리

### 4.3 텍스트 없는 요소 처리

- 요소에 텍스트가 없을 경우 다음 전략 사용:
  1. 다른 속성 (placeholder, name, aria-label 등) 활용
  2. OCR을 통한 이미지 텍스트 인식 (버튼의 경우)
  3. 태그 유형 + ID/클래스/인덱스를 조합한 이름 자동 생성

## 5. 시작하기

### 5.1 필수 조건

- Python 3.8+
- Google Cloud 계정 및 Vision API 활성화 (OCR 기능 사용 시)
- Chrome 브라우저 (Selenium WebDriver 용)

### 5.2 설치 및 설정 방법

1. GitHub에서 저장소를 클론합니다:
   ```bash
   git clone https://github.com/taeshkim/po_generator.git
   cd po_generator
   ```

2. 가상환경을 생성하고 활성화합니다:
   ```bash
   # 가상환경 생성
   python -m venv venv
   
   # 가상환경 활성화
   # Windows:
   venv\Scripts\activate
   
   # macOS/Linux:
   source venv/bin/activate
   ```

3. 필요한 의존성 패키지를 설치합니다:
   ```bash
   pip install -r requirements.txt
   ```

4. (선택사항) OCR 기능을 사용하려면 환경 변수를 설정합니다:
   ```bash
   # .env.example 파일을 복사하여 .env 파일 생성
   cp .env.example .env
   
   # .env 파일을 편집하여 Google Cloud Vision API 인증 정보 설정
   # Windows의 경우 메모장 등으로 .env 파일을 직접 열어 편집
   # macOS/Linux:
   nano .env
   ```

### 5.3 사용 방법

#### 기본 사용법
```bash
# 주어진 URL의 웹페이지에서 상호작용 요소를 추출하여 페이지 오브젝트 생성
python src/main.py --url https://example.com
```

#### 옵션 활용 예시

**텍스트가 있는 버튼만 추출:**
```bash
python src/main.py --url https://example.com --buttons-only --text-only
```

**OCR 기능 비활성화 (Google Cloud Vision API 없이 사용):**
```bash
python src/main.py --url https://example.com --no-ocr
```

**디버그 모드 활성화 (상세 정보 출력):**
```bash
python src/main.py --url https://example.com --debug
```

**특정 출력 디렉토리 지정:**
```bash
python src/main.py --url https://example.com --output my_page_objects
```

**처리할 최대 요소 수 제한:**
```bash
python src/main.py --url https://example.com --max-elements 20
```

**입력 필드만 추출:**
```bash
python src/main.py --url https://example.com --inputs-only
```

#### 결과 확인
생성된 페이지 오브젝트 클래스는 기본적으로 `output` 디렉토리(또는 `--output` 옵션으로 지정한 디렉토리)에 저장됩니다. 
생성된 파일은 일반적으로 `[도메인명]_page.py` 형식으로 명명됩니다.

## 6. 생성된 코드 예시

생성된 페이지 오브젝트 클래스는 다음과 같은 형태를 가집니다:

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class example_com_Page:
    """
    https://example.com 페이지의 페이지 오브젝트 클래스
    """

    def __init__(self, driver):
        """
        생성자
        
        Args:
            driver: Selenium WebDriver 인스턴스
        """
        self.driver = driver
        self.url = "https://example.com"

    def navigate(self):
        """페이지로 이동"""
        self.driver.get(self.url)
        return self

    def click_login_button(self):
        """
        '로그인' 버튼 클릭
        """
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(.)='로그인']")))
        return self

    def enter_username(self, text):
        """
        '아이디' 필드에 텍스트 입력
        
        Args:
            text: 입력할 텍스트
        """
        element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        element.clear()  # 기존 텍스트 지우기
        element.send_keys(text)
        return self

    def enter_password(self, text):
        """
        '비밀번호' 필드에 텍스트 입력
        
        Args:
            text: 입력할 텍스트
        """
        element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
        element.clear()  # 기존 텍스트 지우기
        element.send_keys(text)
        return self

    def select_remember_me(self, check=True):
        """
        '로그인 상태 유지' 체크박스/라디오 버튼 설정
        
        Args:
            check: True면 체크, False면 체크 해제 (기본값: True)
        """
        element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "remember-me")))
        # 현재 체크 상태 확인
        is_checked = element.is_selected()
        # 원하는 상태와 다르면 클릭
        if is_checked != check:
            element.click()
        return self
```

## 7. 라이선스

MIT License
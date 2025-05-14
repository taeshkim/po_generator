"""
웹 스크래핑을 통해 페이지에서 상호작용 요소를 추출하는 모듈
"""
import os
import time
from typing import List, Dict, Any, Tuple
from io import BytesIO
import base64

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class WebScraper:
    """웹페이지에서 요소를 스크래핑하는 클래스"""
    
    def __init__(self):
        """Selenium WebDriver 초기화"""
        headless = os.getenv('HEADLESS_MODE', 'True').lower() == 'true'
        timeout = int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))
        
        # Chrome 옵션 설정
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # 성능 향상을 위한 추가 옵션
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')  # 이미지 로딩 비활성화
        
        # 페이지 로딩 속도 향상을 위한 설정
        prefs = {
            'profile.default_content_setting_values': {
                'images': 2,       # 이미지 로딩 비활성화
                'plugins': 2,      # 플러그인 비활성화
                'popups': 2,       # 팝업 비활성화
                'geolocation': 2,  # 위치 정보 비활성화
                'notifications': 2 # 알림 비활성화
            }
        }
        chrome_options.add_experimental_option('prefs', prefs)
        
        # WebDriver 초기화
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.set_page_load_timeout(timeout)
    
    def __del__(self):
        """소멸자: 드라이버 종료"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def navigate_to(self, url: str) -> bool:
        """
        URL로 이동
        
        Args:
            url: 이동할 웹페이지 URL
            
        Returns:
            성공 여부
        """
        try:
            self.driver.get(url)
            # 페이지가 완전히 로드될 때까지 대기
            self.driver.implicitly_wait(10)
            print("페이지 로드 완료...")
            return True
        except Exception as e:
            print(f"URL 탐색 오류: {e}")
            return False
    
    def get_buttons(self) -> List[WebElement]:
        """
        페이지에서 버튼 요소 추출 (헤더와 푸터 포함)
        
        Returns:
            버튼 웹 요소 리스트
        """
        # 다양한 버튼 선택자 시도
        button_elements = []
        
        try:
            # 타임아웃 설정
            self.driver.implicitly_wait(5)
            print("버튼 요소 검색 중...")
            
            # 1. 표준 button 태그 (가장 빠르게 처리)
            button_elements.extend(self.driver.find_elements(By.TAG_NAME, "button"))
            
            # 2. input 태그 중 button, submit 타입
            button_elements.extend(self.driver.find_elements(By.CSS_SELECTOR, "input[type='button'], input[type='submit']"))
            
            # 3. role이 button인 요소들
            button_elements.extend(self.driver.find_elements(By.CSS_SELECTOR, "[role='button']"))
            
            # 검색 효율 향상을 위해 일괄 CSS 선택자 사용
            button_elements.extend(self.driver.find_elements(By.CSS_SELECTOR, 
                "a[class*='btn'], div[class*='btn'], span[class*='btn'], " + 
                "a[href*='login'], a[href*='signin'], a[href*='signup'], a[href*='register'], " +
                "a[href*='mypage'], a[href*='cart'], a[href*='search'], a[href*='customer'], " +
                "header a, .header a, #header a, footer a, .footer a, #footer a"
            ))
            
            # 중복 요소 제거 (element ID 기준)
            unique_elements = {}
            for element in button_elements:
                try:
                    # WebElement 객체의 ID로 중복 체크
                    element_id = element.id
                    if element_id not in unique_elements:
                        unique_elements[element_id] = element
                except:
                    continue
            
            buttons = list(unique_elements.values())
            print(f"{len(buttons)}개의 버튼 요소 찾음.")
            return buttons
            
        except Exception as e:
            print(f"버튼 요소 추출 중 오류: {e}")
            return button_elements
    
    def get_inputs(self) -> List[WebElement]:
        """
        페이지에서 입력 요소 추출 (텍스트 필드, 비밀번호 필드 등)
        
        Returns:
            입력 웹 요소 리스트
        """
        input_elements = []
        
        try:
            # 타임아웃 설정
            self.driver.implicitly_wait(5)
            print("입력 요소 검색 중...")
            
            # 1. 기본 입력 필드 (text, password, email, number 등)
            input_elements.extend(self.driver.find_elements(By.CSS_SELECTOR, 
                "input[type='text'], input[type='password'], input[type='email'], input[type='number'], " +
                "input[type='tel'], input[type='search'], input[type='url'], input:not([type])"
            ))
            
            # 2. textarea 요소
            input_elements.extend(self.driver.find_elements(By.TAG_NAME, "textarea"))
            
            # 3. contenteditable 요소
            input_elements.extend(self.driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true']"))
            
            # 4. 특정 클래스나 역할을 가진 입력 요소
            input_elements.extend(self.driver.find_elements(By.CSS_SELECTOR, 
                "[role='textbox'], [class*='input'], [class*='field'], [class*='text-box']"
            ))
            
            # 5. 로그인/회원가입 폼 내의 입력 요소 찾기
            form_selectors = ["form", "form[action*='login']", "form[action*='signin']", 
                             "form[action*='register']", "form[action*='signup']", 
                             "div[class*='login'], div[class*='signin'], div[id*='login']"]
            
            for selector in form_selectors:
                try:
                    forms = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for form in forms:
                        form_inputs = form.find_elements(By.TAG_NAME, "input")
                        input_elements.extend(form_inputs)
                except:
                    continue
            
            # 중복 요소 제거
            unique_elements = {}
            for element in input_elements:
                try:
                    element_id = element.id
                    if element_id not in unique_elements:
                        unique_elements[element_id] = element
                except:
                    continue
            
            inputs = list(unique_elements.values())
            print(f"{len(inputs)}개의 입력 요소 찾음.")
            return inputs
            
        except Exception as e:
            print(f"입력 요소 추출 중 오류: {e}")
            return input_elements
    
    def get_interaction_elements(self) -> Dict[str, List[WebElement]]:
        """
        페이지에서 모든 상호작용 요소 추출 (버튼, 입력 필드 등)
        
        Returns:
            요소 유형별 웹 요소 리스트를 담은 딕셔너리
        """
        # 버튼 요소 추출
        buttons = self.get_buttons()
        
        # 입력 요소 추출
        inputs = self.get_inputs()
        
        # 체크박스와 라디오 버튼 추출
        checkboxes_radios = self.driver.find_elements(By.CSS_SELECTOR, 
            "input[type='checkbox'], input[type='radio']"
        )
        
        # 선택 요소 추출 (드롭다운 등)
        selects = self.driver.find_elements(By.TAG_NAME, "select")
        
        return {
            'button': buttons,
            'input': inputs,
            'checkbox_radio': checkboxes_radios,
            'select': selects
        }
    
    def get_element_info(self, element: WebElement) -> Dict[str, Any]:
        """
        웹 요소에 대한 정보 추출
        
        Args:
            element: 정보를 추출할 웹 요소
            
        Returns:
            요소 정보를 담은 딕셔너리
        """
        try:
            # 요소가 존재하는지 확인
            WebDriverWait(self.driver, 1).until(EC.staleness_of(element))
            print("요소가 더 이상 존재하지 않습니다.")
            return {'is_displayed': False}
        except:
            pass
            
        try:
            location = element.location
            size = element.size
            
            # 텍스트 및 속성 추출
            text = element.text.strip() if element.text else ""
            element_id = element.get_attribute('id') or ""
            element_class = element.get_attribute('class') or ""
            element_name = element.get_attribute('name') or ""
            element_type = element.get_attribute('type') or ""
            element_value = element.get_attribute('value') or ""
            element_href = element.get_attribute('href') or ""
            element_aria_label = element.get_attribute('aria-label') or ""
            element_title = element.get_attribute('title') or ""
            element_placeholder = element.get_attribute('placeholder') or ""
            
            # 요소 유형 판별
            tag_name = element.tag_name
            if tag_name == 'input':
                if element_type in ['text', 'password', 'email', 'tel', 'number', 'url', 'search']:
                    element_category = 'input'
                elif element_type in ['checkbox', 'radio']:
                    element_category = 'checkbox_radio'
                elif element_type in ['button', 'submit', 'reset']:
                    element_category = 'button'
                else:
                    element_category = 'other'
            elif tag_name == 'button':
                element_category = 'button'
            elif tag_name == 'textarea':
                element_category = 'input'
            elif tag_name == 'select':
                element_category = 'select'
            elif tag_name == 'a':
                element_category = 'button'  # a 태그를 버튼으로 간주
            else:
                element_category = 'other'
            
            # 텍스트가 없으면 다른 속성에서 텍스트 추출 시도
            if not text:
                if element_value and element_category != 'input':  # 입력 필드의 값은 텍스트로 사용하지 않음
                    text = element_value
                elif element_placeholder:
                    text = element_placeholder
                elif element_aria_label:
                    text = element_aria_label
                elif element_title:
                    text = element_title
                elif element_href:
                    # URL에서 마지막 부분만 추출 (개행 문자 제거)
                    element_href = element_href.replace('\n', '').replace('\r', '')
                    text = element_href.split('/')[-1].split('?')[0].replace('-', ' ').replace('_', ' ')
            
            # XPath 생성 (더 효율적인 방법으로)
            xpath_options = []
            
            # ID 기반 XPath (가장 안정적)
            if element_id:
                # ID도 개행 문자가 있을 수 있으므로 제거
                clean_id = element_id.replace('\n', ' ').replace('\r', ' ')
                clean_id = ' '.join(clean_id.split())  # 연속된 공백을 하나로
                id_xpath = f"//*[@id='{clean_id}']"
                xpath_options.append(id_xpath)
            
            # 이름 기반 XPath
            if element_name:
                # 이름에도 개행 문자가 있을 수 있으므로 제거
                clean_name = element_name.replace('\n', ' ').replace('\r', ' ')
                clean_name = ' '.join(clean_name.split())  # 연속된 공백을 하나로
                name_xpath = f"//*[@name='{clean_name}']"
                xpath_options.append(name_xpath)
            
            # 텍스트 기반 XPath (안정적이지만 텍스트가 변경될 수 있음)
            if text and len(text) < 50:  # 텍스트가 너무 길면 XPath로 쓰기 어려움
                # 개행문자를 공백으로 변환하고 정규화
                clean_text = text.replace('\n', ' ').replace('\r', ' ')
                clean_text = ' '.join(clean_text.split())  # 연속된 공백을 하나로
                text_xpath = f"//*[normalize-space(.)='{clean_text}']"
                xpath_options.append(text_xpath)
            
            # 다른 속성 기반 XPath는 생략 (성능 향상)
            
            # CSS 선택자 생성
            css_selector = None
            if element_id:
                css_selector = f"#{element_id}"
            elif element_class:
                css_selector = f".{element_class.split()[0]}"  # 첫 번째 클래스만 사용
            
            return {
                'element': element,
                'tag_name': tag_name,
                'element_category': element_category,
                'text': text,
                'id': element_id,
                'class': element_class,
                'name': element_name,
                'type': element_type,
                'value': element_value,
                'placeholder': element_placeholder,
                'href': element_href,
                'aria_label': element_aria_label,
                'title': element_title,
                'location': location,
                'size': size,
                'xpath_options': xpath_options,
                'css_selector': css_selector,
                'is_displayed': element.is_displayed(),
                'is_enabled': element.is_enabled()
            }
        except StaleElementReferenceException:
            print("요소가 더 이상 존재하지 않습니다.")
            return {'is_displayed': False}
        except Exception as e:
            print(f"요소 정보 추출 중 오류: {e}")
            return {'is_displayed': False}
    
    def capture_element_screenshot(self, element: WebElement) -> bytes:
        """
        웹 요소의 스크린샷 캡처
        
        Args:
            element: 스크린샷을 찍을 웹 요소
            
        Returns:
            요소 이미지 바이트 데이터
        """
        try:
            # 스크롤해서 요소가 보이게 함
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.2)  # 스크롤 후 짧게 대기 (시간 단축)
            
            # 전체 페이지 스크린샷
            screenshot = self.driver.get_screenshot_as_png()
            
            # 스크린샷 이미지로 변환
            img = Image.open(BytesIO(screenshot))
            
            # 요소 위치와 크기
            location = element.location
            size = element.size
            
            # 요소 영역 크롭
            left = location['x']
            top = location['y']
            right = location['x'] + size['width']
            bottom = location['y'] + size['height']
            
            # 이미지 크롭 및 바이트로 변환
            element_img = img.crop((left, top, right, bottom))
            img_byte_arr = BytesIO()
            element_img.save(img_byte_arr, format='PNG')
            
            return img_byte_arr.getvalue()
        except Exception as e:
            print(f"요소 스크린샷 캡처 중 오류: {e}")
            # 오류 발생 시 빈 이미지 반환
            empty_img = Image.new('RGB', (100, 100), color = 'white')
            img_byte_arr = BytesIO()
            empty_img.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
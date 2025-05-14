"""
페이지 오브젝트 패턴 함수 생성 모듈
"""
from typing import List, Dict, Any

class PageObjectGenerator:
    """페이지 오브젝트 패턴 함수를 생성하는 클래스"""
    
    def __init__(self):
        """페이지 오브젝트 생성기 초기화"""
        self.indent = "    "  # 들여쓰기 4칸
    
    def generate_page_object_class(self, url: str, elements: List[Dict[str, Any]]) -> str:
        """
        페이지 오브젝트 클래스 코드 생성
        
        Args:
            url: 웹페이지 URL
            elements: 요소 정보 리스트
            
        Returns:
            생성된 페이지 오브젝트 클래스 코드
        """
        # 페이지 이름 생성 (URL에서 도메인명 추출)
        from urllib.parse import urlparse
        # URL에서 개행 문자 제거
        clean_url = url.replace('\n', '').replace('\r', '')
        domain = urlparse(clean_url).netloc.replace(".", "_").replace("-", "_")
        page_name = f"{domain}_Page"
        
        # 클래스 코드 생성
        code = [
            f"class {page_name}:",
            f"{self.indent}\"\"\"",
            f"{self.indent}{url} 페이지의 페이지 오브젝트 클래스",
            f"{self.indent}\"\"\"",
            "",
            f"{self.indent}def __init__(self, driver):",
            f"{self.indent}{self.indent}\"\"\"",
            f"{self.indent}{self.indent}생성자",
            f"{self.indent}{self.indent}",
            f"{self.indent}{self.indent}Args:",
            f"{self.indent}{self.indent}{self.indent}driver: Selenium WebDriver 인스턴스",
            f"{self.indent}{self.indent}\"\"\"",
            f"{self.indent}{self.indent}self.driver = driver",
            f"{self.indent}{self.indent}self.url = \"{url}\"",
            "",
            f"{self.indent}def navigate(self):",
            f"{self.indent}{self.indent}\"\"\"페이지로 이동\"\"\"",
            f"{self.indent}{self.indent}self.driver.get(self.url)",
            f"{self.indent}{self.indent}return self",
            ""
        ]
        
        # 생성된 메서드 이름을 저장 (중복 방지)
        used_method_names = set()
        
        # 요소별 메서드 생성
        for element in elements:
            element_category = element.get('element_category', 'button')  # 기본값은 버튼
            
            if element_category == 'button':
                # 버튼 요소의 경우 클릭 메서드 생성
                button_code = self._generate_button_method(element, used_method_names)
                code.extend(button_code)
                code.append("")
            
            elif element_category == 'input':
                # 입력 필드의 경우 입력 메서드 생성
                input_code = self._generate_input_method(element, used_method_names)
                code.extend(input_code)
                code.append("")
                
            elif element_category == 'checkbox_radio':
                # 체크박스나 라디오 버튼의 경우 토글 메서드 생성
                checkbox_code = self._generate_checkbox_method(element, used_method_names)
                code.extend(checkbox_code)
                code.append("")
                
            elif element_category == 'select':
                # 선택 요소의 경우 선택 메서드 생성
                select_code = self._generate_select_method(element, used_method_names)
                code.extend(select_code)
                code.append("")
        
        return "\n".join(code)
    
    def _sanitize_text(self, text: str) -> str:
        """
        텍스트를 메서드 이름에 사용할 수 있도록 정리
        
        Args:
            text: 원본 텍스트
            
        Returns:
            정리된 텍스트
        """
        # 한글 판별 (한글이 있으면 로마자 변환 시도 또는 영어 대체어 사용)
        has_korean = any('\uAC00' <= char <= '\uD7A3' for char in text)
        
        if has_korean:
            try:
                # 한글 로마자 변환 시도
                import hangul_romanize
                from hangul_romanize.romanizer import Romanizer
                romanizer = Romanizer(text)
                text = romanizer.romanize()
            except (ImportError, Exception):
                # 변환 실패 시 해시 대신 의미있는 기본값 사용
                if '로그인' in text or '로인' in text:
                    return 'login'
                elif '비밀번호' in text or '패스워드' in text:
                    return 'password'
                elif '아이디' in text or 'ID' in text:
                    return 'userid'
                elif '검색' in text or '찾기' in text:
                    return 'search'
                elif '확인' in text:
                    return 'confirm'
                elif '취소' in text:
                    return 'cancel'
                elif '제출' in text or '전송' in text:
                    return 'submit'
                elif '회원가입' in text or '가입' in text:
                    return 'signup'
                # 추가적인 한글 키워드 매핑 가능
        
        # 개행 문자를 공백으로 변환
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # 특수 문자와 공백 제거
        import re
        text = re.sub(r'[^\w\s]', '', text).lower()
        
        # 공백을 언더스코어로 변환
        text = text.strip().replace(' ', '_')
        
        # 숫자로 시작하는 경우 앞에 'n'을 붙임
        if text and text[0].isdigit():
            text = 'n' + text
            
        # 빈 문자열인 경우
        if not text:
            return 'element'
            
        return text
    
    def _generate_method_name(self, element: Dict[str, Any], prefix: str, used_names: set) -> str:
        """
        요소 정보를 기반으로 메서드 이름 생성
        
        Args:
            element: 요소 정보 딕셔너리
            prefix: 메서드 접두사 (click, enter, select 등)
            used_names: 이미 사용된 메서드 이름 집합
            
        Returns:
            생성된 메서드 이름
        """
        # 요소의 텍스트, ID, 이름, 플레이스홀더 등을 활용하여 메서드 이름 생성
        element_category = element.get('element_category', 'button')
        
        # 입력 필드일 경우 placeholder, name, id 먼저 확인
        if element_category == 'input':
            if element.get('placeholder'):
                name_base = self._sanitize_text(element['placeholder'])
            elif element.get('name'):
                name_base = self._sanitize_text(element['name'])
            elif element.get('id'):
                name_base = self._sanitize_text(element['id'])
            elif element.get('aria_label'):
                name_base = self._sanitize_text(element['aria_label'])
            elif element.get('text'):
                name_base = self._sanitize_text(element['text'])
            else:
                tag = element.get('tag_name', 'input')
                name_base = f"{tag}{element.get('index', '')}"
        else:
            # 버튼 등의 경우 텍스트 먼저 확인
            if element.get('text'):
                name_base = self._sanitize_text(element['text'])
            elif element.get('aria_label'):
                name_base = self._sanitize_text(element['aria_label'])
            elif element.get('title'):
                name_base = self._sanitize_text(element['title'])
            elif element.get('id'):
                name_base = self._sanitize_text(element['id'])
            elif element.get('name'):
                name_base = self._sanitize_text(element['name'])
            else:
                tag = element.get('tag_name', 'element')
                name_base = f"{tag}{element.get('index', '')}"
        
        # 메서드 이름 조합
        method_name = f"{prefix}_{name_base}"
        
        # 메서드 이름이 너무 길면 잘라내기
        if len(method_name) > 50:
            method_name = method_name[:50]
        
        # 중복 방지
        original_name = method_name
        counter = 1
        while method_name in used_names:
            method_name = f"{original_name}_{counter}"
            counter += 1
        
        # 사용된 이름 추가
        used_names.add(method_name)
        
        return method_name
    
    def _generate_button_method(self, element: Dict[str, Any], used_names: set) -> List[str]:
        """
        버튼을 위한 메서드 코드 생성
        
        Args:
            element: 버튼 정보 딕셔너리
            used_names: 이미 사용된 메서드 이름 집합
            
        Returns:
            생성된 메서드 코드 라인 리스트
        """
        # 버튼 텍스트로 함수명 생성
        method_name = self._generate_method_name(element, "click", used_names)
        
        # 버튼을 찾는 가장 좋은 방법 선택
        locator_code = self._get_best_locator(element)
        
        # 버튼 설명 텍스트 (개행 문자 제거)
        button_text = element.get('text') or element.get('aria_label') or element.get('title') or element.get('id') or "버튼"
        button_description = button_text.replace('\n', ' ').replace('\r', ' ')
        # 연속된 공백을 하나로 통합
        button_description = ' '.join(button_description.split())
        
        # 메서드 코드 생성
        method_code = [
            f"{self.indent}def {method_name}(self):",
            f"{self.indent}{self.indent}\"\"\"",
            f"{self.indent}{self.indent}'{button_description}' 버튼 클릭",
            f"{self.indent}{self.indent}\"\"\"",
            locator_code,
            f"{self.indent}{self.indent}return self"
        ]
        
        return method_code
    
    def _generate_input_method(self, element: Dict[str, Any], used_names: set) -> List[str]:
        """
        입력 필드를 위한 메서드 코드 생성
        
        Args:
            element: 입력 필드 정보 딕셔너리
            used_names: 이미 사용된 메서드 이름 집합
            
        Returns:
            생성된 메서드 코드 라인 리스트
        """
        # 입력 필드 설명으로 함수명 생성
        method_name = self._generate_method_name(element, "enter", used_names)
        
        # 입력 필드를 찾는 가장 좋은 방법 선택
        locator_code = self._get_best_locator(element)
        
        # 요소 설명 (placeholder, name, id 등을 사용, 개행 문자 제거)
        field_text = element.get('placeholder') or element.get('name') or element.get('id') or element.get('text') or element.get('aria_label') or "값"
        field_description = field_text.replace('\n', ' ').replace('\r', ' ')
        # 연속된 공백을 하나로 통합
        field_description = ' '.join(field_description.split())
        
        # 메서드 코드 생성
        method_code = [
            f"{self.indent}def {method_name}(self, text):",
            f"{self.indent}{self.indent}\"\"\"",
            f"{self.indent}{self.indent}'{field_description}' 필드에 텍스트 입력",
            f"{self.indent}{self.indent}",
            f"{self.indent}{self.indent}Args:",
            f"{self.indent}{self.indent}{self.indent}text: 입력할 텍스트",
            f"{self.indent}{self.indent}\"\"\"",
            f"{self.indent}{self.indent}element = {locator_code.strip()}",
            f"{self.indent}{self.indent}element.clear()  # 기존 텍스트 지우기",
            f"{self.indent}{self.indent}element.send_keys(text)",
            f"{self.indent}{self.indent}return self"
        ]
        
        return method_code
    
    def _generate_checkbox_method(self, element: Dict[str, Any], used_names: set) -> List[str]:
        """
        체크박스/라디오 버튼을 위한 메서드 코드 생성
        
        Args:
            element: 체크박스/라디오 버튼 정보 딕셔너리
            used_names: 이미 사용된 메서드 이름 집합
            
        Returns:
            생성된 메서드 코드 라인 리스트
        """
        # 체크박스 설명으로 함수명 생성
        method_name = self._generate_method_name(element, "select", used_names)
        
        # 체크박스를 찾는 가장 좋은 방법 선택
        locator_code = self._get_best_locator(element)
        
        # 요소 설명 (개행 문자 제거)
        field_text = element.get('text') or element.get('name') or element.get('id') or element.get('aria_label') or "옵션"
        field_description = field_text.replace('\n', ' ').replace('\r', ' ')
        # 연속된 공백을 하나로 통합
        field_description = ' '.join(field_description.split())
        
        # 메서드 코드 생성
        method_code = [
            f"{self.indent}def {method_name}(self, check=True):",
            f"{self.indent}{self.indent}\"\"\"",
            f"{self.indent}{self.indent}'{field_description}' 체크박스/라디오 버튼 설정",
            f"{self.indent}{self.indent}",
            f"{self.indent}{self.indent}Args:",
            f"{self.indent}{self.indent}{self.indent}check: True면 체크, False면 체크 해제 (기본값: True)",
            f"{self.indent}{self.indent}\"\"\"",
            f"{self.indent}{self.indent}element = {locator_code.strip()}",
            f"{self.indent}{self.indent}# 현재 체크 상태 확인",
            f"{self.indent}{self.indent}is_checked = element.is_selected()",
            f"{self.indent}{self.indent}# 원하는 상태와 다르면 클릭",
            f"{self.indent}{self.indent}if is_checked != check:",
            f"{self.indent}{self.indent}{self.indent}element.click()",
            f"{self.indent}{self.indent}return self"
        ]
        
        return method_code
    
    def _generate_select_method(self, element: Dict[str, Any], used_names: set) -> List[str]:
        """
        선택 요소를 위한 메서드 코드 생성
        
        Args:
            element: 선택 요소 정보 딕셔너리
            used_names: 이미 사용된 메서드 이름 집합
            
        Returns:
            생성된 메서드 코드 라인 리스트
        """
        # 선택 요소 설명으로 함수명 생성
        method_name = self._generate_method_name(element, "select", used_names)
        
        # 선택 요소를 찾는 가장 좋은 방법 선택
        locator_code = self._get_best_locator(element)
        
        # 요소 설명 (개행 문자 제거)
        field_text = element.get('text') or element.get('name') or element.get('id') or element.get('aria_label') or "드롭다운"
        field_description = field_text.replace('\n', ' ').replace('\r', ' ')
        # 연속된 공백을 하나로 통합
        field_description = ' '.join(field_description.split())
        
        # 메서드 코드 생성
        method_code = [
            f"{self.indent}def {method_name}(self, option_text):",
            f"{self.indent}{self.indent}\"\"\"",
            f"{self.indent}{self.indent}'{field_description}' 드롭다운에서 옵션 선택",
            f"{self.indent}{self.indent}",
            f"{self.indent}{self.indent}Args:",
            f"{self.indent}{self.indent}{self.indent}option_text: 선택할 옵션의 텍스트",
            f"{self.indent}{self.indent}\"\"\"",
            f"{self.indent}{self.indent}from selenium.webdriver.support.ui import Select",
            f"{self.indent}{self.indent}element = {locator_code.strip()}",
            f"{self.indent}{self.indent}select = Select(element)",
            f"{self.indent}{self.indent}select.select_by_visible_text(option_text)",
            f"{self.indent}{self.indent}return self"
        ]
        
        return method_code
    
    def _get_best_locator(self, element: Dict[str, Any]) -> str:
        """
        요소를 찾기 위한 가장 좋은 로케이터 코드 생성
        
        Args:
            element: 요소 정보 딕셔너리
            
        Returns:
            로케이터 코드
        """
        # 요소 카테고리에 따라 적절한 대기 조건 결정
        element_category = element.get('element_category', 'button')
        if element_category == 'button':
            wait_code = "WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable"
        else:
            wait_code = "WebDriverWait(self.driver, 10).until(EC.presence_of_element_located"
        
        # ID가 있는 경우 ID 사용 (가장 안정적)
        if element.get('id'):
            return (
                f"{self.indent}{self.indent}{wait_code}((By.ID, \"{element['id']}\")))\n"
            )
        
        # 이름이 있는 경우 이름 사용
        elif element.get('name'):
            return (
                f"{self.indent}{self.indent}{wait_code}((By.NAME, \"{element['name']}\")))\n"
            )
        
        # XPath 옵션이 있는 경우 XPath 사용
        elif element.get('xpath_options') and element['xpath_options']:
            xpath = element['xpath_options'][0]
            return (
                f"{self.indent}{self.indent}{wait_code}((By.XPATH, \"{xpath}\")))\n"
            )
        
        # CSS 선택자가 있는 경우 CSS 선택자 사용
        elif element.get('css_selector'):
            return (
                f"{self.indent}{self.indent}{wait_code}((By.CSS_SELECTOR, \"{element['css_selector']}\")))\n"
            )
        
        # 텍스트가 있는 경우 텍스트로 검색
        elif element.get('text'):
            # 텍스트에 따옴표나 개행이 있는 경우 처리
            # XPath에서는 개행 문자가 특히 문제가 되므로 완전히 제거
            text = element['text'].replace("'", "\\'").replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')
            # 연속된 공백을 하나로 통합
            text = ' '.join(text.split())
            tag = element.get('tag_name', '*')
            
            if element_category == 'button':
                return (
                    f"{self.indent}{self.indent}{wait_code}((By.XPATH, \"//{tag}[normalize-space(.)='{text}']"
                    f" | //{tag}[@value='{text}'] | //{tag}[normalize-space(@placeholder)='{text}']\"))))\n"
                )
            else:
                return (
                    f"{self.indent}{self.indent}{wait_code}((By.XPATH, \"//{tag}[normalize-space(@placeholder)='{text}']"
                    f" | //{tag}[normalize-space(@name)='{text}']\"))))\n"
                )
        
        # aria-label이 있는 경우 aria-label 사용
        elif element.get('aria_label'):
            aria_label = element['aria_label'].replace("'", "\\'").replace('"', '\\"').replace('\n', ' ').replace('\r', '')
            return (
                f"{self.indent}{self.indent}{wait_code}((By.CSS_SELECTOR, \"[aria-label='{aria_label}']\")))\n"
            )
        
        # 클래스가 있는 경우 클래스명 사용
        elif element.get('class'):
            class_name = element['class'].split()[0]  # 첫 번째 클래스만 사용
            return (
                f"{self.indent}{self.indent}# 주의: 클래스 선택자는 변경될 수 있습니다\n"
                f"{self.indent}{self.indent}{wait_code}((By.CLASS_NAME, \"{class_name}\"))))\n"
            )
        
        # 위치 기반 CSS 선택자 사용 (마지막 수단)
        else:
            tag_name = element.get('tag_name', '*')
            index = element.get('index', 1)
            return (
                f"{self.indent}{self.indent}# 주의: 위치 기반 선택자는 페이지가 변경되면 작동하지 않을 수 있습니다\n"
                f"{self.indent}{self.indent}{wait_code}((By.CSS_SELECTOR, \"{tag_name}:nth-of-type({index})\"))))\n"
            )
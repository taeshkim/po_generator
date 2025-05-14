"""
페이지 오브젝트 생성기 테스트
"""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# 프로젝트 루트 디렉토리를 모듈 검색 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.po_generator import PageObjectGenerator


class TestPageObjectGenerator(unittest.TestCase):
    """페이지 오브젝트 생성기 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.generator = PageObjectGenerator()
    
    def test_generate_method_name(self):
        """메서드 이름 생성 테스트"""
        # 영어 텍스트
        self.assertEqual(self.generator._generate_method_name("Login"), "click_login")
        self.assertEqual(self.generator._generate_method_name("Sign Up"), "click_sign_up")
        self.assertEqual(self.generator._generate_method_name("Submit Form"), "click_submit_form")
        
        # 특수문자 포함
        self.assertEqual(self.generator._generate_method_name("Login!"), "click_login")
        self.assertEqual(self.generator._generate_method_name("Sign-Up Now"), "click_signup_now")
        
        # 한글 텍스트 (해시값으로 변환)
        korean_method = self.generator._generate_method_name("로그인")
        self.assertTrue(korean_method.startswith("click_button_"))
        self.assertEqual(len(korean_method), len("click_button_") + 6)  # 6자리 해시값
    
    def test_get_best_locator(self):
        """최적의 로케이터 선택 테스트"""
        # ID가 있는 경우
        button_with_id = {
            'id': 'login-button',
            'text': 'Login',
            'xpath_options': ['//*[@id="login-button"]']
        }
        locator_code = self.generator._get_best_locator(button_with_id)
        self.assertIn('find_element(By.ID, "login-button")', locator_code)
        
        # ID가 없고 XPath만 있는 경우
        button_with_xpath = {
            'id': '',
            'text': 'Login',
            'xpath_options': ['/html/body/div/button[1]']
        }
        locator_code = self.generator._get_best_locator(button_with_xpath)
        self.assertIn('find_element(By.XPATH, "/html/body/div/button[1]")', locator_code)
        
        # ID와 XPath가 없고 텍스트만 있는 경우
        button_with_text = {
            'id': '',
            'text': 'Login',
            'xpath_options': []
        }
        locator_code = self.generator._get_best_locator(button_with_text)
        self.assertIn('find_element(By.XPATH, "//button[contains(text(), \'Login\')]', locator_code)
        
        # 모두 없고 클래스만 있는 경우
        button_with_class = {
            'id': '',
            'text': '',
            'xpath_options': [],
            'class': 'btn btn-primary'
        }
        locator_code = self.generator._get_best_locator(button_with_class)
        self.assertIn('find_element(By.CLASS_NAME, "btn")', locator_code)
    
    def test_generate_page_object_class(self):
        """페이지 오브젝트 클래스 생성 테스트"""
        url = "https://example.com/login"
        buttons = [
            {
                'id': 'login-button',
                'text': 'Login',
                'xpath_options': ['//*[@id="login-button"]'],
                'tag_name': 'button'
            },
            {
                'id': '',
                'text': 'Sign Up',
                'xpath_options': ['/html/body/div/a[1]'],
                'tag_name': 'a'
            }
        ]
        
        code = self.generator.generate_page_object_class(url, buttons)
        
        # 클래스 이름 확인
        self.assertIn("class example_com_Page:", code)
        
        # URL 확인
        self.assertIn(f'self.url = "{url}"', code)
        
        # 버튼 메서드 확인
        self.assertIn("def click_login(self):", code)
        self.assertIn("def click_sign_up(self):", code)
        
        # 로케이터 확인
        self.assertIn('find_element(By.ID, "login-button")', code)
        self.assertIn('find_element(By.XPATH, "/html/body/div/a[1]")', code)


if __name__ == "__main__":
    unittest.main()
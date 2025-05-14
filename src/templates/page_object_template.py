"""
페이지 오브젝트 클래스 템플릿
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PageTemplate:
    """
    페이지 오브젝트 패턴의 기본 템플릿 클래스
    """

    def __init__(self, driver):
        """
        생성자
        
        Args:
            driver: Selenium WebDriver 인스턴스
        """
        self.driver = driver
        self.url = None
    
    def navigate(self):
        """페이지로 이동"""
        if self.url:
            self.driver.get(self.url)
        return self
    
    def wait_for_element(self, locator, timeout=10):
        """
        요소가 나타날 때까지 대기
        
        Args:
            locator: (By, value) 형식의 로케이터 튜플
            timeout: 타임아웃 (초 단위)
            
        Returns:
            찾은 웹 요소
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
    
    def wait_for_clickable(self, locator, timeout=10):
        """
        요소가 클릭 가능할 때까지 대기
        
        Args:
            locator: (By, value) 형식의 로케이터 튜플
            timeout: 타임아웃 (초 단위)
            
        Returns:
            찾은 웹 요소
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
    
    def click_element(self, locator, timeout=10):
        """
        요소 클릭
        
        Args:
            locator: (By, value) 형식의 로케이터 튜플
            timeout: 타임아웃 (초 단위)
            
        Returns:
            self (메서드 체이닝을 위함)
        """
        element = self.wait_for_clickable(locator, timeout)
        element.click()
        return self
    
    def input_text(self, locator, text, timeout=10):
        """
        텍스트 입력
        
        Args:
            locator: (By, value) 형식의 로케이터 튜플
            text: 입력할 텍스트
            timeout: 타임아웃 (초 단위)
            
        Returns:
            self (메서드 체이닝을 위함)
        """
        element = self.wait_for_element(locator, timeout)
        element.clear()
        element.send_keys(text)
        return self
    
    def get_text(self, locator, timeout=10):
        """
        요소의 텍스트 가져오기
        
        Args:
            locator: (By, value) 형식의 로케이터 튜플
            timeout: 타임아웃 (초 단위)
            
        Returns:
            요소의 텍스트
        """
        element = self.wait_for_element(locator, timeout)
        return element.text
"""
Google Cloud Vision API를 사용한 OCR 기능 모듈
"""
import os
import io
import json
from typing import List, Dict, Any
import warnings
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class OCRProcessor:
    """Google Cloud Vision API를 사용하여 이미지에서 텍스트를 추출하는 클래스"""
    
    def __init__(self):
        """Google Cloud Vision 클라이언트 초기화"""
        # API 키 확인
        self.api_available = False
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if not credentials_path or not os.path.isfile(credentials_path):
            warnings.warn(f"Google Cloud Vision API 인증 정보 파일이 존재하지 않습니다: {credentials_path}")
            self.client = None
        else:
            try:
                # 인증 파일 확인
                print(f"인증 파일 확인 중: {credentials_path}")
                with open(credentials_path, 'r') as f:
                    json.load(f)  # JSON 형식 검증
                
                # 환경 변수가 제대로 설정되었는지 확인
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
                
                from google.cloud import vision
                self.client = vision.ImageAnnotatorClient()
                self.api_available = True
                print("Google Cloud Vision API 초기화 성공")
            except Exception as e:
                warnings.warn(f"Google Cloud Vision API 초기화 오류: {e}")
                self.client = None
    
    def detect_text(self, image_content: bytes) -> List[Dict[str, Any]]:
        """
        이미지에서 텍스트 감지
        
        Args:
            image_content: 이미지 바이트 데이터
            
        Returns:
            감지된 텍스트와 경계 상자 좌표를 포함하는 딕셔너리 리스트
        """
        # API가 사용 불가능한 경우 빈 리스트 반환
        if not self.api_available or self.client is None:
            print("Google Cloud Vision API가 구성되지 않았습니다. 빈 결과를 반환합니다.")
            return []
        
        try:
            from google.cloud import vision
            image = vision.Image(content=image_content)
            response = self.client.text_detection(image=image)
            
            if response.error.message:
                raise Exception(f"Google Vision API 오류: {response.error.message}")
            
            # 첫 번째 항목은 전체 텍스트
            if not response.text_annotations:
                return []
                
            texts = []
            for text in response.text_annotations[1:]:  # 첫 번째 항목은 전체 텍스트이므로 건너뜀
                vertices = [(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices]
                
                # 바운딩 박스의 좌상단과 우하단 좌표 계산
                x_values = [vertex[0] for vertex in vertices]
                y_values = [vertex[1] for vertex in vertices]
                top_left = (min(x_values), min(y_values))
                bottom_right = (max(x_values), max(y_values))
                
                texts.append({
                    'text': text.description,
                    'vertices': vertices,
                    'top_left': top_left,
                    'bottom_right': bottom_right,
                    'center': (
                        (top_left[0] + bottom_right[0]) / 2, 
                        (top_left[1] + bottom_right[1]) / 2
                    )
                })
                
            return texts
        except Exception as e:
            print(f"텍스트 감지 중 오류 발생: {e}")
            return []
    
    def is_button_text(self, text_info: Dict[str, Any]) -> bool:
        """
        텍스트가 버튼에 해당하는지 판단 (간단한 휴리스틱 사용)
        
        Args:
            text_info: 감지된 텍스트 정보 딕셔너리
            
        Returns:
            버튼으로 판단되면 True, 아니면 False
        """
        # 간단한 버튼 텍스트 판단 로직 (필요에 따라 개선할 수 있음)
        text = text_info['text'].lower()
        button_keywords = [
            'submit', 'send', 'login', 'sign', 'sign up', 'sign in', 'logout', 
            'register', 'cancel', 'delete', 'save', 'next', 'previous', 'back',
            'continue', 'apply', 'search', 'buy', 'purchase', 'add', 'create',
            '제출', '보내기', '로그인', '회원가입', '가입', '등록', '취소', '삭제',
            '저장', '다음', '이전', '돌아가기', '계속', '적용', '검색', '구매', '추가', '생성'
        ]
        
        # 길이가 짧고 버튼 키워드와 일치하거나, 15자 이하의 짧은 단어는 버튼일 가능성이 높음
        return any(keyword in text for keyword in button_keywords) or len(text) <= 15
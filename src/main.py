#!/usr/bin/env python3
"""
페이지 오브젝트 생성기 메인 모듈
"""
import os
import sys
import argparse
from typing import List, Dict, Any
import time
from pathlib import Path
from dotenv import load_dotenv

# 현재 디렉토리를 모듈 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.web_scraper import WebScraper
from src.utils.ocr import OCRProcessor
from src.utils.po_generator import PageObjectGenerator

# 환경 변수 로드
load_dotenv()

def parse_args():
    """명령줄 인수 파싱"""
    parser = argparse.ArgumentParser(description='URL로부터 페이지 오브젝트 패턴 함수 생성')
    parser.add_argument('--url', type=str, required=True, help='페이지 오브젝트를 생성할 웹페이지 URL')
    parser.add_argument('--output', type=str, default='output', help='생성된 페이지 오브젝트 코드를 저장할 디렉토리')
    parser.add_argument('--no-ocr', action='store_true', help='OCR 기능을 비활성화합니다 (Google Cloud Vision API가 없는 경우 사용)')
    parser.add_argument('--max-elements', type=int, help='처리할 최대 요소 수 (기본값: 제한 없음)')
    parser.add_argument('--timeout', type=int, default=60, help='스크래핑 타임아웃 (초, 기본값: 60)')
    parser.add_argument('--debug', action='store_true', help='디버그 모드 활성화 (더 많은 정보 출력)')
    parser.add_argument('--text-only', action='store_true', help='텍스트가 있는 요소만 포함 (기본값: 모든 요소 포함)')
    parser.add_argument('--buttons-only', action='store_true', help='버튼 요소만 추출 (기본값: 모든 상호작용 요소 추출)')
    parser.add_argument('--inputs-only', action='store_true', help='입력 요소만 추출 (기본값: 모든 상호작용 요소 추출)')
    
    return parser.parse_args()

def main():
    """메인 함수"""
    # 명령줄 인수 파싱
    args = parse_args()
    
    print(f"URL '{args.url}'에서 상호작용 요소 추출 중...")
    
    # 출력 디렉토리 생성
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    
    # 웹 스크래퍼 인스턴스 생성
    scraper = WebScraper()
    
    # OCR 프로세서 인스턴스 생성
    ocr_processor = OCRProcessor()
    
    # 페이지 오브젝트 생성기 인스턴스 생성
    po_generator = PageObjectGenerator()
    
    try:
        # URL로 이동
        if not scraper.navigate_to(args.url):
            print(f"URL '{args.url}'로 이동할 수 없습니다.")
            return
        
        # 타임아웃 설정
        start_time = time.time()
        print(f"상호작용 요소 검색을 시작합니다. 최대 {args.timeout}초 대기 중...")
        
        # 어떤 요소를 추출할지 결정
        all_elements = []
        
        if args.buttons_only:
            # 버튼만 추출
            buttons = scraper.get_buttons()
            print(f"{len(buttons)}개의 버튼 요소를 찾았습니다.")
            all_elements = [(button, 'button') for button in buttons]
            
        elif args.inputs_only:
            # 입력 필드만 추출
            inputs = scraper.get_inputs()
            print(f"{len(inputs)}개의 입력 요소를 찾았습니다.")
            all_elements = [(input_field, 'input') for input_field in inputs]
            
        else:
            # 모든 상호작용 요소 추출
            interaction_elements = scraper.get_interaction_elements()
            
            # 요소 유형별로 처리
            for category, elements in interaction_elements.items():
                for element in elements:
                    all_elements.append((element, category))
            
            print(f"총 {len(all_elements)}개의 상호작용 요소를 찾았습니다:")
            print(f"- 버튼: {len(interaction_elements['button'])}개")
            print(f"- 입력 필드: {len(interaction_elements['input'])}개")
            print(f"- 체크박스/라디오 버튼: {len(interaction_elements['checkbox_radio'])}개")
            print(f"- 선택 요소: {len(interaction_elements['select'])}개")
        
        elapsed_time = time.time() - start_time
        print(f"요소 탐색 완료 (소요 시간: {elapsed_time:.2f}초)")
        
        if not all_elements:
            print("상호작용 요소를 찾을 수 없습니다.")
            return
        
        # 처리할 요소 수 제한 (지정된 경우)
        if args.max_elements and len(all_elements) > args.max_elements:
            print(f"요소가 너무 많습니다. 처음 {args.max_elements}개만 처리합니다.")
            all_elements = all_elements[:args.max_elements]
        
        # 요소 정보 수집
        element_info_list = []
        skipped_elements = 0
        non_text_elements = 0
        
        print(f"요소 정보 추출 중... (최대 {len(all_elements)}개)")
        for i, (element, category) in enumerate(all_elements):
            try:
                # 중간 진행 상황 표시
                if (i+1) % 10 == 0:
                    print(f"진행 중: {i+1}/{len(all_elements)}개 처리됨")
                
                # 요소 정보 추출
                element_info = scraper.get_element_info(element)
                
                # 카테고리 설정
                element_info['element_category'] = category
                
                # 요소가 화면에 표시되지 않으면 건너뜀
                if not element_info.get('is_displayed', False):
                    if args.debug:
                        print(f"요소 {i+1}: 화면에 표시되지 않음 (건너뜀)")
                    skipped_elements += 1
                    continue
                
                # OCR이 비활성화되지 않고 버튼이면 OCR 수행
                if not args.no_ocr and category == 'button' and (not element_info.get('text') or args.debug):
                    try:
                        # 버튼 스크린샷 캡처
                        element_screenshot = scraper.capture_element_screenshot(element)
                        
                        # OCR로 텍스트 인식
                        ocr_results = ocr_processor.detect_text(element_screenshot)
                        
                        # 버튼 텍스트인지 확인
                        button_texts = [result for result in ocr_results 
                                       if ocr_processor.is_button_text(result)]
                        
                        # OCR 결과가 있으면 기존 텍스트 업데이트
                        if button_texts:
                            # 가장 큰 텍스트 사용 (버튼 레이블일 가능성이 높음)
                            best_text = max(button_texts, 
                                           key=lambda x: (x['bottom_right'][0] - x['top_left'][0]) * 
                                                       (x['bottom_right'][1] - x['top_left'][1]))
                            
                            if args.debug:
                                old_text = element_info.get('text', '(없음)')
                                new_text = best_text['text']
                                if old_text != new_text:
                                    print(f"요소 {i+1} OCR 결과: '{old_text}' -> '{new_text}'")
                            
                            element_info['text'] = best_text['text']
                            element_info['ocr_data'] = button_texts
                    except Exception as e:
                        if args.debug:
                            print(f"요소 {i+1} OCR 처리 중 오류: {e}")
                
                # 인덱스 추가 (CSS 선택자용)
                element_info['index'] = i + 1
                
                # 텍스트가 있거나 --text-only 옵션이 비활성화된 경우 추가
                has_text = bool(element_info.get('text', '').strip())
                
                if has_text or not args.text_only:
                    # 자동 생성 요소 이름 설정 (텍스트가 없는 경우)
                    if not has_text and category != 'input':  # 입력 필드는 placeholder 등이 있으므로 제외
                        # 태그와 ID 또는 클래스 기반으로 자동 이름 생성
                        tag = element_info.get('tag_name', 'element')
                        element_id = element_info.get('id', '')
                        element_class = element_info.get('class', '').split()[0] if element_info.get('class') else ''
                        element_type = element_info.get('type', '')
                        element_name = element_info.get('name', '')
                        element_placeholder = element_info.get('placeholder', '')
                        href = element_info.get('href', '')
                        
                        # 가장 구체적인 정보 사용
                        if element_placeholder:
                            auto_name = element_placeholder
                        elif element_id:
                            auto_name = f"{tag}_{element_id}"
                        elif element_name:
                            auto_name = f"{tag}_{element_name}"
                        elif element_class:
                            auto_name = f"{tag}_{element_class}"
                        elif element_type:
                            auto_name = f"{tag}_{element_type}"
                        elif href:
                            # URL에서 의미 있는 부분 추출하고 개행 문자 제거
                            href = href.replace('\n', '').replace('\r', '')
                            url_part = href.split('/')[-1].split('?')[0]
                            if url_part:
                                auto_name = f"{tag}_{url_part}"
                            else:
                                auto_name = f"{tag}_{i+1}"
                        else:
                            auto_name = f"{tag}_{i+1}"
                        
                        # 특수문자 제거
                        import re
                        auto_name = re.sub(r'[^\w\s]', '_', auto_name)
                        auto_name = re.sub(r'_+', '_', auto_name)  # 연속된 언더스코어 하나로
                        auto_name = auto_name[:100]  # 이름이 너무 길어지지 않도록 제한
                        
                        element_info['text'] = auto_name
                    
                    # 디버그 모드에서 요소 정보 추가 출력
                    if args.debug:
                        tag = element_info.get('tag_name', '?')
                        cls = element_info.get('class', '').split()[0] if element_info.get('class') else ''
                        id_attr = element_info.get('id', '')
                        name_attr = element_info.get('name', '')
                        type_attr = element_info.get('type', '')
                        placeholder = element_info.get('placeholder', '')
                        
                        id_info = f" id='{id_attr}'" if id_attr else ''
                        class_info = f" class='{cls}...'" if cls else ''
                        name_info = f" name='{name_attr}'" if name_attr else ''
                        type_info = f" type='{type_attr}'" if type_attr else ''
                        placeholder_info = f" placeholder='{placeholder}'" if placeholder else ''
                        
                        element_desc = f"<{tag}{id_info}{class_info}{name_info}{type_info}{placeholder_info}>"
                        text = element_info.get('text', '(텍스트 없음)')
                        category_text = f"[{category}]"
                        
                        print(f"요소 {i+1}: {category_text} {element_desc} {text}")
                    else:
                        category_text = f"[{category}]"
                        text = element_info.get('text', '(텍스트 없음)')
                        print(f"요소 {i+1}: {category_text} {text}")
                    
                    element_info_list.append(element_info)
                else:
                    if args.debug:
                        print(f"요소 {i+1}: 텍스트 없음 (건너뜀)")
                    non_text_elements += 1
                
            except Exception as e:
                print(f"요소 {i+1} 처리 중 오류: {e}")
        
        # 요약 정보 출력
        if args.debug:
            print(f"\n처리 결과 요약:")
            print(f"- 총 요소 수: {len(all_elements)}")
            print(f"- 화면에 표시되지 않아 건너뛴 요소: {skipped_elements}")
            print(f"- 텍스트가 없어 건너뛴 요소: {non_text_elements}")
            print(f"- 유효한 요소: {len(element_info_list)}")
        
        # 페이지 오브젝트 클래스 생성
        if element_info_list:
            print(f"{len(element_info_list)}개의 유효한 요소로 페이지 오브젝트 생성 중...")
            
            # 페이지 이름 생성 (URL에서 도메인명 추출)
            from urllib.parse import urlparse
            # URL에서 개행 문자 제거
            clean_url = args.url.replace('\n', '').replace('\r', '')
            domain = urlparse(clean_url).netloc.replace(".", "_").replace("-", "_")
            
            # 페이지 오브젝트 코드 생성
            po_code = po_generator.generate_page_object_class(clean_url, element_info_list)
            
            # 출력 파일 경로
            output_file = output_dir / f"{domain}_page.py"
            
            # 파일에 저장
            with open(output_file, 'w', encoding='utf-8') as f:
                # 필요한 import 문 추가
                imports = [
                    "from selenium.webdriver.common.by import By",
                    "from selenium.webdriver.support.ui import WebDriverWait",
                    "from selenium.webdriver.support import expected_conditions as EC",
                    ""
                ]
                f.write("\n".join(imports) + "\n" + po_code)
            
            print(f"페이지 오브젝트 클래스가 {output_file}에 생성되었습니다.")
            
            # 생성된 메서드 이름 목록 출력
            if args.debug:
                import re
                methods = re.findall(r'def\s+(\w+)\(self', po_code)
                methods = [m for m in methods if m != 'navigate' and m != '__init__']  # 기본 메서드 제외
                
                # 메서드 유형 분류
                click_methods = [m for m in methods if m.startswith('click_')]
                enter_methods = [m for m in methods if m.startswith('enter_')]
                select_methods = [m for m in methods if m.startswith('select_')]
                
                print("\n생성된 메서드 목록:")
                if click_methods:
                    print(f"\n버튼 메서드 ({len(click_methods)}개):")
                    for i, method in enumerate(click_methods):
                        print(f"{i+1}. {method}")
                
                if enter_methods:
                    print(f"\n입력 필드 메서드 ({len(enter_methods)}개):")
                    for i, method in enumerate(enter_methods):
                        print(f"{i+1}. {method}")
                
                if select_methods:
                    print(f"\n선택 요소 메서드 ({len(select_methods)}개):")
                    for i, method in enumerate(select_methods):
                        print(f"{i+1}. {method}")
                
        else:
            print("유효한 상호작용 요소를 찾을 수 없습니다.")
    
    except Exception as e:
        print(f"오류 발생: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
    
    finally:
        # 리소스 정리는 객체 소멸자에서 처리됨
        pass

if __name__ == "__main__":
    main()
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time
import string
import random # Added for random sleep

def main():
    # WebDriver 경로 설정 (chromedriver.exe가 스크립트와 동일한 디렉토리에 있다고 가정)
    # 사용자의 chromedriver.exe 경로에 맞게 수정해야 합니다.
    # 예: 'd:\\path\\to\\chromedriver.exe' 또는 '/usr/local/bin/chromedriver'
    webdriver_path = './chromedriver' 
    service = Service(executable_path=webdriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저 창을 숨기려면 주석 해제
    options.add_argument('--disable-gpu') # headless 모드에서 필요할 수 있음
    # options.add_argument("--window-size=1920,1080") # 해상도 설정
    # options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36")
    driver = None # Initialize driver to None
    try:
        driver = webdriver.Chrome(service=service, options=options)
        # 대상 URL
        url = 'https://domain.gabia.com/regist/regist_step1.php'
        driver.get(url)
        print(f"'{url}'에 접속했습니다.")

        # 4글자 도메인 이름 생성 (알파벳 소문자만 사용)
        possible_chars = string.ascii_lowercase
        four_letter_domains = []
        count = 0
        # 전체 조합 생성 (시간이 매우 오래 걸릴 수 있음 - 26^4 = 456,976개)
        # 테스트를 위해 조합 수를 줄이려면 아래 주석을 해제하고 반복 범위를 줄이세요.
        # for char1 in possible_chars[:1]: # 예: 'a'로 시작
        #     for char2 in possible_chars[:2]: # 예: 'aa', 'ab'
        #         for char3 in possible_chars[:1]:
        #             for char4 in possible_chars[:1]:
        #                 domain_name = f"{char1}{char2}{char3}{char4}"
        #                 four_letter_domains.append(f"{domain_name}.org")
        #                 count += 1
        #                 if count >= 5: # 테스트용으로 5개로 제한
        #                     break
        #             if count >= 5: break
        #         if count >= 5: break
        #     if count >= 5: break
        # 실제 전체 조합 생성:
        for char1 in possible_chars:
            for char2 in possible_chars:
                for char3 in possible_chars:
                    domain_name = f"{char1}{char2}{char3}"
                    four_letter_domains.append(f"{domain_name}.org")

        print(f"총 {len(four_letter_domains)}개의 3글자 .org 도메인 조합을 생성했습니다.")

        # available_output_file = r"C:\Users\kyle\Documents\kisscuseme\Data\available_domains.md"
        # checked_output_file = r"C:\Users\kyle\Documents\kisscuseme\Data\checked_domains.md"
        available_output_file = r"/Users/a2130056/Documents/kisscuseme/Data/available_domains.md"
        checked_output_file = r"/Users/a2130056/Documents/kisscuseme/Data/checked_domains.md"

        # Gabia 도메인 검색 페이지의 요소 선택자
        search_box_css_selector = "input[id='new_domain']" 
        search_button_css_selector = "button[id='btn-domainsearch']" 

        # 이미 확인한 도메인 로드
        checked_domains = set()
        try:
            with open(checked_output_file, 'r', encoding='utf-8') as cf:
                for line in cf:
                    checked_domains.add(line.strip())
            print(f"'{checked_output_file}'에서 {len(checked_domains)}개의 이미 확인된 도메인을 로드했습니다.")
        except FileNotFoundError:
            print(f"'{checked_output_file}' 파일이 없습니다. 새로 시작합니다.")

        with open(available_output_file, 'a', encoding='utf-8') as af, \
             open(checked_output_file, 'a', encoding='utf-8') as cf:
            for i, domain_to_check in enumerate(four_letter_domains):
                if domain_to_check in checked_domains:
                    print(f"({i+1}/{len(four_letter_domains)}) 이미 확인됨 (건너뛰기): {domain_to_check}")
                    continue
                try:
                    print(f"({i+1}/{len(four_letter_domains)}) 확인 중: {domain_to_check}")
                    
                    # 검색창이 나타날 때까지 대기하고 도메인 이름 입력
                    search_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, search_box_css_selector))
                    )
                    search_input.clear()
                    search_input.send_keys(domain_to_check) # 확장자 제외하고 이름만 입력
                    
                    # .org TLD 선택 로직 (Gabia는 검색창에 이름만 넣고 TLD는 별도 선택하거나 기본값 사용)
                    # 이 스크립트에서는 .org가 이미 선택되어 있거나, Gabia가 자동으로 처리한다고 가정합니다.
                    # 명시적으로 .org를 선택해야 한다면, 상세 검색 옵션 UI를 조작하는 코드가 필요합니다.
                    # 예: (주석처리된 TLD 선택 로직 참고)
                    # WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//input[@value='.org' and @name='tlds[]']"))).click()

                    # 검색 버튼 클릭
                    search_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, search_button_css_selector))
                    )
                    search_button.click()

                    # 결과 로딩 대기 (Gabia는 AJAX로 결과를 로드할 수 있음)
                    # 결과 영역이 나타날 때까지 기다리는 것이 좋음
                    # 예: WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'domain_list_result')))
                    time.sleep(random.uniform(1.5, 3.0)) # 서버 부하 감소 및 AJAX 로딩 시간 확보

                    is_available = False
                    try:
                        # Gabia의 '등록 가능' 상태는 주로 '선택' 버튼으로 표시됨
                        # 또는 "등록 가능합니다" 메시지.
                        # 검색한 도메인 이름과 함께 표시되는 요소를 정확히 찾아야 함.
                        domain_name_only = domain_to_check.replace('.org', '')
                        
                        # 시나리오 1: '선택' 버튼 확인 (가장 일반적인 경우)
                        # 해당 도메인 이름이 포함된 li 요소 내의 '선택' 버튼을 찾음
                        select_button_xpath = f"//ul[contains(@class,'domain_list')]//li[.//span[@class='name' and normalize-space(text())='{domain_to_check}']]//button[contains(@class,'btn_select')]"
                        # 또는 더 간단하게, 결과 영역에 '선택' 버튼이 있는지 (단일 검색 결과 시)
                        # select_button_xpath_general = f"//div[contains(@class,'result_box') and contains(@class,'on')]//button[contains(text(),'선택')]"
                        
                        # 새로운 사용 가능 여부 판단 로직:
                        # ID가 _singleResult인 DOM 내에 '등록할 수 있는 도메인'이라는 text가 있는지 확인
                        try:
                            availability_check_xpath = "//*[@id='_singleResult' and contains(., '등록할 수 있는 도메인')]"
                            element = WebDriverWait(driver, 3).until(
                                EC.presence_of_element_located((By.XPATH, availability_check_xpath))
                            )
                            if element.is_displayed():
                                is_available = True
                                print(f"{domain_to_check}는 사용 가능합니다 (ID: _singleResult, Text: '등록할 수 있는 도메인').")
                                af.write(domain_to_check + "\n")
                                af.flush() # 사용 가능한 도메인 파일에 즉시 기록
                                time.sleep(0.5)
                            else:
                                print(f"{domain_to_check}는 사용 불가능하거나 ID _singleResult 내 텍스트를 찾을 수 없습니다.")
                        except:
                            print(f"{domain_to_check}는 사용 불가능하거나 ID _singleResult 요소를 찾을 수 없습니다.")
                    except Exception as e_avail_check:
                        print(f"{domain_to_check} 사용 가능 여부 확인 중 오류: {e_avail_check}")
                    finally:
                        # 확인된 도메인 기록
                        cf.write(domain_to_check + "\n")
                        cf.flush()

                except Exception as e_domain_loop:
                    print(f"{domain_to_check} 처리 중 오류 발생: {e_domain_loop}")
                    # 오류 발생 시 현재 URL과 스크린샷 저장 (디버깅용)
                    # timestamp = time.strftime("%Y%m%d-%H%M%S")
                    # driver.save_screenshot(f"error_{domain_to_check.replace('.','_')}_{timestamp}.png")
                    # print(f"오류 발생 URL: {driver.current_url}")
                    # 페이지를 새로고침하거나 초기 URL로 돌아가서 다음 도메인 시도
                    try:
                        print("오류 발생으로 초기 URL로 돌아갑니다.")
                        driver.get(url)
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, search_box_css_selector))) # 검색창 로드 확인
                    except Exception as e_reload:
                        print(f"페이지 리로드 중 심각한 오류 발생: {e_reload}. 스크립트를 중단합니다.")
                        raise # 심각한 오류 시 스크립트 중단
                    continue

        print(f"사용 가능한 도메인 목록이 '{available_output_file}'에 저장되었습니다.")
        print(f"확인된 도메인 목록이 '{checked_output_file}'에 저장되었습니다.")

    except Exception as e_main:
        print(f"스크립트 실행 중 오류 발생: {e_main}")
    finally:
        # 모든 작업 완료 후 드라이버 종료
        if driver:
            driver.quit()
            print("웹 드라이버를 종료했습니다.")

if __name__ == "__main__":
    main()
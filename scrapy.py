from selenium import webdriver
import time
from konlpy.tag import Twitter
from FileConvert import Converting


######################
# 데이터 입출력 클래스 #
######################
class Keyword:
    def __init__(self):
        pass

    # 영화 제목 입력 함수
    def input_keyword_list(self):
        print("\n")
        print("======================================================================================")
        print("좋아하는 영화 제목을 입력해주세요. '그만' 이라고 입력할 때까지 추가 입력 가능합니다. (최대 5개)")
        print("======================================================================================")

        input_arr = []
        count = 1

        # 최대 5개까지 영화제목을 배열에 넣고 '그만' 이라고 입력하면 배열을 return
        while count > 0:
            temp = input("영화 %d번째 제목 입력 : " % count)
            if temp != "그만":
                input_arr.append(temp)
            else:
                break
            count += 1

            if count > 5:
                print("입력 제한은 최대 5개 입니다.")
                break

        return input_arr

    # 영화 데이터 출력 함수
    def print_keyword_list(self, data):
        print("\n\n")
        print("==============================================================")
        print("입력된 영화들의 데이터를 분석하여 공통된 데이터만 추출하였습니다.")
        print("==============================================================")

        # 공통 데이터 출력
        for k, v in data.items():
            if not v:
                data[k] = "공통된 데이터가 없습니다."
            else:
                data[k] = ", ".join(v)

            print(k, ":", data[k])


######################
# 스크래핑 관한 클래스 #
######################
class Scraping:
    def __init__(self):
        pass

    # 웹스크래핑 함수
    def get_scrap_info(self, name_arr):

        # 트위터 형태소 분석기 사용. 정확성은 떨어지지만 속도는 빠름
        twitter = Twitter()
        temp_dict = {}

        # 셀레니움 스크래핑
        driver = webdriver.Chrome('chromedriver.exe')
        driver.get('https://movie.naver.com/')
        time.sleep(1)

        # 입력했던 영화 제목들을 하나씩 접근하여 스크래핑
        for name in name_arr:
            actors = []
            similar_movies = []

            # ========================================영화 정보 스크랩 Start==============================================

            # 검색창에 영화 이름 검색
            driver.find_element_by_id('ipt_tx_srch').send_keys(name)
            driver.find_element_by_xpath('//*[@id="jSearchArea"]/div/button').click()
            time.sleep(1)

            # 검색했는데 해당 영화가 안나오면 다시 입력
            try:
                movie_list = driver.find_element_by_class_name('search_list_1')
            except:
                print("\n\n###############################")
                print("영화 제목을 정확하게 입력해 주세요.", sep='\n')
                print("###############################\n\n")
                return Keyword.input_keyword_list()

            # 검색결과 페이지에서 첫번째에 있는 영화 클릭
            movie_list.find_element_by_xpath('//*[@id="old_content"]/ul[2]/li[1]/dl/dt/a').click()
            time.sleep(1)

            # -----------------------장르, 줄거리(형태소 분석)----------------------------
            genres_list = driver.find_element_by_xpath('//*[@id="content"]/div[1]/div[2]/div[1]/dl/dd[1]/p/span[1]').text
            genres = genres_list.split(', ')

            # 줄거리 명사만 추출, 명사 중복 제거
            summary = driver.find_element_by_class_name('con_tx').text
            summary_nouns = twitter.nouns(summary)
            summary_nouns_set = list(set(summary_nouns))

            # --------------------------------배우---------------------------------------
            driver.find_element_by_link_text('배우/제작진').click()
            time.sleep(1)

            # 주연 배우만 수집
            actors_info = driver.find_elements_by_class_name('p_info')
            for line in actors_info:
                if line.find_element_by_class_name('p_part').text == "주연":
                    actors.append(line.find_element_by_class_name('k_name').text)
                else:
                    continue

            # ------------------------------연관 영화------------------------------------
            driver.find_element_by_link_text('명대사/연관영화').click()
            time.sleep(1)

            # 연관 영화는 iframe이 달라서 바로 접근이 안됨. iframe에 접근해서 크롤링
            driver.switch_to_frame(driver.find_element_by_id('relateIframe'))
            similar_movie_titles = driver.find_elements_by_class_name('title_mv')

            # 연관 영화 리스트에 있는 영화 제목들을 배열에 넣음
            for line in similar_movie_titles:
                similar_movies.append(line.text)

            # ========================================영화 정보 스크랩 End================================================

            # 영화 정보들을 나중에 JSON으로 변환하기위해 딕셔너리에 넣음
            temp_dict[name] = {'줄거리': summary_nouns_set, '장르': genres,
                               '배우': actors, '연관 영화': similar_movies}

            # 아까 접근했던 iframe에서 나가기
            driver.switch_to.default_content()

        driver.close()

        return temp_dict

    # 데이터 비교하는 공통만 추출하는 함수
    def compare_data(self, data):

        # 배우, 장르, 줄거리 키워드, 연관 영화
        # 각각 리스트들을 접근하기 쉽게 한 곳에 넣음
        actors_keyword = []
        genres_keyword = []
        summary_keyword = []
        similar_movies_keyword = []
        result_lists = [summary_keyword, genres_keyword, actors_keyword, similar_movies_keyword]

        data_keys = list(data.keys())
        movie_info_keys = list(data[data_keys[0]].keys())

        for line in data:
            i = 0
            for result in result_lists:
                result.extend(data[line][movie_info_keys[i]])
                i += 1

        # 각각 리스트마다 중복값만 넣는다
        actors_keyword = list(set([x for x in actors_keyword if actors_keyword.count(x) > 1]))
        genres_keyword = list(set([x for x in genres_keyword if genres_keyword.count(x) > 1]))
        summary_keyword = list(set([x for x in summary_keyword if summary_keyword.count(x) > 1]))
        similar_movies_keyword = list(set([x for x in similar_movies_keyword if similar_movies_keyword.count(x) > 1]))

        keyword_dict = {'줄거리': summary_keyword, '장르': genres_keyword,
                        '배우': actors_keyword, '연관 영화': similar_movies_keyword}

        return keyword_dict


if __name__ == '__main__':

    convert = Converting()  # FileConvert.py 파일을 import해서 생성자 생성
    keyword = Keyword()
    scrap = Scraping()

    titles = keyword.input_keyword_list()  # 영화 제목들을 입력받음

    info = scrap.get_scrap_info(titles)  # 영화 제목마다 검색해서 스크래핑

    convert.to_json(info, "movies.json")  # 스크랩한 데이터를 json으로 변환

    moviesData = convert.call_json('movies.json')  # json으로 변환한 파일을 불러온다

    compareData = scrap.compare_data(moviesData)  # 비교해서 공통 데이터만 추출

    convert.to_json(compareData, "result.json")  # 공통 데이터를 json으로 변환

    resultData = convert.call_json('result.json')  # json으로 변환한 파일을 불러온다

    keyword.print_keyword_list(resultData)  # result 데이터 출력
import speech_recognition as sr
import pyaudio
import pickle
# 형태소 분석
from konlpy.tag import Okt
import pandas as pd
import threading


okt = Okt()


class voice:
    def __init__(self) -> object:
        self.r = sr.Recognizer(language="ko-KR", key="AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw")

        self.df = pd.read_csv("500_가중치.csv", encoding='utf-8')  # 전체 형태소 분석 (가중치) 파일
        self.type_df = pd.read_csv("type_token_가중치.csv", encoding='utf-8')  # 범죄 유형 분류 기준 단어 파일

        self.cnt = 1  # 보이스피싱 확률 변수
        self.type1_cnt = 1  # 대출사기형 확률
        self.type2_cnt = 1  # 수사기관사칭형 확률
        self.text = ''  # 음성에서 변환된 텍스트
        self.token_dict = {}  # 단어:횟수 딕셔너리 생성

    def call(self):
        print('\n※ 통화 시작 ※\n')

        # ============================================================================================================ #
        # description_label.config(text='통화시작')
        # ============================================================================================================ #

        # while True:
        def _process():
            # for i in range(0,100):
            while True:
                with sr.Microphone() as source:
                    try:
                        #voice = self.r.listen(source, phrase_time_limit=10, timeout=3)
                        voice = self.r.listen(source, timeout=3)
                        #self.text = self.r.recognize_google(voice, language='ko-KR')
                        self.text = self.r.recognize(voice)
                        print(self.text)
                        self.ing_cnt()  # 피싱 탐지 함수 호출
                        print('피싱방지')
                        # print('▶ 통화내역 : {}'.format(self.text))

                    except:
                        self.result()
                        print('\n※ 통화 종료 ※\n')
                        # ============================================================================================ #
                        # description_label.config(text=' 통화 종료 ')
                        # ============================================================================================ #
                        break

        th = threading.Thread(target=_process)
        th.start()

    def detection(self):
        self.token_ko = pd.DataFrame(okt.pos(self.text), columns=['단어', '형태소'])
        self.token_ko = self.token_ko[
            (self.token_ko['단어'].str.len() > 1) & (self.token_ko.형태소.isin(['Noun', 'Adverb']))]

        for i in self.token_ko.단어.values:
            if i in self.df.단어.values:
                self.cnt *= float(self.df.loc[self.df.단어 == i, '확률'])
                if i not in self.token_dict:
                    self.token_dict[i] = 1
                else:
                    self.token_dict[i] = self.token_dict.get(i) + 1

        if self.cnt > 100:
            self.cnt = 100  # 확률이 100%를 넘겼을 경우 100으로 초기화

    # 유형을 분류하는 함수
    def categorizing(self):
        self.token_df = pd.DataFrame(zip(self.token_dict.keys(), self.token_dict.values()), columns=['의심 단어', '횟수'])
        self.token_df = self.token_df.sort_values(by='횟수', ascending=False)

        for i, x in zip(self.token_df['의심 단어'].values, self.token_df['횟수'].values):
            if i in self.type_df.type1_단어.values:
                self.type1_cnt *= float(self.type_df.loc[self.type_df.type1_단어 == i, 'type1_확률']) ** x
            elif i in self.type_df.type2_단어.values:
                self.type2_cnt *= float(self.type_df.loc[self.type_df.type2_단어 == i, 'type2_확률']) ** x

        if self.type1_cnt > self.type2_cnt:
            return '대출사기형'
        else:
            return '수사기관사칭형'

    # 결과를 출력하는 함수

    def ing_cnt(self):
        self.detection()  # 분석 함수 호출
        # a = "format example1 : {:.2f}".format(1.23456789)
        score_label.config(text= "{:.0f}".format(self.cnt))
        dg_text  = '! 보이스피싱 위험도가 매우 높습니다.\n 경찰 검찰 뭐시기 뭐시기는 절대로 당신에게 개인정보를 요구하지 않습니다. 보이스 피싱 신고는 112'
        if self.cnt <= 20:
            safe_type = '안전'
            # ======================================================================================================== #
            status_label.config(text=safe_type)
            danger_description.config(text= '보이스 피싱 위험성이 감지 되지 않았습니다.')
            status_label.config(image=s_img[0])
            # th2 = threading.Thread(target=status_label.config(text=safe_type))
            # th2.start()
            # ======================================================================================================== #

        elif self.cnt <= 40:
            safe_type = '의심'
            # ======================================================================================================== #
            status_label.config(text=safe_type)
            danger_description.config(text=safe_type+dg_text)
            # th2 = threading.Thread(target=status_label.config(text=safe_type))
            status_label.config(image=s_img[1])
            # th2.start()
            # ======================================================================================================== #

        elif self.cnt <= 60:
            safe_type = '경고'
            # ======================================================================================================== #
            status_label.config(text=safe_type)
            danger_description.config(text=safe_type+dg_text)
            status_label.config(image=s_img[2])
            # th2 = threading.Thread(target=status_label.config(text='경고'))
            # th2.start()
            # ======================================================================================================== #

        else:
            safe_type = '위험'
            # ======================================================================================================== #
            status_label.config(text=safe_type)
            danger_description.config(text=safe_type+dg_text)
            status_label.config(image=s_img[3])
            # th2 = threading.Thread(target=description_label.config(text='위험'))
            # th2.start()
            # ======================================================================================================== #

        bolded_safe_type = "\033[1m" + safe_type + "\033[0m"

        print(f'▶ 보이스피싱 지수 : {self.cnt:.2f} [{bolded_safe_type}]')
        return safe_type


    def result(self):
        # 보이스피싱 확률이 의심 단계 이상일 때만 출력할 수 있도록
        if self.cnt > 20:
            self.token_csv = self.token_ko['단어'].values  # csv 생성을 위한 통화음성 단어 추출 (명사, 부사)

            type_title = self.categorizing()  # 유형 분류 함수 호출
            print(f'\n▶ 해당 음성은 {type_title} 보이스피싱일 가능성이 높습니다')
            print('▶ 보이스피싱 탐색 결과')
            print(self.token_df.head(10))


# v = voice()
# v.call()

# ==================================================================================================================== #
# ==================================================================================================================== #
# ==================================================================================================================== #
# ==================================================================================================================== #
# ==================================================================================================================== #
# ==================================================================================================================== #
# ==================================================================================================================== #
# ==================================================================================================================== #
# ==================================================================================================================== #
# ==================================================================================================================== #
# ==================================================================================================================== #
# ==================================================================================================================== #


from tkinter import *

win = Tk()  # 창 생성

# win.geometry("350x585")  # 창의 크기 변경
win.geometry("470x819")  # 창의 크기 변경
win.title("Res9ue")  # 창의 이름 변경
win.option_add("*Font", "맑은고딕 25")  # 폰트변경
#########################################################시작 멘트#########################################################
description_label = Label(win, text="시작을 누르면\n 보이스피싱 검사를 시작합니다.", borderwidth=3, relief="ridge")
# description_label = Label(win, text="시작을 누르면\n 보이스피싱 검사를 시작합니다.")
description_label.config(width=28, height=20)
description_label.place(x=6, y=10)

# ==================================================================================================================== #


'''
버튼을 눌렀을 때
1. description label 삭제
2. voice 클래스 생성, call() 함수 실행
3. analysis_label, status_label,score_label ,jum_label 생성
'''


def t_start():
    # 1
    description_label.destroy()
    # 2
    v = voice()
    th1 = threading.Thread(target=v.call())
    th1.start()

    second_scene()
# 3
def second_scene():
    # analysis_label.cof(win, text='분석중...', borderwidth=3, relief="ridge")
    analysis_label.config(text='분석중...', borderwidth=3, relief="ridge")
    analysis_label.config(width=5, height=1)
    analysis_label.place(x=10, y=30)
    analysis_label.place()


    # status_label = Label(win, text="상태", borderwidth=1, relief="ridge")
    # status_label.config(text="상태", borderwidth=1, relief="ridge")
    # status_label.config(width=10, height=6)
    status_label.place(x=90, y=100)
    status_label.place()

    # score_label = Label(win, text='점수', borderwidth=1, relief="ridge")
    score_label.config( borderwidth=1, relief="ridge")
    score_label.config(width=5, height=2)
    score_label.place(x=300, y=315)
    score_label.place()

    # jum_label = Label(win, text='점', borderwidth=1, relief="ridge")
    jum_label.config(text='점', borderwidth=1, relief="ridge")
    jum_label.config(width=3, height=2)
    jum_label.place(x=400, y=315)
    jum_label.place()


    danger_description.config(text='설명이 들어가는 공간', borderwidth=1, relief="ridge")
    danger_description.config(width=28, height=8)
    danger_description.place(x=6, y=400)
    danger_description.place()

'''
def th():
    th = threading.Thread(target=start())
    th.daemon = False
    th.start()
'''

##############################시작버튼##############################

start_btn = Button(win, text="검사시작", command=t_start)  # 버튼 설정, 버튼크기

analysis_label = Label(win, text='분석중...', borderwidth=3, relief="ridge")
analysis_label.place_forget()

#상태
s_img = [PhotoImage(file="l_0.png").subsample(4), PhotoImage(file="l_1.png").subsample(4), PhotoImage(file="l_2.png").subsample(4), PhotoImage(file="l_3.png").subsample(4) ]
# img = img.subsample(4)#그림 크기를 1/n로 줄이겠다
status_label = Label(win, image=s_img[0])
status_label.place_forget()

score_label = Label(win, borderwidth=1, relief="ridge")
score_label.place_forget()

jum_label = Label(win, text='점', borderwidth=1, relief="ridge")
jum_label.place_forget()

start_btn.config(width=10, height=2)  # 버튼 크기
start_btn.place(x=155, y=700)

danger_description = Label(win, text='', borderwidth=3, relief="ridge")
analysis_label.place_forget()

win.mainloop()
'''
    imgObj = PhotoImage(file = "image.gif")
      
    imgLabel = Label(root, image=imgObj)
    imgLabel.pack()
    '''
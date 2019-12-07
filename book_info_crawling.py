#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
新刊検索クローリング関連
"""

# import ***************************************************************************
# 追加要 ***********
import requests     # webページ取得用
import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#*******************
import csv          # CSV読み書き
import urllib       # urlエンコード変換
import datetime     # 日付判定
import time         # wait用
from typing import List
#*******************
from debug_info import Debug
from csv_util import CsvUtil, CsvEncodeType
from db_info_control import DBInfoCntrl, DBAuthorInfo
#***********************************************************************************

# Const Define *********************************************************************
# AMAZON_SEARCH_URL = "https://www.amazon.co.jp/s?k="   # アマゾン検索用URL
AMAZON_SEARCH_URL = "https://www.amazon.co.jp/s?k="
AMAZON_SEARCH_URL2 = "&i=stripbooks&rh=p_n_srvg_2374648051%3A86137051|86138051|86139051|86140051%2Cp_n_availability%3A2227306051&s=date-desc-rank&dc&__mk_ja_JP=カタカナ&qid=1575193372&rnid=2374648051&ref=sr_nr_p_n_srvg_2374648051_9"

REQUEST_RETRY_NUM = 5   # リクエストリトライ回数
REQUEST_WAIT_TIME = 10  # リトライ待ち時間(s)
#***********************************************************************************

class BookInfoCrawling:

    def __init__(self):
        """  コンストラクタ
        """
        self.__search_infos = {} # 検索情報リスト(ディクショナリ)
        self.__author_list = []  # 著者名リスト
        self.__search_cnt = 0    # 検索カウント
        self.__db_ctrl = DBInfoCntrl() # DB制御
        self.__web_drivers = [] # 生成したドライバ一覧

    
    def create_url(self) -> List[str]:
        """ URL生成  
        著者名から検索用URLを生成する  
        [I] name_data : 著者名リスト  
        [O] list : URLリスト
        """
        Debug.tmpprint("func : create_url")
        url_list = []
        # 全key名でURLを生成し，listに保持
        for search_name in self.__author_list:
            Debug.tmpprint(search_name)
            url_list.append(AMAZON_SEARCH_URL + urllib.parse.quote(search_name.encode("utf-8")) + AMAZON_SEARCH_URL2) # 日本語を16進数に変換
        return url_list


    def create_search_info_list(self, filename:str) -> None:
        """ 検索データ情報リストの生成  
        著者名リストを生成．別途著者名をキーとしたハッシュマップを生成し，データとして検索開始日を保持する  
        [I] filename : 確認対象ファイル名  
        [O] dict : キー=著者名，データ=検索開始日
        """
        Debug.tmpprint("func : create_search_info_list")
        if filename.find(".csv") > 0:
            self.__create_url_for_csv(filename)
        else:
            self.__create_url_for_db()


    def get_serch_info(self) -> dict:
        """ 検索データ情報リスト取得  
        [O]検索データ情報リスト
        """
        return self.search_infos


    def create_author_list(self):
        """ 著者リスト生成  
        """
        for author in self.search_infos.keys():
            self.__author_list.append(author)


    def get_author_list(self) -> List[str]:
        """ 著者リスト取得  
        [O] 著者リスト
        """
        return self.__author_list
    

    def get_author_list_num(self) -> List[int]:
        """ 著者リスト数取得  
        [O] 著者リスト数
        """
        return len(self.__author_list)


    def create_db(self, user_name:str) -> None:
        """ DB生成  
        [I] user_name ユーザ名
        """
        self.__db_ctrl.create_db(user_name)

    
    def set_table_key(self, user_name:str) -> bool:
        """ ユーザ情報テーブル主キー設定  
        [I] user_name ユーザ名  
        [O] 結果
        """
        return self.__db_ctrl.set_user_info_key(user_name)


    def exec_search(self, url:str) -> List[webdriver.remote.webelement.WebElement]:
        """ 検索実行
        渡されたURLから検索処理を実行する  
        [I] url : 検索実行URL  
        [O] 検索結果
        """
        Debug.tmpprint("func : exec_search")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        divs = driver.find_elements_by_class_name('s-result-item')
        # 失敗時は一定時間待ってから再度取得を試みる
        if len(divs) == 0:
            is_ok = False
            for retry in range(0,REQUEST_RETRY_NUM,1):
                time.sleep(REQUEST_WAIT_TIME *( retry+1))
                # 再度実行
                divs = driver.find_elements_by_class_name('s-result-item')
                if len(divs) != 0:
                    is_ok = True
                    break
                else:
                    if retry == REQUEST_RETRY_NUM:
                        # リトライ上限に達した
                        Debug.dprint("request err -> " + self.__author_list[self.__search_cnt])
            if is_ok == False:
                # 最後まで成功しなかった場合該当データ削除
                self.__search_infos.pop(self.__author_list[self.__search_cnt])
                self.__author_list.pop(self.__search_cnt)
                # 結果なし
                divs = []
        # 検索ログ出力
        Debug.dprint("search author(" +  str(self.__search_cnt + 1) + "/" + str(self.get_author_list_num()) + ") -> " + self.__author_list[self.__search_cnt])
        # 検索数を進める
        self.__search_cnt += 1
        # ドライバ保持
        self.__web_drivers.append(driver)
        # 結果を返す
        return divs


    def cloase_driver(self) -> None:
        """ ドライバクローズ  
        生成したドライバを閉じる
        """
        # ドライバクローズ
        for driver in self.__web_drivers:
            driver.close()
            driver.quit()



    def __create_header(self) -> dict:
        """ リクエストヘッダ生成  
        リクエスト用のヘッダ情報を返す
        """
        return {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.99 Safari/537.36 Vivaldi/2.9.1705.41'}


    def __create_url_for_csv(self, filename:str) -> None:
        """  検索データ情報リスト生成(csvから生成)  
        著者名リストを生成．別途著者名をキーとしたハッシュマップを生成し，データとして検索開始日を保持する  
        [I] filename : 確認対象ファイル名  
        """
        Debug.tmpprint("func : create_url_for_csv")
        encode_str = "utf-8"
        csv_type = CsvUtil.is_utf8_file_with_bom(filename)
        if csv_type is CsvEncodeType.UTF_8_BOM:
            encode_str = "utf-8-sig"
        elif csv_type is CsvEncodeType.SHIFT_JIS:
            encode_str = "shift_jis"
        else:
            encode_str = "utf-8"
        serach_list_dict = {}
        # csv読込み
        with open(filename, mode="r", encoding=encode_str, newline="") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)   #  ヘッダ読み飛ばし
            # データ生成
            for row in reader:
                # dictionaryに著者名をキーとしてデータを保持
                if row[1] == "":
                    row[1] = datetime.datetime.today().strftime("%Y/%m/%d") # 期間が空白なら，実行日を設定
                serach_list_dict[row[0]] = row[1]
        # 結果を保持
        self.search_infos = serach_list_dict


    def __create_url_for_db(self) -> None:
        """  検索データ情報リスト生成(DBから生成)  
        著者名リストを生成．別途著者名をキーとしたハッシュマップを生成し，データとして検索開始日を保持する  
        [I] filename : 確認対象ファイル名  
        """
        Debug.tmpprint("func : __create_url_for_db")
        serach_list_dict = {}
        # DB読込み
        serach_info = self.__db_ctrl.get_db_search_list()
        # データ生成
        for row in serach_info:
            # dictionaryに著者名をキーとしてデータを保持
            if row.search_date is None:
                row.search_date = datetime.datetime.today().strftime("%Y/%m/%d") # 期間が空白なら，実行日を設定
            serach_list_dict[row.author_name] = row.search_date
        # 結果を保持
        self.search_infos = serach_list_dict

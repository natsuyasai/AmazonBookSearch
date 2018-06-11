#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
新刊検索クローリング関連
"""

# import ***************************************************************************
# 追加要 ***********
import requests     # webページ取得用
#*******************
import csv          # CSV読み書き
import urllib       # urlエンコード変換
import datetime     # 日付判定
#*******************
from debug_info import Debug
from csv_util import CsvUtil
from csv_util import CsvEncodeType
#***********************************************************************************

# Const Define *********************************************************************
AMAZON_SEARCH_URL = "https://www.amazon.co.jp/s/url=search-alias%3Dstripbooks&field-keywords="   # アマゾン検索用URL
# https://www.amazon.co.jp/s/ref=nb_sb_noss?__mk_ja_JP=カタカナ&url=search-alias%3Dstripbooks&field-keywords=
# https://www.amazon.co.jp/s/ref=nb_sb_noss?__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&url=search-alias%3Dstripbooks&field-keywords=

#***********************************************************************************

class BookInfoCrawling:

    @staticmethod
    def create_header() -> dict:
        """ リクエストヘッダ生成  
        リクエスト用のヘッダ情報を返す
        """
        return {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.183 Safari/537.36 Vivaldi/1.96.1147.42'}

    
    def create_url(self, name_data: dict) -> list:
        """ URL生成  
        著者名から検索用URLを生成する  
        [I] name_data : 著者名リスト  
        [O] list : URLリスト
        """
        Debug.tmpprint("func : create_url")
        url_list = []
        # 全key名でURLを生成し，listに保持
        for search_name in name_data.keys():
            Debug.tmpprint(search_name)
            url_list.append(AMAZON_SEARCH_URL + urllib.parse.quote(search_name.encode("utf-8"))) # 日本語を16進数に変換
        return url_list


    def create_search_info_list(self, filename) -> dict:
        """ 検索データ情報リストの生成  
        著者名リストを生成．別途著者名をキーとしたハッシュマップを生成し，データとして検索開始日を保持する  
        [I] filename : 確認対象ファイル名  
        [O] dict : キー=著者名，データ=検索開始日
        """
        Debug.tmpprint("func : create_search_info_list")
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
        return serach_list_dict
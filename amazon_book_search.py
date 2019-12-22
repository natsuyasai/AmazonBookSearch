#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
新刊チェックプログラム

"""
# import ***************************************************************************
# 追加要 ***********
import requests     # webページ取得用
#*******************
import csv          # CSV読み書き
import urllib       # urlエンコード変換
import datetime     # 日付判定
import re           # 文字列解析
import os           # ファイル確認
from typing import List
#*******************
from debug_info import Debug                    # デバッグ用
from book_info_crawling import BookInfoCrawling # クローリング関連
from book_info_scraping import BookInfoScraping # スクレイピング関連
from book_info_scraping import BookInfo         # 解析情報保持データ型
#***********************************************************************************

# Const Define *********************************************************************
READ_FILE_NAME = "search_list.csv"         # 読込みファイル名
#READ_FILE_NAME = " "
#***********************************************************************************

# エントリポイント @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
def main():
    Debug.tmpprint("Start\n")
    # ファイルチェック
    # ファイルが見つからなかった場合は，新規にファイルを作成し，終了する
    #if check_search_file(READ_FILE_NAME) == False:
    #    print("finish!")
    #    return
    
    # クローリング用クラス生成
    book_crawling = BookInfoCrawling()
    # DB設定
    #if book_crawling.set_table_key("nyasai") is False:
    #    print("finish!")
    #    return
    # 検索データ取得
    book_crawling.create_search_info_list(READ_FILE_NAME)
    # 著者リスト生成
    book_crawling.create_author_list()
    # 著者リスト保持
    target_author_list = book_crawling.get_author_list()
    # url生成
    url_list = book_crawling.create_url()
    # 検索
    all_book_infos: List[BookInfo] = []
    book_scraping = BookInfoScraping()
    search_cnt = 0
    for url in url_list:
        # 検索結果取得
        Debug.tmpprint(url)
        search_result_divs = book_crawling.exec_search(url)
        # 正常に結果が取得できた場合
        if len(search_result_divs) != 0:
            # 解析実行
            one_author_book_info = book_scraping.analysis_url(
                search_result_divs, target_author_list[search_cnt])
            # 結果をリストに保持
            all_book_infos.append(one_author_book_info)
            # 結果出力
            #output_result(one_author_book_info, book_crawling.get_author_list()[search_cnt], book_crawling.get_serch_info()[book_crawling.get_author_list()[search_cnt]])
            search_cnt += 1
            
    # ドライバクローズ
    book_crawling.cloase_driver()
    # 結果出力
    # TODO: 既に一度出力していれば無視するか？それとも毎回全上書きを行うか？
    # 既にファイルが有れば，そのファイルとの差分をとって結果を何かしらで通知．
    # ファイルがなければ全て通知
    output_result_for_csv(
        all_book_infos, book_crawling.get_author_list(), book_crawling.get_serch_info())
    output_result_for_html(
        all_book_infos, book_crawling.get_author_list(), book_crawling.get_serch_info())
    print("finish!")

#************************************************************************************************
# 関数実装部
#************************************************************************************************

def check_search_file(filename: str) -> bool:
    """ 検索リストファイル確認  
    ファイルが存在しなければ，新たに生成する  
    [I] filename : 確認対象ファイル名
    """
    Debug.tmpprint("func : check_search_file")
    if os.path.isfile(filename) == True:
        return True
    else:
        print("検索対象リストが見つかりません．新規に生成します．")
        # ファイル生成
        strs = "著者名(名字と名前の間は空白を入れないこと),取得開始期間(空なら実行日を開始日として取得)\n"
        with open(filename, mode="w", encoding="utf-8-sig" ,newline="") as csvfile:
            csvfile.write(strs)
        return False


def output_result_for_csv(all_book_infos: List[List[BookInfo]], author_list: List[str], output_date: dict):
    """ CSV書き込み  
    著者名と本リスト，URL，発売日，価格を保存する  
    [I] all_book_infos : 解析後の本情報(全著者分)，author_list : 著者名リスト，output_date : 出力対象の日付
    """
    Debug.tmpprint("func : output_result_for_csv")
    output_filename = "new_book_info_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".csv"
    #csvオープン
    with open(output_filename, mode="a", newline="", encoding='utf-8-sig') as csvfile:
        csvfile.write("著者名,タイトル,発売日,価格,商品URL\n")
        # 検索対象データ分ループ
        for author_cnt in range(0, len(author_list), 1):
            book_infos = all_book_infos[author_cnt]
            # 1検索対象データの結果リストから，著者名が一致するもののみを取得
            book_info_cnt = 0
            for book_info in book_infos:
                try:
                    if book_info.author.find(author_list[author_cnt]) != -1:
                        # 期間が指定日以降なら保存する
                        if datetime.datetime.strptime(book_info.date, "%Y/%m/%d") \
                            >= datetime.datetime.strptime(output_date[author_list[author_cnt]],"%Y/%m/%d"):
                            output_str=""
                            # 著者名
                            output_str += book_info.author + ","
                            # タイトル
                            output_str += book_info.title + ","
                            # 発売日
                            output_str += book_info.date + ","
                            # 価格
                            output_str += "\"" + book_info.price + "\","
                            # 商品URL
                            output_str += book_info.url + "\n"
                            csvfile.write(output_str)
                except IndexError:
                    print("IndexError!! -> " + book_info.author)
                    book_info_cnt -= 1
                    continue
                book_info_cnt += 1


def output_result_for_html(all_book_infos: List[List[BookInfo]], author_list: List[str], output_date: dict):
    """ HTML書き込み  
    著者名と本リスト，URL，発売日，価格を保存する  
    [I] all_book_infos : 解析後の本情報(全著者分)，author_list : 著者名リスト，output_date : 出力対象の日付
    """
    Debug.tmpprint("func : output_result_for_html")
    output_filename = "new_book_info_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".html"
    #csvオープン
    with open(output_filename, mode="a", newline="") as htmlfile:
        # 検索対象データ分ループ
        for author_cnt in range(0, len(author_list), 1):
            book_infos = all_book_infos[author_cnt]
            # 1検索対象データの結果リストから，著者名が一致するもののみを取得
            book_info_cnt = 0
            for book_info in book_infos:
                try:
                    if book_info.author.find(author_list[author_cnt]) != -1:
                        # 期間が指定日以降なら保存する
                        if datetime.datetime.strptime(book_info.date,"%Y/%m/%d") \
                            >= datetime.datetime.strptime(output_date[author_list[author_cnt]],"%Y/%m/%d"):
                            output_str=""
                            # 著者
                            output_str += book_info.author + "<br/>"
                            # タイトル
                            output_str += book_info.title + "<br/>"
                            # 発売日
                            output_str += book_info.date + "<br/>"
                            # 価格
                            output_str += book_info.price + "<br/>"
                            # 商品URL
                            output_str += '<a href="' + book_info.url + 'target="_blank"' +'">Link</a><br/><br/>'
                            htmlfile.write(output_str)
                except IndexError:
                    print("IndexError!! -> " + book_info.author)
                    book_info_cnt -= 1
                    continue
                book_info_cnt += 1



def output_result(book_info: BookInfo, search_author: str, output_date: str):
    """ 結果出力 
    著者名と本リスト，URL，発売日，価格を出力する  
    [I] book_info : 解析後の本情報(1著者)search_author : 著者名，output_date : 出力対象の日付
    """
    # 1検索対象データの結果リストから，著者名が一致するもののみを取得
    book_info_cnt = 0
    for author in book_info.author:
        # 著者名から空白文字を削除する
        author = author.replace(" ","")
        try:
            if author.find(search_author) != -1:
                # 期間が指定日以降なら保存する
                if datetime.datetime.strptime(book_info.date[book_info_cnt],"%Y/%m/%d") \
                    >= datetime.datetime.strptime(output_date, "%Y/%m/%d"):
                    output_str=""
                    output_str += author + "<br/>"                          # 著者名
                    output_str += book_info.title[book_info_cnt] + "<br/>"  # タイトル
                    output_str += book_info.date[book_info_cnt] + "<br/>"   # 発売日
                    #output_str += book_info.price[book_info_cnt] + "," # 価格
                    output_str += "<br/>"
                    output_str += '<a href="' + book_info.url[book_info_cnt] + '">Link</a><br/><br/>'   # 商品URL
                    print(output_str)
        except IndexError:
            print("IndexError!! -> " + author)
            book_info_cnt -= 1
            continue
        book_info_cnt += 1


# 実行
if __name__ == "__main__":
    main()

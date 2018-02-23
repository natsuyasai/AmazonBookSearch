#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
新刊チェックプログラム

実装メモ
 検索結果から，現在の日付以降の発売日となっている本の一覧を生成
 起動時にcsvが存在すれば，その一覧にある本は対象から省くようにする
"""
# import ***************************************************************************
import requests     # webページ取得用
import lxml.html    # webページ取得データ取得
import csv          # CSV読み書き
import urllib       # urlエンコード変換
import datetime     # 日付判定
import time         # wait用
import re           # 文字列解析
#***********************************************************************************

# Const Define *********************************************************************
READ_FILE_NAME = "search_list.csv"         # 読込みファイル名
AMAZON_SEARCH_URL = "https://www.amazon.co.jp/s/ref=nb_sb_noss?__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&url=search-alias%3Dstripbooks&field-keywords="   # アマゾン検索用URL
# https://www.amazon.co.jp/s/ref=nb_sb_noss?__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&url=search-alias%3Dstripbooks&field-keywords=
REQUEST_RETRY_NUM = 5   # リクエストリトライ回数
REQUEST_WAIT_TIME = 1   # リトライ待ち時間
#***********************************************************************************

# Struct ***************************************************************************
# 検索結果情報データ構造クラス
class BookInfo:
    def __init__(self):
        self.author = []        # 著者名
        self.title = []         # 書名
        self.date = []          # 発売日
        self.price = []         # 価格
        self.url = []           # 商品詳細ページへのURL
#***********************************************************************************
# Debug ****************************************************************************
# デバッグ関連クラス
class Debug:
    # ログ出力
    def dprint(self, print_data):
        print(print_data)
    
    # 一時出力
    def tmpprint(self, print_data):
        print(print_data)

# デバッグ出力関連クラスインスタンス
dbg = Debug()
#***********************************************************************************


# エントリポイント @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
def main():
    dbg.dprint("Start\n")
    # 検索データ取得
    search_infos = create_serach_info_list(READ_FILE_NAME)
    # 著者リスト生成
    author_list = []
    for author in search_infos.keys():
        author_list.append(author)
    # url生成
    url_list = create_url(search_infos)
    # 検索
    search_cnt = 0
    all_book_infos = []
    for url in url_list:
        # 検索結果取得
        dbg.tmpprint(url)
        search_result = requests.get(url)
        # 失敗時は一定時間待ってから再度取得を試みる
        if search_result.status_code != requests.codes["ok"]:
            is_ok = False
            for retry in range(1,REQUEST_RETRY_NUM,1):
                time.sleep(REQUEST_WAIT_TIME)
                search_result = requests.get(url)
                if search_result.status_code == requests.codes["ok"]:
                    is_ok = True
                    break
                else:
                    if retry == REQUEST_RETRY_NUM:
                        print("request err")
            if is_ok == False:
                continue # 最後までだめなら次へ
        # 解析
        all_book_infos.append(analysis_url(search_result))
        search_cnt+=1
    # 結果出力
    # TODO: 既に一度出力していれば無視するか？それとも毎回全上書きを行うか？
    write_csv(all_book_infos, author_list, search_infos)

    print("finish!")

#************************************************************************************************
# 関数実装部
#************************************************************************************************

# 検索データ情報リストの生成
# 著者名リストを生成．別途著者名をキーとしたハッシュマップを生成し，データとして検索開始日を保持する
def create_serach_info_list(filename) -> dict:
    dbg.dprint("func : create_serach_info_list")
    serach_list_dict = {}
    # csv読込み
    with open(filename, mode="r", encoding="utf-8",newline="") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)   #  ヘッダ読み飛ばし
        # データ生成
        for row in reader:
            # dictionaryに著者名をキーとしてデータを保持
            if row[1] == "":
                row[1] = datetime.datetime.today().strftime("%Y/%m/%d") # 期間が空白なら，実行日を設定
            serach_list_dict[row[0]] = row[1]
    return serach_list_dict


# CVS書き込み
# 著者名と本リスト，URL，発売日，価格を保存する
def write_csv(all_book_infos:list, author_list:list, output_date:dict):
    dbg.dprint("func : write_csv")
    # 出力文字リスト生成
    output_str=""
    book_info = BookInfo()
    # 検索対象データ分ループ
    for author_cnt in range(0, len(author_list), 1):
        book_info = all_book_infos[author_cnt]
        # 1検索対象データの結果リストから，著者名が一致するもののみを取得
        book_info_cnt = 0
        for author in book_info.author:
            # 著者名から空白文字を削除する
            author = author.replace(" ","")
            if author.find(author_list[author_cnt]) != -1:
                # 期間が指定日以降なら保存する
                if datetime.datetime.strptime(book_info.date[book_info_cnt],"%Y/%m/%d") \
                    >= datetime.datetime.strptime(output_date[author_list[author_cnt]],"%Y/%m/%d"):
                    output_str += author + ","                          # 著者名
                    output_str += book_info.title[book_info_cnt] + ","  # タイトル
                    output_str += book_info.date[book_info_cnt] + ","   # 発売日
                    #output_str += book_info.price[book_info_cnt] + "," # 価格
                    output_str += ","
                    output_str += book_info.url[book_info_cnt] + "\n"   # 商品URL
            book_info_cnt += 1
    #csvオープン
    with open("new_book_info.csv", mode="a", newline="") as csvfile:
        csvfile.write("著者名,タイトル,発売日,価格,商品URL\n")
        csvfile.write(output_str)

# URL生成
# 著者名から検索用URLを生成する
def create_url(name_data: dict) -> list:
    dbg.dprint("func : create_url")
    url_list = []
    # 全key名でURLを生成し，listに保持
    for search_name in name_data.keys():
        dbg.tmpprint(search_name)
        url_list.append(AMAZON_SEARCH_URL + urllib.parse.quote_plus(search_name,encoding="utf-8")) # 日本語を16進数に変換
    return url_list


# 検索結果解析
# 検索結果から以下を解析
# 本のタイトル
# 発売日
# 著者名
# 価格
# 商品ページへのURL
def analysis_url(html_info: requests.models.Response) -> BookInfo:
    dbg.dprint("func : analysis_url")
    dbg.tmpprint(html_info)
    # htmlパース
    html_info.raise_for_status()
    root = lxml.html.fromstring(html_info.text)
    #items = root.xpath("//div[contains(@class, 's-item-container')]") # 各商品部分取得
    book_info = BookInfo()
    # 情報解析/取得
    # タイトル
    book_info.title = get_book_title(root)
    # 発売日
    book_info.date = get_book_date(root)
    # 著者名
    book_info.author = get_book_author(root)
    # 価格
    #book_info.price = get_book_price(root)
    # 商品URL
    book_info.url = get_book_url(root, book_info.title)

    return book_info



# 本のタイトル取得
def get_book_title(html_item : lxml.html.HtmlElement) -> str:
    dbg.dprint("func : get_book_title")
    # 商品タイトル部分抽出
    title_list = []
    titles = html_item.xpath(
        "//div[contains(@class, 's-item-container')]"\
        "//div[contains(@class, 'a-row a-spacing-mini')]"\
        "//div[contains(@class, 'a-row a-spacing-none')]"\
        "//h2[contains(@class, 's-access-title')]")
    for title in titles:
        title_list.append(title.text_content().encode("utf-8").decode("utf-8"))
        dbg.tmpprint(title.text_content().encode("utf-8").decode("utf-8"))
    return title_list


# 本の発売日取得
def get_book_date(html_item : lxml.html.HtmlElement) -> str:
    dbg.dprint("func : get_book_date")
    date_list = []
    # 発売日部分取得
    dates = html_item.xpath(
        "//div[contains(@class, 's-item-container')]"\
        "//div[contains(@class, 'a-row a-spacing-mini')]"\
        "//div[contains(@class, 'a-row a-spacing-none')]"\
        "//span[contains(@class, 'a-size-small a-color-secondary')]")
    for date in dates:
        date_str = ""
        # 発売日以外の部分も引っかかってしまうため，日付情報に変換ができないものは弾く
        try:
            date_str = datetime.datetime.strptime(date.text_content().encode("utf-8").decode("utf-8"), "%Y/%m/%d").strftime("%Y/%m/%d")
        except ValueError:
            continue
        date_list.append(date_str)
        dbg.tmpprint(date_str)
    return date_list


# 本の著者名取得
def get_book_author(html_item : lxml.html.HtmlElement) -> str:
    dbg.dprint("func : get_book_author")
    # 著者名部分抽出
    # note. アマゾンの下記要素を取得すると，「日付→空白→著者名」の順に取得される．
    #       そのため，3要素目以降を取得するようにする
    author_list = []
    authors = html_item.xpath(
        "//div[contains(@class, 's-item-container')]"\
        "//div[contains(@class, 'a-row a-spacing-mini')]"\
        "//div[contains(@class, 'a-row a-spacing-none')]"\
        "//span[contains(@class, 'a-size-small a-color-secondary')]")
    data_cnt = 1
    for author in authors:
        # 日付でなく且つ空白でなければ著者情報
        try:
            datetime.datetime.strptime(author.text_content().encode("utf-8").decode("utf-8"), "%Y/%m/%d").strftime("%Y/%m/%d")
            data_cnt = 1
        except ValueError:
            tmp_str = author.text_content().encode("utf-8").decode("utf-8")
            if len(tmp_str) != 0:
                # 複数著者名
                if data_cnt == 4:
                    mult_author = author_list[-1]   # 末尾データ取得
                    author_list.pop()               # 末尾データ削除
                    author_list.append(mult_author + tmp_str)   # 最終データに現在の著者名をつなげた文字列とする
                else:
                    # 著者名保持
                    author_list.append(tmp_str)
                    dbg.tmpprint(tmp_str)
        data_cnt+=1
    return author_list


# 本の価格取得
def get_book_price(html_item : lxml.html.HtmlElement) -> str:
    dbg.dprint("func : get_book_price")
    # 価格部分抽出
    price_list = []
    prices = html_item.xpath(
        "//div[contains(@class, 's-item-container')]"\
        "//div[contains(@class, 'a-row a-spacing-none')]"\
        "//a[contains(@class, 'a-link-normal a-text-normal')]"\
        "//span[contains(@class, 'a-size-base a-color-price s-price a-text-bold')]")
    # TODO: Kindle版のものも取れてしまうが，どう切り分けるべきか．．．
    for price in prices:
        price_list.append(price.text_content().encode("utf-8").decode("utf-8"))
        dbg.tmpprint(price.text_content().encode("utf-8").decode("utf-8"))
    return price_list


# 本の商品ページURL取得
def get_book_url(html_item : lxml.html.HtmlElement, title_info:list) -> str:
    dbg.dprint("func : get_book_url")
    # URL部分抽出
    url_list = []
    urls = html_item.xpath(
        "//div[contains(@class, 's-item-container')]"\
        "//div[contains(@class, 'a-row a-spacing-mini')]"\
        "//div[contains(@class, 'a-row a-spacing-none')]"\
        "//a[contains(@class, 'a-link-normal s-access-detail-page  s-color-twister-title-link a-text-normal')]")
    title_cnt = 0
    is_get_url = False
    for url in urls:
        for item in url.items(): # hrefにURLがあるため，それを探索し，取得する
            # タイトルと一致するならばその1回だけURLを取得する
            if item[0] == "title" and item[1] == title_info[title_cnt]:
                is_get_url = True
                title_cnt += 1
            if item[0] == "href" and is_get_url == True:
                url_list.append(item[1])
                dbg.tmpprint(item[1])
                is_get_url = False
    return url_list


# 実行
if __name__ == "__main__":
    main()

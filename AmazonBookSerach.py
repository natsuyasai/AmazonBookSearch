#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
新刊チェックプログラム

実装メモ
 amazon検索プログラム
 ワードを別ファイルに登録．
 登録したワードをもとにamazonで検索
 検索結果から，現在の日付以降の発売日となっている本の一覧を生成
 一覧は同一ディレクトリにcsv形式で保存
 起動時にcsvが存在すれば，その一覧にある本は対象から省くようにする
"""
#************** import ***************
import requests     # webページ取得用
import lxml.html    # webページ取得データ取得
import csv          # CSV読み書き
import urllib       # urlエンコード変換
import datetime     # 日付判定
import time         # wait用
#*************************************

#************** Const Define ***************
READ_FILE_NAME = "SearchList.csv"         # 読込みファイル名
AMAZON_SEARCH_URL = "https://www.amazon.co.jp/s/ref=nb_sb_noss?__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&url=search-alias%3Dstripbooks&field-keywords="   # アマゾン検索用URL
# https://www.amazon.co.jp/s/ref=nb_sb_noss?__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&url=search-alias%3Dstripbooks&field-keywords=
REQUEST_RETRY_NUM = 5   # リクエストリトライ回数
REQUEST_WAIT_TIME = 1   # リトライ待ち時間


# 検索結果情報データ構造クラス
class BookInfo:
    def __init__(self):
        self.author = []        # 著者名
        self.title = []         # 書名
        self.date = []          # 発売日
        self.price = []         # 価格
        self.url = []           # 商品詳細ページへのURL

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


# 検索データ情報リストの生成
# 著者名リストを生成．別途著者名をキーとしたハッシュマップを生成し，データとして検索開始日を保持する
def create_serach_info_list(filename) -> dict:
    dbg.dprint("func : create_serach_info_list")
    serach_list_dict = {}
    # csv読込み
    with open(filename, encoding="UTF-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)   #  ヘッダ読み飛ばし
        # データ生成
        for row in reader:
            # dictionaryに著者名をキーとしてデータを保持
            serach_list_dict[row[0]] = row[1]
    return serach_list_dict


# CVS書き込み
# 著者名と本リスト，URL，発売日，価格を保存する
def write_csv():
    dbg.dprint("func : write_csv")

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
def analysis_url(html_info: requests.models.Response, author_info:str) -> list:
    dbg.dprint("func : analysis_url")
    dbg.tmpprint(html_info)
    # htmlパース
    html_info.raise_for_status()
    root = lxml.html.fromstring(html_info.text)
    items = root.xpath("//div[contains(@class, 's-item-container')]") # 各商品部分取得
    # note. ex) divs[0][2][0][0][0].items()[0] -> タイトル
    book_analysis_info = [] # 解析後の情報(BookInfoを格納する)
    for item in items:
        book_info = BookInfo()
        # 情報解析/取得
        # タイトル
        book_info.title = get_book_title(item, author_info)
        # 発売日
        book_info.date = get_book_date(item, author_info)
        # 著者名
        book_info.author = get_book_author(item, author_info)
        # 価格
        book_info.price = get_book_price(item, author_info)
        # 商品URL
        book_info.url = get_book_url(item, author_info)
        # 情報保持
        book_analysis_info.append(book_info)
        # 文字列に変換(日本語が16進数表記になるため，デコードを行う)
        #dbg.tmpprint(item.text_content().encode("utf-8").decode("utf-8"))
    return book_analysis_info

# 本のタイトル取得
def get_book_title(html_item : lxml.html.HtmlElement, author_info:str) -> str:
    dbg.dprint("func : get_book_title")
    # 商品タイトル部分抽出
    #temp_infos = html_item.xpath("//div[contains(@class, 'a-spacing-mini')]")
    title_list = []
    titles = html_item.xpath("//div//div//h2[contains(@class, 's-access-title')]")
    for title in titles:
        title_list.append(title.text_content().encode("utf-8").decode("utf-8"))
        dbg.tmpprint(title.text_content().encode("utf-8").decode("utf-8"))
    return title_list

# 本の発売日取得
def get_book_date(html_item : lxml.html.HtmlElement, author_info:str) -> str:
    dbg.dprint("func : get_book_date")
    date_list = []
    dates = html_item.xpath("//div[contains(@class, 'a-row a-spacing-mini')]//div[contains(@class, 'a-row a-spacing-none')]//span[contains(@class, 'a-size-small a-color-secondary')]")
    for date in dates:
        date_str = ""
        try:
            date_str = datetime.datetime.strptime(date.text_content().encode("utf-8").decode("utf-8"), "%Y/%m/%d").strftime("%Y/%m/%d")
        except ValueError:
            continue
        date_list.append(date_str)
        dbg.tmpprint(date_str)
    return date_list

# 本の著者名取得
def get_book_author(html_item : lxml.html.HtmlElement, author_info:str) -> str:
    dbg.dprint("func : get_book_author")
    return ""

# 本の価格取得
def get_book_price(html_item : lxml.html.HtmlElement, author_info:str) -> str:
    dbg.dprint("func : get_book_price")
    return ""

# 本の商品ページURL取得
def get_book_url(html_item : lxml.html.HtmlElement, author_info:str) -> str:
    dbg.dprint("func : get_book_url")
    return ""

# エントリポイント
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
    for url in url_list:
        # 検索結果取得
        dbg.tmpprint(url)
        search_result = requests.get(url)
        # 失敗時は一定時間待ってから再度取得を試みる
        if search_result.status_code != requests.codes["ok"]:
            for retry in range(1,REQUEST_RETRY_NUM,1):
                time.sleep(REQUEST_WAIT_TIME)
                search_result = requests.get(url)
                if search_result.status_code == requests.codes["ok"]:
                    break
                else:
                    if retry == REQUEST_RETRY_NUM:
                        print("request err")
            continue
        # 解析
        analysis_url(search_result, author_list[search_cnt])
        search_cnt+=1
    
    print("finish!")

if __name__ == "__main__":
    main()

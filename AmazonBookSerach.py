#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
新刊チェックプログラム

使用パッケージ
Webページを取得する：requests
Webページからデータを抜き出す：lxml
Webページの自動操作：selenium

戻り値指定
def hoge() -> int:
    return hogehoge
"""
"""
実装メモ
 amazon検索プログラム
 ワードを別ファイルに登録．
 登録したワードをもとにamazonで検索
 検索結果から，現在の日付以降の発売日となっている本の一覧を生成
 一覧は同一ディレクトリにcsv形式で保存
 起動時にcsvが存在すれば，その一覧にある本は対象から省くようにする
"""
#************** import ***************
import requests # webページ取得用
import lxml     # webページ取得データ取得
import csv      # CSV読み書き
import urllib   # urlエンコード変換
import bs4
#*************************************

#************** Const Define ***************
READ_FILE_NAME = "SearchList.csv"         # 読込みファイル名
AMAZON_SEARCH_URL = "https://www.amazon.co.jp/s/ref=nb_sb_noss?__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&url=search-alias%3Dstripbooks&field-keywords="   # アマゾン検索用URL
# https://www.amazon.co.jp/s/ref=nb_sb_noss?__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&url=search-alias%3Dstripbooks&field-keywords=

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


# CSV読み込み
def read_csv(filename: str, is_read_header : bool) -> dict:
    dbg.dprint("read_csv")
    # csv読込み
    with open(filename, encoding="UTF-8") as csvfile:
        reader = csv.reader(csvfile)
        if is_read_header is False:
            next(reader)   #  ヘッダ読み飛ばし
    return reader

# 検索データ情報リストの生成
# 著者名リストを生成．別途著者名をキーとしたハッシュマップを生成し，データとして検索開始日を保持する
def create_serach_info_list(filename) -> dict:
    dbg.dprint("create_serach_info_list")
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


# URL生成
# 著者名から検索用URLを生成する
def create_url(name_data: dict) -> list:
    dbg.dprint("create_url")
    url_list = []
    # 全key名でURLを生成し，listに保持
    for search_name in name_data.keys():
        dbg.tmpprint(search_name)
        url_list.append(AMAZON_SEARCH_URL + urllib.parse.quote_plus(search_name,encoding="utf-8")) # 日本語を16進数に変換
    return url_list


# 検索結果取得
# 生成したURLから検索した結果を取得する


# 検索結果解析
# 検索結果から以下を解析
# 本のタイトル
# 発売日
# 著者名
# 価格
# 商品ページへのURL

# 本のタイトル取得

# 本の発売日取得

# 本の著者名取得

# 本の価格取得

# 本の商品ページURL取得

# エントリポイント
def main():
    dbg.dprint("Start\n")
    # 検索データ取得
    search_infos = create_serach_info_list(READ_FILE_NAME)
    # url生成
    url_list = create_url(search_infos)
    # 検索
    for url in url_list:
        # 検索結果取得
        dbg.tmpprint(url)
        search_result = requests.get(url)
        #debug_log(search_result.text)
        # htmlパース
        search_result.raise_for_status()
        soup = bs4.BeautifulSoup(search_result.text, "html.parser")
        dbg.tmpprint(soup.title)
    

if __name__ == "__main__":
    main()

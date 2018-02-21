#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
新刊チェックプログラム

使用パッケージ
Webページを取得する：requests
Webページからデータを抜き出す：lxml
Webページの自動操作：selenium
ファイル読込み/書込み：pandas

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
#*************************************

#************** Const Define ***************
READ_FILE_NAME = "SearchList.csv"         # 読込みファイル名
AMAZON_SEARCH_URL = "https://www.google.co.jp/search?&q="   # アマゾン検索用URL


# ログ出力
def debug_log(print_data):
    print(print_data)

# CSV読み込み
def read_csv(filename: str, is_read_header : bool) -> dict:
    debug_log("read_csv")
    # csv読込み
    with open(filename, encoding="UTF-8") as csvfile:
        reader = csv.reader(csvfile)
        if is_read_header is False:
            next(reader)   #  ヘッダ読み飛ばし
    return reader

# 検索データ情報リストの生成
# 著者名リストを生成．別途著者名をキーとしたハッシュマップを生成し，データとして検索開始日を保持する
def create_serach_info_list(filename) -> dict:
    debug_log("create_serach_info_list")
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
def create_url(name_list: dict) -> list:
    debug_log("create_url")
    url_list = []
    # 全key名でURLを生成し，listに保持
    for search_name in list(name_list.keys):
        debug_log(search_name)
        url_list.append(AMAZON_SEARCH_URL+search_name)
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
    debug_log("Start\n")
    # 検索データ取得
    search_infos = create_serach_info_list(READ_FILE_NAME)
    print(search_infos.keys())
    """
    url_list = create_url(search_dict)
    for name in url_list:
        print(name)
        #rtn = requests.get(name)
        #print(rtn.text)
        """
    

if __name__ == "__main__":
    main()

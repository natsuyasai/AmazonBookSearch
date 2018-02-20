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
import pandas   # CSV読み書き
from enum import Enum
#*************************************

#************** Const Define ***************
READ_FILE_NAME = "SearchList.csv"         # 読込みファイル名
COL_CAPT_NAME=["著者名","取得開始期間"]      # 読込みファイルの列名
AUTHOR_NAME=0                             # 著者名インデックス 
START_DATE=1                              # 期間インデックス

# ログ出力
def debug_log(print_data):
    print(print_data)

# CSV読み込み
# 著者名リストを生成．別途著者名をキーとしたハッシュマップを生成し，データとして検索開始日を保持する
def read_csv(filename: str):
    # csv読込み
    csv_data = pandas.read_csv(
        filename,           # ファイル名
        encoding="UTF-8",   # エンコード
        header=0,           # ヘッダ行
        names=[             # ヘッダキャプション名
            COL_CAPT_NAME[AUTHOR_NAME],COL_CAPT_NAME[START_DATE]
            ]
        )
    debug_log(csv_data[COL_CAPT_NAME[AUTHOR_NAME]])
    debug_log(csv_data[COL_CAPT_NAME[START_DATE]])


# CVS書き込み
# 著者名と本リスト，URL，発売日，価格を保存する


# URL生成
# 著者名から検索用URLを生成する


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
    debug_log("エントリポイント\n")
    # csvファイル読込み
    read_csv(READ_FILE_NAME)
    

if __name__ == "__main__":
    main()
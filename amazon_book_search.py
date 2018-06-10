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
import time         # wait用
import re           # 文字列解析
import os           # ファイル確認
from enum import Enum # 列挙型用
#*******************
from debug_info import Debug
from book_info_scraping import BookInfoScraping
#***********************************************************************************

# Const Define *********************************************************************
READ_FILE_NAME = "search_list.csv"         # 読込みファイル名
AMAZON_SEARCH_URL = "https://www.amazon.co.jp/s/url=search-alias%3Dstripbooks&field-keywords="   # アマゾン検索用URL
# https://www.amazon.co.jp/s/ref=nb_sb_noss?__mk_ja_JP=カタカナ&url=search-alias%3Dstripbooks&field-keywords=
# https://www.amazon.co.jp/s/ref=nb_sb_noss?__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&url=search-alias%3Dstripbooks&field-keywords=

# LINE通知用
LINE_NOTIFY_TOKEN = ''
LINE_NOTIFY_API = 'https://notify-api.line.me/api/notify'


REQUEST_RETRY_NUM = 5   # リクエストリトライ回数
REQUEST_WAIT_TIME = 10  # リトライ待ち時間(s)

class CsvEncodeType(Enum):
    UTF_8 = 0
    UTF_8_BOM = 1
    SHIFT_JIS = 2
#***********************************************************************************

# Struct ***************************************************************************
#***********************************************************************************
# Debug ****************************************************************************
# デバッグ出力関連クラスインスタンス
dbg = Debug()
#***********************************************************************************

# エントリポイント @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
def main():
    dbg.tmpprint("Start\n")
    # ファイルチェック
    # ファイルが見つからなかった場合は，新規にファイルを作成し，終了する
    if check_search_file(READ_FILE_NAME) == False:
        print("finish!")
        return
    # 検索データ取得
    search_infos = create_search_info_list(READ_FILE_NAME)
    # 著者リスト生成
    author_list = []
    for author in search_infos.keys():
        author_list.append(author)
    # url生成
    url_list = create_url(search_infos)
    author_num = len(author_list)
    # 検索
    search_cnt = 0
    all_book_infos = []
    book_scraping = BookInfoScraping()

    for url in url_list:
        # 検索結果取得
        dbg.tmpprint(url)
        search_result = requests.get(url)
        # 失敗時は一定時間待ってから再度取得を試みる
        if search_result.status_code != requests.codes["ok"]:
            is_ok = False
            for retry in range(0,REQUEST_RETRY_NUM,1):
                time.sleep(REQUEST_WAIT_TIME *( retry+1))
                search_result = requests.get(url)
                if search_result.status_code == requests.codes["ok"]:
                    is_ok = True
                    break
                else:
                    if retry == REQUEST_RETRY_NUM:
                        print("request err -> " + author_list[search_cnt])
            if is_ok == False:
                # 該当データ削除
                search_infos.pop(author_list[search_cnt])
                author_list.pop(search_cnt)
                continue # 最後までだめなら次へ
        # 解析
        print("search author(" +  str(search_cnt + 1) + "/" + str(author_num) + ") -> " + author_list[search_cnt])
        all_book_infos.append(book_scraping.analysis_url(search_result))
        search_cnt+=1
        #time.sleep(10) # 連続アクセスを避けるために少し待つ

    # 結果出力
    # TODO: 既に一度出力していれば無視するか？それとも毎回全上書きを行うか？
    # 既にファイルが有れば，そのファイルとの差分をとって結果を何かしらで通知．
    # ファイルがなければ全て通知
    write_csv(all_book_infos, author_list, search_infos)
    print("finish!")

#************************************************************************************************
# 関数実装部
#************************************************************************************************
def line_notifycate(ntf_str):
    """ LINE通知処理  
    LINEへ通知メッセージを送信する  
    [I] ntf_str : 通知内容
    """
    return
    #payload = {'message': ntf_str}
    #headers = {'Authorization': 'Bearer ' + LINE_NOTIFY_TOKEN}  # 発行したトークン
    #line_ntf_result = requests.post(LINE_NOTIFY_API, data=payload, headers=headers)


def check_search_file(filename) -> bool:
    """ 検索リストファイル確認  
    ファイルが存在しなければ，新たに生成する  
    [I] filename : 確認対象ファイル名
    """
    dbg.tmpprint("func : check_search_file")
    if os.path.isfile(filename) == True:
        return True
    else:
        print("検索対象リストが見つかりません．新規に生成します．")
        # ファイル生成
        strs = "著者名(名字と名前の間は空白を入れないこと),取得開始期間(空なら実行日を開始日として取得)\n"
        with open(filename, mode="w", encoding="utf-8-sig" ,newline="") as csvfile:
            csvfile.write(strs)
        return False


def is_utf8_file_with_bom(filename) -> CsvEncodeType:
    """ BOM確認用関数  
    [I] filename : 確認対象ファイル名  
    [O] SHIFT_JIS : sjis  
    [O] UTF_8_BOM : UTF8BOM付き
    [O] UTF_8 : UTF8
    """
    with open(filename, mode="r", encoding="utf-8",newline="") as csvfile:
        temp = csv.reader(csvfile)
        try:
            line = next(temp)
        except:
            return CsvEncodeType.SHIFT_JIS # UTF8以外であった
        if line[0].find("\ufeff") != -1:
            return CsvEncodeType.UTF_8_BOM # BOM付き
    return CsvEncodeType.UTF_8 # UTF-8 BOMなし


def create_url(name_data: dict) -> list:
    """ URL生成  
    著者名から検索用URLを生成する  
    [I] name_data : 著者名リスト  
    [O] list : URLリスト
    """
    dbg.tmpprint("func : create_url")
    url_list = []
    # 全key名でURLを生成し，listに保持
    for search_name in name_data.keys():
        dbg.tmpprint(search_name)
        url_list.append(AMAZON_SEARCH_URL + urllib.parse.quote(search_name.encode("utf-8"))) # 日本語を16進数に変換
    return url_list



def create_search_info_list(filename) -> dict:
    """ 検索データ情報リストの生成  
    著者名リストを生成．別途著者名をキーとしたハッシュマップを生成し，データとして検索開始日を保持する  
    [I] filename : 確認対象ファイル名  
    [O] dict : キー=著者名，データ=検索開始日
    """
    dbg.tmpprint("func : create_search_info_list")
    encode_str = "utf-8"
    csv_type = is_utf8_file_with_bom(filename)
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


def write_csv(all_book_infos:list, author_list:list, output_date:dict):
    """ CSV書き込み  
    著者名と本リスト，URL，発売日，価格を保存する  
    [I] all_book_infos : 解析後の本情報(全著者分)，author_list : 著者名リスト，output_date : 出力対象の日付
    """
    dbg.tmpprint("func : write_csv")
    output_filename = "new_book_info_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".csv"
    #csvオープン
    with open(output_filename, mode="a", newline="") as csvfile:
        csvfile.write("著者名,タイトル,発売日,価格,商品URL\n")
        # 出力文字リスト生成
        book_info = BookInfo()
        # 検索対象データ分ループ
        for author_cnt in range(0, len(author_list), 1):
            book_info = all_book_infos[author_cnt]
            # 1検索対象データの結果リストから，著者名が一致するもののみを取得
            book_info_cnt = 0
            for author in book_info.author:
                # 著者名から空白文字を削除する
                author = author.replace(" ","")
                try:
                    if author.find(author_list[author_cnt]) != -1:
                        # 期間が指定日以降なら保存する
                        if datetime.datetime.strptime(book_info.date[book_info_cnt],"%Y/%m/%d") \
                            >= datetime.datetime.strptime(output_date[author_list[author_cnt]],"%Y/%m/%d"):
                            output_str=""
                            output_str += author + ","                          # 著者名
                            output_str += book_info.title[book_info_cnt] + ","  # タイトル
                            output_str += book_info.date[book_info_cnt] + ","   # 発売日
                            #output_str += book_info.price[book_info_cnt] + "," # 価格
                            output_str += ","
                            output_str += book_info.url[book_info_cnt] + "\n"   # 商品URL
                            csvfile.write(output_str)
                            line_notifycate(output_str) # 通知
                except IndexError:
                    print("IndexError!! -> " + author)
                    book_info_cnt -= 1
                    continue
                book_info_cnt += 1


# 実行
if __name__ == "__main__":
    main()

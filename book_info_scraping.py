#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
新刊チェックプログラム  
スクレイピング処理実行関連

"""
# import ***************************************************************************
# 追加要 ***********
import requests     # webページ取得用
import lxml.html    # webページ取得データ取得
#*******************
import datetime     # 日付判定
import re           # 文字列解析
from debug_info import Debug
#***********************************************************************************

# Const Define *********************************************************************

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

class BookInfoScraping:
    def analysis_url(self, html_info: requests.models.Response) -> BookInfo:
        """ 検索結果解析
        検索結果から以下を解析  
        本のタイトル  
        発売日  
        著者名  
        価格  
        商品ページへのURL  
        [I] html_info : requets.get結果  
        [O] BookInfo : 解析結果
        """
        Debug.tmpprint("func : analysis_url")
        Debug.tmpprint(html_info)
        # htmlパース
        html_info.raise_for_status()
        root = lxml.html.fromstring(html_info.text)
        book_info = BookInfo()
        # 情報解析/取得
        # タイトル
        book_info.title = self.__get_book_title(root)
        # 発売日
        book_info.date = self.__get_book_date(root)
        # 著者名
        book_info.author = self.__get_book_author(root)
        # 価格
        #book_info.price = self.__get_book_price(root)
        # 商品URL
        book_info.url = self.__get_book_url(root, book_info.title)

        return book_info


    def __get_book_title(self, html_item : lxml.html.HtmlElement) -> list:
        """ 本のタイトル取得  
        [I] html_item : htmlデータ  
        [O] list : 本のタイトルリスト
        """
        Debug.tmpprint("func : get_book_title")
        # 商品タイトル部分抽出
        title_list = []
        titles = html_item.xpath(
            "//div[contains(@class, 'sg-row')]"\
            "//div[contains(@class, 'sg-col-inner')]"
            "//div[contains(@class, 'a-section a-spacing-none')]"\
            "//h2[contains(@class, 'a-size-mini a-spacing-none a-color-base s-line-clamp-2')]"\
            "//span[contains(@class, 'a-size-medium a-color-base a-text-normal')]")
        for title in titles:
            title_list.append(title.text_content().encode("utf-8").decode("utf-8"))
            Debug.tmpprint(title.text_content().encode("utf-8").decode("utf-8"))
        return title_list


    def __get_book_date(self, html_item : lxml.html.HtmlElement) -> list:
        """ 本の発売日取得  
        [I] html_item : htmlデータ  
        [O] list : 本の発売日リスト
        """
        Debug.tmpprint("func : get_book_date")
        date_list = []
        # 発売日部分取得
        dates = html_item.xpath(
            "//div[contains(@class, 'sg-row')]"\
            "//div[contains(@class, 'sg-col-inner')]"\
            "//div[contains(@class, 'a-section a-spacing-none')]"\
            "//div[contains(@class, 'a-row a-size-base a-color-secondary')]"\
            "//span[contains(@class, 'a-size-base a-color-secondary a-text-normal')]")
        for date in dates:
            date_str = ""
            # 発売日以外の部分も引っかかってしまうため，日付情報に変換ができないものは弾く
            try:
                date_str = datetime.datetime.strptime(date.text_content().encode("utf-8").decode("utf-8"), "%Y/%m/%d").strftime("%Y/%m/%d")
            except ValueError:
                try:
                    date_str = datetime.datetime.strptime(date.text_content().encode("utf-8").decode("utf-8"), "%Y/%m").strftime("%Y/%m/%d")
                except ValueError:
                    continue
            date_list.append(date_str)
            Debug.tmpprint(date_str)
        return date_list


    def __get_book_author(self, html_item : lxml.html.HtmlElement) -> list:
        """ 本の著者名取得  
        [I] html_item : htmlデータ  
        [O] list : 本の著者名リスト
        """
        Debug.tmpprint("func : get_book_author")
        # 著者名部分抽出
        author_list = []
        authors = html_item.xpath(
            "//div[contains(@class, 'sg-row')]"\
            "//div[contains(@class, 'sg-col-inner')]"\
            "//div[contains(@class, 'a-section a-spacing-none')]"\
            "//div[contains(@class, 'a-row a-size-base a-color-secondary')]"\
            "//a[contains(@class, 'a-size-base a-link-normal')]")
        data_cnt = 1
        for author in authors:
            tmp_str = author.text_content().encode("utf-8").decode("utf-8")
            # 改行と空白を削除
            tmp_str = tmp_str.replace("\n", "")
            tmp_str = tmp_str.replace(" ", "")
            if len(tmp_str) != 0:
                # 複数著者名
                if data_cnt == 4:
                    mult_author = author_list[-1]   # 末尾データ取得
                    author_list.pop()               # 末尾データ削除
                    author_list.append(mult_author + tmp_str)   # 最終データに現在の著者名をつなげた文字列とする
                else:
                    # 著者名保持
                    author_list.append(tmp_str)
                    Debug.tmpprint(tmp_str)
            data_cnt+=1
        return author_list


    def __get_book_price(self, html_item : lxml.html.HtmlElement) -> list:
        """ 本の価格取得  
        [I] html_item : htmlデータ  
        [O] list : 本の価格リスト
        """
        Debug.tmpprint("func : get_book_price")
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
            Debug.tmpprint(price.text_content().encode("utf-8").decode("utf-8"))
        return price_list


    # 本の商品ページURL取得
    def __get_book_url(self, html_item : lxml.html.HtmlElement, title_info:list) -> list:
        """ 本の商品ページURL取得  
        [I] html_item : htmlデータ  
        [O] list : 本の商品ページリスト
        """
        Debug.tmpprint("func : get_book_url")
        # URL部分抽出
        url_list = []
        urls = html_item.xpath(
            "//div[contains(@class, 'sg-row')]"\
            "//div[contains(@class, 'sg-col-inner')]"\
            "//div[contains(@class, 'a-section a-spacing-none')]"\
            "//h2[contains(@class, 'a-size-mini a-spacing-none a-color-base s-line-clamp-2')]"\
            "//a[contains(@class, 'a-link-normal a-text-normal')]"\
            "//@href")
        LINK_URL = "https://www.amazon.co.jp"
        for url in urls:
            url_list.append(LINK_URL + url)
            Debug.tmpprint(LINK_URL + url)
        return url_list

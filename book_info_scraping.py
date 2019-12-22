#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
新刊チェックプログラム  
スクレイピング処理実行関連

"""
# import ***************************************************************************
# 追加要 ***********
import lxml.html    # webページ取得データ取得
from selenium import webdriver
#*******************
import datetime     # 日付判定
import re           # 文字列解析
from typing import List
from debug_info import Debug
#***********************************************************************************

# Const Define *********************************************************************

#***********************************************************************************

# Struct ***************************************************************************
# 検索結果情報データ構造クラス
class BookInfo:
    def __init__(self):
        self.author: str = ''        # 著者名
        self.title: str = ''         # 書名
        self.date: str = ''          # 発売日
        self.price: str = ''         # 価格
        self.url: str = ''           # 商品詳細ページへのURL
#***********************************************************************************

class BookInfoScraping:
    def analysis_url(self, divs: List[webdriver.remote.webelement.WebElement], target_author: str) -> List[BookInfo]:
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
        book_infos: List[BookInfo] = []
        # 情報解析/取得
        for div in divs:
            book_info = BookInfo()
            # 著者名
            book_info.author = self.__get_book_author(div)
            # TODO:著者名が検索対象と一致しなければとばす
            #      マッチ条件どうするか
            #if book_info.author != target_author:
            #    continue
            # タイトル
            book_info.title = self.__get_book_title(div)
            # 発売日
            book_info.date = self.__get_book_date(div)
            # 価格
            book_info.price = self.__get_book_price(div)
            # 商品URL
            book_info.url = self.__get_book_url(div, book_info.title)
            # 結果保持
            book_infos.append(book_info)

        return book_infos


    def __get_book_title(self, div: webdriver.remote.webelement.WebElement) -> str:
        """ 本のタイトル取得  
        [I] div : htmlデータ  
        [O] list : 本のタイトルリスト
        """
        Debug.tmpprint("func : get_book_title")
        # 商品タイトル部分抽出
        html_element = lxml.html.fromstring(div.get_attribute('innerHTML'))
        titles = html_element.xpath(
            "//div[contains(@class, 'sg-row')]"
            "//div[contains(@class, 'sg-col-inner')]"
            "//div[contains(@class, 'a-section a-spacing-none')]"
            "//h2[contains(@class, 'a-size-mini a-spacing-none a-color-base s-line-clamp-2')]"
            "//span[contains(@class, 'a-size-medium a-color-base a-text-normal')]")
        formatting_title_str: str = ""
        for title in titles:
            formatting_title_str = title.text_content().encode("utf-8").decode("utf-8")
            Debug.tmpprint(formatting_title_str)
            break
        return formatting_title_str


    def __get_book_date(self, div: webdriver.remote.webelement.WebElement) -> str:
        """ 本の発売日取得 
        [I] div : htmlデータ  
        [O] list : 本の発売日リスト
        """
        Debug.tmpprint("func : get_book_date")
        # 発売日部分取得
        html_element = lxml.html.fromstring(div.get_attribute('innerHTML'))
        dates = html_element.xpath(
            "//div[contains(@class, 'sg-row')]"\
            "//div[contains(@class, 'sg-col-inner')]"\
            "//div[contains(@class, 'a-section a-spacing-none')]"\
            "//div[contains(@class, 'a-row a-size-base a-color-secondary')]"\
            "//span[contains(@class, 'a-size-base a-color-secondary a-text-normal')]")
        formatting_title_str: str = ""
        for date in dates:
            formatting_title_str = datetime.datetime.strptime(date.text_content().encode(
                "utf-8").decode("utf-8"), "%Y/%m/%d").strftime("%Y/%m/%d")
            Debug.tmpprint(formatting_title_str)
            break
        return formatting_title_str


    def __get_book_author(self, div: webdriver.remote.webelement.WebElement) -> str:
        """ 本の著者名取得  
        [I] div : htmlデータ  
        [O] list : 本の著者名リスト
        """
        Debug.tmpprint("func : get_book_author")
        # 著者名部分抽出
        html_element = lxml.html.fromstring(div.get_attribute('innerHTML'))
        authors_link = html_element.xpath(
                "//div[contains(@class, 'sg-row')]"\
                "//div[contains(@class, 'sg-col-inner')]"\
                "//div[contains(@class, 'a-section a-spacing-none')]"\
                "//div[contains(@class, 'a-row a-size-base a-color-secondary')]"\
                "//a[contains(@class, 'a-size-base')]")
        authors_nonlink = html_element.xpath(
            "//div[contains(@class, 'sg-row')]"
            "//div[contains(@class, 'sg-col-inner')]"
            "//div[contains(@class, 'a-section a-spacing-none')]"
            "//div[contains(@class, 'a-row a-size-base a-color-secondary')]"
            "//span[contains(@class, 'a-size-base')]")
        formatting_author_str: str = ""
        is_continue = lambda target_str: target_str == "" or target_str == "、 " or target_str == ", "
        is_break = lambda target_str: target_str == " | "
        for author in authors_link:
            tmp_str = author.text_content().encode("utf-8").decode("utf-8")
            # 無効，区切りは無視
            if is_continue(tmp_str):
                continue
            # 日付との区切り部分のため終了
            if is_break(tmp_str):
                break
            # 改行と空白を削除
            tmp_str = tmp_str.replace("\n", "")
            tmp_str = tmp_str.replace(" ", "")
            formatting_author_str = tmp_str
            Debug.tmpprint(formatting_author_str)

        for author in authors_nonlink:
            tmp_str = author.text_content().encode("utf-8").decode("utf-8")
            # 無効，区切りは無視
            if is_continue(tmp_str):
                continue
            # 日付との区切り部分のため終了
            if is_break(tmp_str):
                break
            # 改行と空白を削除
            tmp_str = tmp_str.replace("\n", "")
            tmp_str = tmp_str.replace(" ", "")
            # 現状保持無しなら新規追加
            if len(formatting_author_str) == 0:
                formatting_author_str  = tmp_str
            else:
                # 保持していれば文字列追加
                formatting_author_str += ("、" + tmp_str)
            Debug.tmpprint(formatting_author_str)   
        return formatting_author_str


    def __get_book_price(self, div: webdriver.remote.webelement.WebElement) -> str:
        """ 本の価格取得  
        [I] div : htmlデータ  
        [O] list : 本の価格リスト
        """
        Debug.tmpprint("func : get_book_price")
        # 価格部分抽出
        html_element = lxml.html.fromstring(div.get_attribute('innerHTML'))
        prices = html_element.xpath(
            "//div[contains(@class, 'sg-row')]"\
            "//div[contains(@class, 'sg-col-inner')]"\
            "//div[contains(@class, 'a-row')]"\
            "//span[contains(@class, 'a-price')]"
            "//span[contains(@class, 'a-offscreen')]")
        formatting_author_str: str = ""
        for price in prices:
            formatting_author_str = price.text_content().encode("utf-8").decode("utf-8")
            Debug.tmpprint(formatting_author_str)
            break
        return formatting_author_str


    def __get_book_url(self, div: webdriver.remote.webelement.WebElement, title_info: list) -> str:
        """ 本の商品ページURL取得  
        [I] div : htmlデータ  
        [O] list : 本の商品ページリスト
        """
        Debug.tmpprint("func : get_book_url")
        # URL部分抽出
        html_element = lxml.html.fromstring(div.get_attribute('innerHTML'))
        urls = html_element.xpath(
            "//div[contains(@class, 'sg-row')]"\
            "//div[contains(@class, 'sg-col-inner')]"\
            "//div[contains(@class, 'a-section a-spacing-none')]"\
            "//h2[contains(@class, 'a-size-mini a-spacing-none a-color-base s-line-clamp-2')]"\
            "//a[contains(@class, 'a-link-normal a-text-normal')]"\
            "//@href")
        LINK_URL = "https://www.amazon.co.jp"
        result_url_str = ""
        for url in urls:
            result_url_str = LINK_URL + url
            Debug.tmpprint(result_url_str)
            break
        return result_url_str

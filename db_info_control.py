#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
検索情報DB制御

"""
# import ***************************************************************************
import sqlite3          # DB
#***********************************************************************************

# Const Define *********************************************************************
DB_FILE_NAME = "book_info.db"
USER_INFO = "user_info"     # ユーザ情報テーブル名
BOOK_INFO = "_book_info"    # 検索対象情報テーブル名
#***********************************************************************************

# Struct ***************************************************************************
class DBAuthorInfo:
    def __init__(self):
        self.author_name = ""
        self.search_date = ""
#***********************************************************************************


class DBInfoCntrl:

    def __init__(self):
        """  コンストラクタ
        """
        self.__db_conection = None    # DBファイルコネクション
        self.__user_info_tbl_name = USER_INFO # ユーザ情報テーブル名
        self.__book_info_tbl_name = ""        # 検索対象情報テーブル名
        self.__user_info_tbl_cursor = None  # ユーザ情報テーブルカーソル情報
        self.__book_info_tbl_cursor = None  # 検索対象情報テーブルカーソル情報


    def create_db(self, user_name:str) -> bool:
        """ DB生成
        """
        try:
            # 接続
            self.__connect_db()
            # テーブル生成
            # 未生成時のみ生成を行う
            #self.__user_info_tbl_cursor.execute("drop table if exists %s" % USER_INFO)
            # ユーザ情報テーブル
            self.__user_info_tbl_cursor.execute("create table if not exists %s (user_name text primary key, table_name text)" % USER_INFO)
            # 
            self.__book_info_tbl_name  = user_name+BOOK_INFO
            #self.__book_info_tbl_cursor.execute("drop table if exists %s" % (table_name))
            self.__book_info_tbl_cursor.execute("create table if not exists %s (author_name text primary key, date text)" % (self.__book_info_tbl_name))

            #insert
            query_str = "insert into " + USER_INFO + " values (?, ?)"
            # 現データ数取得
            #self.__user_info_tbl_cursor.execute("select count(*) from %s " % self.__user_info_tbl_name)
            #data_max = self.__user_info_tbl_cursor.fetchall()
            self.__user_info_tbl_cursor.execute(query_str, (user_name, self.__book_info_tbl_name))

        except sqlite3.Error as e:
            # 検索対象情報テーブル名保持
            self.__book_info_tbl_name = user_name+BOOK_INFO
            print(e.args[0])
            return False
            
        # output
        for row in self.__user_info_tbl_cursor.execute("select * from %s" % USER_INFO):
            print(row)
            for row_sub in self.__book_info_tbl_cursor.execute("select * from %s" % row[1]):
                print(row_sub)
                
        # 接続解除
        self.__disconnect_db()
        return True


    def get_db_author_list(self) -> list:
        """ 著者名リスト取得
        """
        author_list = []
        return author_list


    def add_book_info(self, author:str, date:str):
        """ 検索対象情報追加  
        [I] author : 著者名 [I] date 出力対象日閾値
        """
        # 接続
        self.__connect_db()
        # 追加
        try:
            query_str = "insert into " + self.__book_info_tbl_name + " values (?, ?)"
            self.__book_info_tbl_cursor.execute(query_str,(author, date))
        except sqlite3.Error as e:
            print(e.args[0])
        # output
        for row in self.__book_info_tbl_cursor.execute("select * from %s" % self.__book_info_tbl_name):
            print(row)
        # 接続解除
        self.__disconnect_db()


    def __connect_db(self):
        """ DB接続，カーソル取得
        """
        self.__db_conection = sqlite3.connect(DB_FILE_NAME)
        self.__user_info_tbl_cursor = self.__db_conection.cursor()  # ユーザ情報テーブルカーソル情報
        self.__book_info_tbl_cursor = self.__db_conection.cursor()  # 検索対象情報テーブルカーソル情報

    
    def __disconnect_db(self):
        """ DB接続解除
        """
        # 保存
        self.__db_conection.commit()
        # 接続終了
        self.__db_conection.close()
    

if __name__ == "__main__":
    dbtest = DBInfoCntrl()
    dbtest.create_db("nyasai")
    dbtest.add_book_info("テスト","2018/06/14")

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


    def create_db(self, user_name:str):
        """ DB生成
        """
        try:
            self.__connect_db()
            # テーブル生成
            # 未生成時のみ生成を行う
            #self.__user_info_tbl_cursor.execute("drop table if exists %s" % USER_INFO)
            # ユーザ情報テーブル
            self.__user_info_tbl_cursor.execute("create table if not exists %s (id int primary key, user_name text, table_name text)" % USER_INFO)
            # 
            self.__book_info_tbl_name = user_name+BOOK_INFO
            #self.__book_info_tbl_cursor.execute("drop table if exists %s" % (table_name))
            self.__book_info_tbl_cursor.execute("create table if not exists %s (id int primary key, table_name text)" % (self.__book_info_tbl_name))

            #insert
            query_str = "insert into " + USER_INFO + " values (?, ?, ?)"
            self.__user_info_tbl_cursor.execute(query_str, (1,user_name, self.__book_info_tbl_name))
            
        except sqlite3.Error as e:
            print(e.args[0])
            
        # output
        for row in self.__user_info_tbl_cursor.execute("select * from %s" % USER_INFO):
            print(row)
            for row_sub in self.__book_info_tbl_cursor.execute("select * from %s" % row[2]):
                print(row_sub)
                
        # 接続解除
        self.__disconnect_db()


    def get_db_author_list(self) -> list:
        author_list = []
        return author_list


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
    

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import subprocess
import amazon_book_search


def main():
    html_str = """
    <html>
    <head>
    <meta http-equiv="Cntent-Type" content="text/html"; charset="UTF-8">
    <title>CGI</title>
    </head>
    <body>
    """
    print(html_str)

    form = cgi.FieldStorage()
    is_name_enable = False
    if "user_name" in form:
        is_name_enable = True

    if is_name_enable is True:
        # 著者が設定されていれば，DBへ登録を行う
        #if len(form["textarea_info"].value) != 0:
        #    pass
        
        # 著者が空または追加登録後，対象ユーザ名のデータを読み込む
        amazon_book_search.main(form["user_name"].value)
        # command = './cgi-bin/amazon_book_search.py ' + form["user_name"].value
        # subprocess.Popen(command)

    print("</body></html>")

def set_info_for_DB():
    pass

if __name__ == "__main__":
    main()
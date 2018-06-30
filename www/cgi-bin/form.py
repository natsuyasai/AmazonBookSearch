#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import amazon_book_search

#print("Content-Type: text/html\n")
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
is_name_enbale = False
if "user_name" in form:
    is_name_enable = True

if is_name_enable is True:
    amazon_book_search.main(form["user_name"].value)

print("</body></html>")

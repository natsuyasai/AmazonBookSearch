#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CSV関連
"""

# import ***************************************************************************
import csv          # CSV読み書き
import urllib       # urlエンコード変換
import re           # 文字列解析
from enum import Enum # 列挙型用
#*******************
from debug_info import Debug
#***********************************************************************************

# Const Define *********************************************************************
class CsvEncodeType(Enum):
    UTF_8 = 0
    UTF_8_BOM = 1
    SHIFT_JIS = 2
#***********************************************************************************

class CsvUtil:
    @staticmethod
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
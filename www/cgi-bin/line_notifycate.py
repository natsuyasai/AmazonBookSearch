#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LINE通知
"""

# import ***************************************************************************
# 追加要 ***********
import requests
#*******************

# LINE通知用
LINE_NOTIFY_TOKEN = ''
LINE_NOTIFY_API = 'https://notify-api.line.me/api/notify'

class LineNotifycate:

    def line_notifycate(self, ntf_str):
        """ LINE通知処理  
        LINEへ通知メッセージを送信する  
        [I] ntf_str : 通知内容
        """
        payload = {'message': ntf_str}
        headers = {'Authorization': 'Bearer ' + LINE_NOTIFY_TOKEN}  # 発行したトークン
        line_ntf_result = requests.post(LINE_NOTIFY_API, data=payload, headers=headers)
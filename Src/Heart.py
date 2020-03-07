# BiliBiliHelper Python Version
# Copy right (c) 2019-2020 TheWanderingCoel
# 该代码实现了发送直播间心跳包的功能
# 代码根据metowolf大佬的PHP版本进行改写
# PHP代码地址:https://github.com/metowolf/BilibiliHelper/blob/0.9x/src/plugins/Heart.php

import asyncio
import platform

if platform.system() == "Windows":
    from Windows_Log import Log
else:
    from Unix_Log import Log
from AsyncioCurl import AsyncioCurl
from Config import *


class Heart:

    def __init__(self):
        self.roomId = config["Live"]["ROOM_ID"]

    async def work(self):

        while 1:
            await self.web(self.roomId)
            await self.mobile(self.roomId)

            await asyncio.sleep(300)

    async def web(self, roomId):
        url = "https://api.live.bilibili.com/User/userOnlineHeart"
        payload = {
            "room_id": self.roomId,
            "csrf_token": account["Token"]["CSRF"],
            "csrf": account["Token"]["CSRF"]
        }
        data = await AsyncioCurl().request_json("POST", url, headers=config["pcheaders"], data=payload)

        if data["code"] != 0:
            Log.warning("直播间 %s 心跳异常 (WEB)" % roomId)
        else:
            Log.info("向直播间 %s 发送心跳包 (WEB)" % roomId)

    async def mobile(self, roomId):
        url = "https://api.live.bilibili.com/mobile/userOnlineHeart"
        payload = {
            "room_id": self.roomId,
            "csrf_token": account["Token"]["CSRF"],
            "csrf": account["Token"]["CSRF"]
        }
        data = await AsyncioCurl().request_json("POST", url, headers=config["pcheaders"], data=payload)

        if data["code"] != 0:
            Log.warning("直播间 %s 心跳异常 (APP)" % roomId)
        else:
            Log.info("向直播间 %s 发送心跳包 (APP)" % roomId)

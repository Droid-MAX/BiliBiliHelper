# BiliBiliHelper Python Version
# Copy right (c) 2019-2020 TheWanderingCoel
# 该代码实现了银瓜子对换硬币的功能

import asyncio
import platform

if platform.system() == "Windows":
    from Windows_Log import Log
else:
    from Unix_Log import Log
from AsyncioCurl import AsyncioCurl
from Base import std235959ptm
from Config import *


class Silver2Coin:

    async def work(self):
        if config["Function"]["SILVER2COIN"] == "False":
            return

        while 1:
            await self.exchange()

            await asyncio.sleep(std235959ptm())

    async def exchange(self):
        url = "https://api.live.bilibili.com/pay/v1/Exchange/silver2coin"
        data = await AsyncioCurl().request_json("GET", url, headers=config["pcheaders"])

        if data["code"] == 403:
            if "每天" in data["message"]:
                Log.warning(data["message"] + "硬币")
            else:
                Log.warning(data["message"])
            return

        Log.info(data["message"] + ",兑换了一枚硬币")

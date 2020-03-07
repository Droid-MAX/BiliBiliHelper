# BiliBiliHelper Python Version
# Copy right (c) 2019-2020 TheWanderingCoel
# 该代码实现了每日礼包功能
# 代码根据metowolf大佬的PHP版本进行改写

import asyncio
import platform

if platform.system() == "Windows":
    from Windows_Log import Log
else:
    from Unix_Log import Log
from Config import *
from AsyncioCurl import AsyncioCurl
from Base import std235959ptm


class DailyBag():
    def __init__(self):
        self.done = []

    async def work(self):
        if config["Function"]["DAILYBAG"] == "False":
            return

        while 1:
            await self.web()

            await self.mobile()

            if len(self.done >= 2):
                self.done = []
                await asyncio.sleep(std235959ptm())
            else:
                await asyncio.sleep(600)

    async def web(self):
        if "web" in self.done:
            return

        url = "https://api.live.bilibili.com/gift/v2/live/receive_daily_bag"
        data = await AsyncioCurl().request_json("GET", url, headers=config["pcheaders"])

        if data["code"] != 0:
            Log.warning("每日礼包领取失败(WEB)")
            return
        else:
            Log.info("每日礼包领取成功(WEB)")
            self.done.append("web")
            return

    async def mobile(self):

        if "app" in self.done:
            return

        url = "https://api.live.bilibili.com/AppBag/sendDaily"
        data = await AsyncioCurl().request_json("GET", url, headers=config["pcheaders"])

        if data["code"] != 0:
            Log.warning("每日礼包领取失败(APP)")
            return
        else:
            Log.info("每日礼包领取成功(APP)")
            self.done.append("app")
            return

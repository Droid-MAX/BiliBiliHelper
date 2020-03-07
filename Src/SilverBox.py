# BiliBiliHelper Python Version
# Copy right (c) 2019-2020 TheWanderingCoel
# 该代码实现了自动领取银瓜子宝箱的功能

import random
import asyncio
import platform

if platform.system() == "Windows":
    from Windows_Log import Log
else:
    from Unix_Log import Log
from AsyncioCurl import AsyncioCurl
from Config import *
from Base import *


class SilverBox:

    def __init__(self):
        self.task = 0
        self.time_start = 0
        self.time_end = 0

    async def work(self):
        if config["Function"]["SILVERBOX"] == "False":
            return

        while 1:
            if self.task == 0:
                await self.getTask()
            else:
                await self.openTask()

    async def openTask(self):
        url = "https://api.live.bilibili.com/mobile/freeSilverAward"
        payload = {
            "time_start": self.time_start,
            "time_end": self.time_end
        }
        sign = Sign(payload)
        data = await AsyncioCurl().request_json("GET", url, params=sign, headers=config["pcheaders"])

        if data["code"] != 0:
            Log.warning("开启宝箱失败")
            await asyncio.sleep(random.randint(60, 120))
            return

        Log.info("开始宝箱成功,获得 %s 个银瓜子,当前有 %s 个银瓜子" % (data["data"]["awardSilver"], int(data["data"]["silver"])))
        self.task = 0
        await asyncio.sleep(random.randint(5, 20))

    async def getTask(self):
        url = "https://api.live.bilibili.com/lottery/v1/SilverBox/getCurrentTask"
        data = await AsyncioCurl().request_json("GET", url, headers=config["pcheaders"])

        if data["code"] == -10017:
            Log.warning(data["message"])
            await asyncio.sleep(std235959ptm())
            return

        if data["code"] != 0:
            Log.error("领取宝箱任务失败")
            return

        Log.info("领取宝箱成功,内含 %s 个瓜子" % data["data"]["silver"])
        Log.info("等待 %s 分钟后打开宝箱" % data["data"]["minute"])

        self.task = 1
        self.time_start = data["data"]["time_start"]
        self.time_end = data["data"]["time_end"]
        await asyncio.sleep(data["data"]["minute"] * 60 + random.randint(5, 30))

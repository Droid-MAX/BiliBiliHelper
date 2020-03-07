# BiliBiliHelper Python Version
# Copy right (c) 2019-2020 TheWanderingCoel
# PK抽奖处理模块

import asyncio
import time
import platform

if platform.system() == "Windows":
    from Windows_Log import Log
else:
    from Unix_Log import Log
from Utils import Utils
from Timer import Timer
from Statistics import Statistics
from BasicRequest import BasicRequest
from Raffle_Handler import RaffleHandler

class PkRaffleHandler:

    @staticmethod
    async def check(real_roomid):
        if not await Utils.is_normal_room(real_roomid):
            return
        data = await BasicRequest.pk_req_check(real_roomid)

        list_available_raffleid = []

        checklen = data["data"]
        try:
            for j in checklen:
                raffle_id = j["id"]
                Log.raffle("本次获取到的 大乱斗 抽奖id为 %s" % raffle_id)
                list_available_raffleid.append(raffle_id)
        except:
            Log.error("检测到无效的大乱斗抽奖")

        tasklist = []
        for raffle_id in list_available_raffleid:
            task = asyncio.ensure_future(PkRaffleHandler.join(real_roomid, raffle_id))
            tasklist.append(task)
        if tasklist:
            raffle_results = await asyncio.gather(*tasklist)
            if False in raffle_results:
                Log.error("繁忙提示,稍后重新尝试")
                RaffleHandler.push2queue((real_roomid,), PkRaffleHandler.check)


    @staticmethod
    async def join(real_roomid, raffle_id):
        await BasicRequest.enter_room(real_roomid)
        data = await BasicRequest.pk_req_join(real_roomid, raffle_id)
        Log.raffle("参与了房间 %s 的 大乱斗 抽奖" % real_roomid)
        Statistics.add2joined_raffles("PK类(合计)")

        code = data["code"]
        if not code:
            Log.raffle("房间 %s 大乱斗 抽奖结果: %s" % (
            real_roomid, data["data"]["award_text"]))
            Statistics.add2results(data["data"]["award_text"][0:2], int(data["data"]["award_num"]))
        elif code == -500:
            Log.error("-500繁忙,稍后重试")
            return False
        elif code == 400:
            Log.error("当前账号正在小黑屋中")
            return False

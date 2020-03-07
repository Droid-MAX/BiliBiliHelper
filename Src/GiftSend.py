# BiliBiliHelper Python Version
# Copy right (c) 2019-2020 TheWanderingCoel
# 该代码实现了自动送出即将过期礼物的功能
# 代码根据metowolf大佬的PHP版本进行改写
# PHP代码地址:https://github.com/metowolf/BilibiliHelper/blob/0.9x/src/plugins/GiftSend.php

import asyncio
import platform

if platform.system() == "Windows":
    from Windows_Log import Log
else:
    from Unix_Log import Log
from AsyncioCurl import AsyncioCurl
from Base import std235959ptm
from Config import *
from Utils import Utils

class GiftSend:

    def __init__(self):
        self.index = 0
        self.uid = 0
        self.ruid = 0
        self.roomid = 0

    async def work(self):
        if config["Function"]["GIFTSEND"] == "False":
            return
        if config["GiftSend"]["ROOM_ID"] == "":
            Log.warning("自动送礼模块房间号未配置,已停止...")
            return

        while 1:
            if self.ruid == 0:
                status = await self.getRoomInfo()
                if status == 1:
                    return
                elif status == 25014:
                    self.index = 0
                    await asyncio.sleep(std235959ptm())

            url = "https://api.live.bilibili.com/gift/v2/gift/bag_list"
            data = await AsyncioCurl().request_json("GET", url, headers=config["pcheaders"])

            if data["code"] != 0:
                Log.warning("背包查看失败!" + data["message"])

            if len(data["data"]["list"]) != 0:
                for each in data["data"]["list"]:
                    if each["expire_at"] >= data["data"]["time"] and each["expire_at"] <= data["data"]["time"] + int(
                            config["GiftSend"]["TIME"]):
                        await self.send(each)
                        await asyncio.sleep(3)

            await asyncio.sleep(600)

    # 返回值
    # 0 没有异常正常结束
    # 1 出现异常退出
    # 25014 今日任务已完成
    async def getRoomInfo(self):
        Log.info("正在生成直播间信息...")

        url = "https://api.bilibili.com/x/member/web/account"
        data = await AsyncioCurl().request_json("GET", url, headers=config["pcheaders"])

        if "code" in data and data["code"] != 0:
            Log.warning("获取账号信息失败!" + data["message"])
            Log.warning("清空礼物功能禁用!")
            return 1

        status = await Utils.is_intimacy_full_today(config["GiftSend"]["ROOM_ID"].split(",")[self.index])
        if status:
            Log.warning("当前房间勋章亲密度已满,尝试切换房间...")
            if len(config["GiftSend"]["ROOM_ID"].split(",")) <= self.index + 1:
                Log.warning("无其他可用房间，休眠到明天...")
                return 25014
            else:
                self.index += 1
                Log.warning("礼物赠送房间更改为 %s" % config["GiftSend"]["ROOM_ID"].split(",")[self.index])

        self.uid = data["data"]["mid"]

        url = "https://api.live.bilibili.com/room/v1/Room/get_info"
        payload = {
            "id": config["GiftSend"]["ROOM_ID"].split(",")[self.index]
        }

        data = await AsyncioCurl().request_json("GET", url, headers=config["pcheaders"], params=payload)

        if data["code"] != 0:
            Log.warning("获取主播房间号失败!" + data["message"])
            Log.warning("清空礼物功能禁用!")
            return 1

        Log.info("直播间信息生成完毕!")

        self.ruid = data["data"]["uid"]
        self.roomid = data["data"]["room_id"]

        return 0

    async def send(self, value):
        url = "https://api.live.bilibili.com/gift/v2/live/bag_send"
        csrf = account["Token"]["CSRF"]

        payload = {
            "coin_type": "silver",
            "gift_id": value["gift_id"],
            "ruid": self.ruid,
            "uid": self.uid,
            "biz_id": self.roomid,
            "gift_num": value["gift_num"],
            "data_source_id": "",
            "data_behavior_id": "",
            "bag_id": value["bag_id"],
            "csrf_token": csrf,
            "csrf": csrf
        }
        data = await AsyncioCurl().request_json("POST", url, headers=config["pcheaders"], data=payload)

        if data["code"] != 0:
            Log.warning("送礼失败!" + data["message"])
        else:
            Log.info("成功向 %s 投喂了 %s 个 %s" % (payload["biz_id"], value["gift_num"], value["gift_name"]))

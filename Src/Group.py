# BiliBiliHelper Python Version
# Copy right (c) 2019-2020 TheWanderingCoel
# 该代码实现了应援团签到功能
# 代码根据metowolf大佬的PHP版本进行改写
# PHP代码地址:https://github.com/metowolf/BilibiliHelper/blob/0.9x/src/plugins/Group.php

import asyncio
import platform

if platform.system() == "Windows":
    from Windows_Log import Log
else:
    from Unix_Log import Log
from AsyncioCurl import AsyncioCurl
from Base import std235959ptm
from Config import *


class Group:

    async def work(self):
        if config["Function"]["GROUP"] == "False":
            return

        while 1:
            groups = await self.getList()
            count = len(groups)
            for each in groups:
                count -= await self.signIn(each)

            if count == 0:
                await asyncio.sleep(std235959ptm())
            else:
                await asyncio.sleep(3600)

    async def getList(self):
        url = "https://api.vc.bilibili.com/link_group/v1/member/my_groups"
        data = await AsyncioCurl().request_json("GET", url, headers=config["pcheaders"])

        if data["code"] != 0:
            Log.warning("查询应援团名单异常")
            return []

        if len(data["data"]["list"]) == 0:
            Log.info("没有需要签到的应援团")
            return []

        return data["data"]["list"]

    async def signIn(self, value):
        url = "https://api.vc.bilibili.com/link_setting/v1/link_setting/sign_in"
        payload = {
            "group_id": value["group_id"],
            "owner_id": value["owner_uid"]
        }
        data = await AsyncioCurl().request_json("POST", url, headers=config["pcheaders"], data=payload)

        if data["code"] != 0:
            Log.warning("应援团 %s 签到异常" % value["group_name"])
            Log.erorr(data)
            return False

        if data["data"]["status"] != 0:
            Log.warning("应援团 %s 已经签到过了" % value["group_name"])
        else:
            Log.info("应援团 %s 签到成功,增加 %s 点亲密度" % (value["group_name"], data["data"]["add_num"]))

        return True

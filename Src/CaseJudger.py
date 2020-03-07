import asyncio
from AsyncioCurl import AsyncioCurl
from Config import *
import platform

if platform.system() == "Windows":
    from Windows_Log import Log
else:
    from Unix_Log import Log
from Base import std235959ptm


class CaseJudger:

    def __init__(self):
        self.caseId = 0  # 案件id
        self.vote = 0  # 1.封禁, 2.否决, 4.删除
        self.voteRule = 0  # 否决
        self.voteBreak = 0  # 封禁
        self.voteDelete = 0  # 删除
        self.level = {
            1: "建议封禁",
            2: "否决",
            4: "建议删除"
        }

    async def work(self):
        if config["Function"]["CASEJUDGER"] == "False":
            return

        while 1:
            status = await self.get_case()
            if status == 25014:
                await asyncio.sleep(std235959ptm())
            elif status == 0:
                await self.jury_case()
                self.determine_action()
                await self.vote_case()

                await asyncio.sleep(3)
            else:
                await asyncio.sleep(600)

    def determine_action(self):
        vote_status = [self.voteRule, self.voteBreak, self.voteDelete]
        vote_max_index = vote_status.index(max(vote_status))
        if vote_max_index == 0:
            self.vote = 2
        elif vote_max_index == 1:
            self.vote = 1
        elif vote_max_index == 2:
            self.vote = 4

    # 返回值
    # 0 没有异常正常结束
    # 1 出现异常退出
    # 25014 今日任务已完成
    async def get_case(self):
        url = "https://api.bilibili.com/x/credit/jury/caseObtain"
        payload = {
            "jsonp": "jsonp",
            "csrf": account["Token"]["CSRF"]
        }
        data = await AsyncioCurl().request_json("POST", url, data=payload, headers=config["pcheaders"])
        if data["code"] == 25014:
            Log.warning("今日审核已满,明天再来看看吧~")
            return 25014
        elif data["code"] == 0:
            try:
                self.caseId = data["data"]["id"]
            except:
                Log.error("案件ID获取失败")
                return 1
            Log.info("本次获取到的案件ID为 %s" % self.caseId)
            return 0
        else:
            Log.error("获取案件失败，等待600秒后重试")
            return 1

    async def jury_case(self):
        url = "https://api.bilibili.com/x/credit/jury/juryCase"
        payload = {
            "jsonp": "jsonp",
            "cid": self.caseId
        }
        data = await AsyncioCurl().request_json("GET", url, params=payload, headers=config["pcheaders"])
        try:
            self.voteRule = data["data"]["voteRule"]
            self.voteBreak = data["data"]["voteBreak"]
            self.voteDelete = data["data"]["voteDelete"]
            Log.info("获取到案件ID为 %s 的投票率: %s 票否决, %s 票建议封禁, %s 票建议删除" % (
                self.caseId, self.voteRule, self.voteBreak, self.voteDelete))
        except:
            Log.error("获取案件投票信息失败")

    async def vote_case(self):
        url = "https://api.bilibili.com/x/credit/jury/vote"
        payload = {
            "jsonp": "jsonp",
            "cid": self.caseId,
            "vote": self.vote,
            "content": "",
            "likes": "",
            "hates": "",
            "attr": 0,
            "csrf": account["Token"]["CSRF"]
        }
        data = await AsyncioCurl().request_json("POST", url, data=payload, headers=config["pcheaders"])
        if data["code"] == 0:
            Log.info("对 %s 案件采取 %s 操作成功" % (self.caseId, self.level.get(self.vote)))
        else:
            Log.warning("对 %s 案件采取 %s 操作失败" % (self.caseId, self.level.get(self.vote)))

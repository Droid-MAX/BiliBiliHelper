import json
import asyncio
import random
from Base import adjust_for_chinese
from BasicRequest import BasicRequest
import platform

if platform.system() == "Windows":
    from Windows_Log import Log
else:
    from Unix_Log import Log
from Config import *
from operator import itemgetter
from AsyncioCurl import AsyncioCurl


class Utils:

    @staticmethod
    def cprint(message):
        for each in message:
            print(each)

    async def is_normal_room(roomid):
        if not roomid:
            return True
        data = await BasicRequest.init_room(roomid)
        if not data["code"]:
            data = data["data"]
            param1 = data["is_hidden"]
            param2 = data["is_locked"]
            param3 = data["encrypted"]
            # 如果三个中有一个是True
            if any((param1, param2, param3)):
                Log.warning("抽奖脚本检测到房间 %s 为异常房间" % roomid)
                return False
            # 否则
            else:
                Log.raffle("抽奖脚本检测到房间 %s 为正常房间" % roomid)
                return True

    @staticmethod
    async def get_room_by_area(area_id, room_id=None):

        if room_id is not None and room_id:
            if await Utils.is_ok_as_monitor(room_id, area_id):
                Log.info("%s 号弹幕监控选择房间 %s" % (area_id, room_id))
                return room_id

        if area_id == 1:
            room_id = 23058
            if await Utils.is_ok_as_monitor(room_id, area_id):
                Log.info("%s 号弹幕监控选择房间 %s" % (area_id, room_id))
                return room_id

        while True:
            data = await BasicRequest.get_room_by_area(area_id)
            data = data["data"]
            room_id = random.choice(data)["roomid"]
            if await Utils.is_ok_as_monitor(room_id, area_id):
                Log.info("%s 号弹幕监控选择房间 %s" % (area_id, room_id))
                return room_id

    @staticmethod
    async def is_ok_as_monitor(room_id, area_id):
        data = await BasicRequest.init_room(room_id)
        data = data["data"]
        is_hidden = data["is_hidden"]
        is_locked = data["is_locked"]
        is_encryped = data["encrypted"]
        is_normal = not any((is_hidden, is_locked, is_encryped))

        data = await BasicRequest.get_room_info(room_id)
        data = data["data"]
        is_open = True if data["live_status"] == 1 else False
        current_area_id = data["parent_area_id"]

        is_ok = (area_id == current_area_id) and is_normal and is_open
        return is_ok

    @staticmethod
    async def fetch_user_info():
        data = await BasicRequest.req_fetch_user_info()
        print("查询用户信息...")
        if not data["code"]:
            data = data["data"]
            userInfo = data["userInfo"]
            userCoinIfo = data["userCoinIfo"]
            uname = userInfo["uname"]
            achieve = data["achieves"]
            user_level = userCoinIfo["user_level"]
            silver = userCoinIfo["silver"]
            gold = userCoinIfo["gold"]
            identification = bool(userInfo["identification"])
            mobile_verify = bool(userInfo["mobile_verify"])
            user_next_level = userCoinIfo["user_next_level"]
            user_intimacy = userCoinIfo["user_intimacy"]
            user_next_intimacy = userCoinIfo["user_next_intimacy"]
            user_level_rank = userCoinIfo["user_level_rank"]
            biliCoin = userCoinIfo["coins"]
            bili_coins = userCoinIfo["bili_coins"]
            print("用户名:" + uname)
            print(f"手机认证状态 {mobile_verify} | 实名认证状态 {identification}")
            print("银瓜子:" + str(silver))
            print("金瓜子:" + str(gold))
            print("硬币数:" + str(biliCoin))
            print("B币数:" + str(bili_coins))
            print("成就值:" + str(achieve))
            print("等级值:" + str(user_level) + "———>" + str(user_next_level))
            print("经验值:" + str(user_intimacy))
            print("剩余值:" + str(user_next_intimacy - user_next_intimacy))
            arrow = int(user_intimacy * 30 / user_next_intimacy)
            line = 30 - arrow
            percent = user_intimacy / user_next_intimacy * 100.0
            process_bar = "[" + ">" * arrow + "-" * line + "]" + "%.2f" % percent + "%"
            print(process_bar)
            print("等级榜:" + str(user_level_rank))

    @staticmethod
    async def fetch_bag_list(verbose=False, bagid=None, show=True, raw=False):
        data = await BasicRequest.req_fetch_bag_list()
        if raw:
            return data
        gift_list = []
        if show:
            print("查询可用礼物...")
        for i in data["data"]["list"]:
            bag_id = i["bag_id"]
            gift_id = i["gift_id"]
            gift_num = i["gift_num"]
            gift_name = i["gift_name"]
            expireat = i["expire_at"]
            left_time = (expireat - data["data"]["time"])
            if not expireat:
                left_days = "+∞".center(6)
                left_time = None
            else:
                left_days = round(left_time / 86400, 1)
            if bagid is not None:
                if bag_id == int(bagid):
                    return gift_id, gift_num
            else:
                if verbose:
                    print(f"编号为 {bag_id} 的 {gift_name:^3} X {gift_num:^4} (在 {left_days:^6} 天后过期)")
                elif show:
                    print(f" {gift_name:^3} X {gift_num:^4} (在 {left_days:^6} 天后过期)")

            gift_list.append([gift_id, gift_num, bag_id, left_time])
        return gift_list

    @staticmethod
    async def check_taskinfo():
        data = await BasicRequest.req_check_taskinfo()
        if not data["code"]:
            data = data["data"]
            double_watch_info = data["double_watch_info"]
            sign_info = data["sign_info"]

        if double_watch_info["status"] == 1:
            print("双端观看直播已完成，但未领取奖励")
        elif double_watch_info["status"] == 2:
            print("双端观看直播已完成，已经领取奖励")
        else:
            print("双端观看直播未完成")
            if double_watch_info["web_watch"] == 1:
                print("网页端观看任务已完成")
            else:
                print("网页端观看任务未完成")

            if double_watch_info["mobile_watch"] == 1:
                print("移动端观看任务已完成")
            else:
                print("移动端观看任务未完成")

        if sign_info["status"] == 1:
            print("每日签到已完成")
        else:
            print("每日签到未完成")

    @staticmethod
    async def fetch_medal(show=True, list_wanted_mendal=None):
        printlist = []
        list_medal = []
        if show:
            printlist.append("查询勋章信息...")
            printlist.append(
                "{} {} {:^12} {:^10} {} {:^6} {}".format(adjust_for_chinese("勋章"), adjust_for_chinese("主播昵称"), "亲密度",
                                                         "今日的亲密度", adjust_for_chinese("排名"), "勋章状态", "房间号码"))
        dic_worn = {"1": "正在佩戴", "0": "待机状态"}
        data = await BasicRequest.req_fetch_medal()
        if not data["code"]:
            for i in data["data"]["fansMedalList"]:
                if "roomid" in i:
                    list_medal.append(
                        (i["roomid"], int(i["dayLimit"]) - int(i["todayFeed"]), i["medal_name"], i["level"]))
                    if show:
                        printlist.append("{} {} {:^14} {:^14} {} {:^6} {:^9}".format(
                            adjust_for_chinese(i["medal_name"] + "|" + str(i["level"])),
                            adjust_for_chinese(i["anchorInfo"]["uname"]),
                            str(i["intimacy"]) + "/" + str(i["next_intimacy"]),
                            str(i["todayFeed"]) + "/" + str(i["dayLimit"]), adjust_for_chinese(str(i["rank"])),
                            dic_worn[str(i["status"])], i["roomid"]))
        if show:
            Utils.cprint(printlist)
        if list_wanted_mendal is not None:
            list_return_medal = []
            for roomid in list_wanted_mendal:
                for i in list_medal:
                    if i[0] == roomid:
                        list_return_medal.append(i[:3])
                        break
        else:
            list_return_medal = [i[:3] for i in sorted(list_medal, key=itemgetter(3), reverse=True)]
        return list_return_medal

    @staticmethod
    async def send_danmu(msg, roomId):
        data = await BasicRequest.req_send_danmu(msg, roomId)
        Log.info(data)

    @staticmethod
    async def boom_danmu(msg, roomId):
        data = await BasicRequest.req_send_danmu(msg, roomId)
        Log.info(data)

    @staticmethod
    async def check_room(roomid):
        data = await BasicRequest.init_room(roomid)
        if not data["code"]:
            data = data["data"]
            if not data["short_id"]:
                print("此房间无短号")
            else:
                print("短号为:" + str(data["short_id"]))
            print("真实房间号为:" + str(data["room_id"]))
            return data["room_id"]
        elif data["code"] == 60004:
            print(data["msg"])

    @staticmethod
    async def send_gift(roomid, num_wanted, bagid, giftid=None):
        if giftid is None:
            giftid, num_owned = await Utils.fetch_bag_list(False, bagid)
            num_wanted = min(num_owned, num_wanted)
        if not num_wanted:
            return
        data = await BasicRequest.init_room(roomid)
        ruid = data["data"]["uid"]
        biz_id = data["data"]["room_id"]
        data1 = await BasicRequest.req_send_gift(giftid, num_wanted, bagid, ruid, biz_id)
        if not data1["code"]:
            print(f'送出礼物: {data1["data"]["gift_name"]} X {data1["data"]["gift_num"]}')
        else:
            print("错误: " + data1["message"])

    @staticmethod
    async def fetch_liveuser_info(real_roomid):
        data = await BasicRequest.req_fetch_liveuser_info(real_roomid)
        if not data["code"]:
            data = data["data"]
            print("主播昵称: " + data["info"]["uname"])

            uid = data["level"]["uid"]
            data_fan = await BasicRequest.req_fetch_fan(real_roomid, uid)
            data_fan = data_fan["data"]
            if not data_fan["code"] and data_fan["medal"]["status"] == 2:
                print("勋章名称: " + data_fan["list"][0]["medal_name"])
            else:
                print("此主播暂时没有开通勋章")

    @staticmethod
    async def fetch_capsule_info():
        data = await BasicRequest.req_fetch_capsule_info()
        if not data["code"]:
            data = data["data"]

        if data["normal"]["status"]:
            print("普通扭蛋币: " + str(data["normal"]["coin"]) + " 个")
        else:
            print("普通扭蛋币暂不可用")

        if data["colorful"]["status"]:
            print("彩色扭蛋币: " + str(data["colorful"]["coin"]) + " 个")
        else:
            print("彩色扭蛋币暂不可用")

    @staticmethod
    async def open_capsule(count):
        data = await BasicRequest.req_open_capsule(count)
        if not data["code"]:
            for i in data["data"]["text"]:
                print(i)

    # 检查当前房间勋章亲密度今日是否已满
    @staticmethod
    async def is_intimacy_full_today(roomid):
        data = await BasicRequest.req_fetch_medal()
        for medal in data["data"]["fansMedalList"]:
            if medal["roomid"] == int(roomid):
                return medal["today_intimacy"] == medal["day_limit"]

    # 今日还剩多少亲密度可以赠送
    @staticmethod
    async def value_to_full_intimacy_today(roomid):
        data = await BasicRequest.req_fetch_medal()
        for medal in data["data"]["fansMedalList"]:
            if medal["roomid"] == int(roomid):
                return medal["day_limit"] - medal["today_intimacy"]
        return None

    @staticmethod
    def is_normal_anchor(name):
        blacklist_words = ["拉黑", "黑名单", "脸皮厚", "没有奖品", "无奖", "脸皮厚", "ceshi", "测试", "脚本", "抽奖号", "星段位",
                           "水晶", "万兴神剪手", "自付邮费", "test", "Test", "TEST", "加密", "QQ", "測試", "VX", "vx", "ce",
                           "shi", "这是一个", "lalall", "第一波", "第二波", "第三波", "测试用", "抽奖标题", "策是", "房间抽奖",
                           "CESHI", "ceshi", "奖品A", "奖品B", "奖品C", "硬币", "无奖品", "白名单", "我是抽奖", "0.1", "五毛二",
                           "一分", "一毛", "0.52", "0.66", "0.01", "0.77", "0.16", "照片", "穷", "0.5", "0.88", "双排", "围巾",
                           "棒棒糖", "1毛", "1分", "1角", "P口罩", "素颜", "写真", "图包", "五毛", "螺蛳粉", "键帽", "自拍", "日历",
                           "0.22", "加速器", "越南盾", "冥币", "一角"]
        for word in blacklist_words:
            if word in name:
                return False
        return True

    @staticmethod
    def have_win_award(users):
        for user in users:
            if user["uid"] == int(account["Token"]["UID"]):
                return True
        return False

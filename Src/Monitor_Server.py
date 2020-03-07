# BiliBiliHelper Python Version
# Copy right (c) 2019-2020 TheWanderingCoel
# 舰长服务器连接核心模块
# 支持服务器: https://github.com/Billyzou0741326/bilibili-live-monitor-js

import json
import struct
import asyncio
import time

import aiohttp
import platform

if platform.system() == "Windows":
    from Windows_Log import Log
else:
    from Unix_Log import Log
from Config import *
from Statistics import Statistics
from Raffle_Handler import RaffleHandler
from Tv_Raffle_Handler import TvRaffleHandler
from Pk_Raffle_Handler import PkRaffleHandler
from Guard_Raffle_Handler import GuardRaffleHandler
from Storm_Raffle_Handler import StormRaffleHandler
from Anchor_Raffle_Handler import AnchorRaffleHandler

class MonitorServer:
    def __init__(self, address, password, client_session=None):
        if client_session is None:
            self.client = aiohttp.ClientSession()
        else:
            self.client = client_session
        self.ws = None
        self.address = address
        self.password = password
        self.task_main = None
        self.accepted = False

    @property
    def handshake(self):
        data = {
            "password": self.password
        }
        data = json.dumps(data)
        return self.prepare_message(7, data)

    def decode_message(self, msg):
        messages = []
        body = ""
        while len(msg) > 0:
            total_len, header_len, _, cmd, _ = struct.unpack('!IHHII', msg[:16])
            body = msg[header_len:total_len]
            msg = msg[total_len:]
            messages.append({'cmd': cmd, 'body': body})
        return messages

    def prepare_message(self, cmd, msg=''):
        body = b''
        try:
            msg = msg.encode('utf-8')
            body += msg
        except AttributeError:
            pass

        header = struct.pack('!IHHII', len(body) + 16, 16, 1, cmd, 1)

        payload = b''
        payload += header
        payload += body

        return payload

    def deserialize(self, json_str):
        try:
            json_str = json_str.decode('utf-8')
        except AttributeError:
            pass
        return json.loads(json_str)

    async def open(self):
        try:
            url = f"ws://{self.address}"
            self.ws = await asyncio.wait_for(self.client.ws_connect(url), timeout=3)
            self.accepted = True
        except:
            Log.error("无法连接到舰长监控服务器,请检查网络连接以及端口是否开放")
            return False
        Log.info("监控服务器已连接到: %s" % url)
        return True

    async def read_bytes(self):
        bytes_data = None

        msg = await self.ws.receive()

        # 来自 https://github.com/TheWanderingCoel/BiliBiliHelper/issues/5
        if msg.type == aiohttp.WSMsgType.binary:
            bytes_data = msg.data
        elif msg.type == aiohttp.WSMsgType.text:
            pass
        elif msg.type == aiohttp.WSMsgType.closed:
            Log.warning("与舰长监控服务器的连接已经断开")
            self.accepted = False
        elif msg.type == aiohttp.WSMsgType.error:
            Log.error("舰长监控服务器未知错误")
            self.accepted = False

        return bytes_data

    async def read_datas(self):
        while True:
            data = await self.read_bytes()
            if data is None:
                return
            body = self.deserialize(data)
            self.handle_message(body)

    async def close(self):
        try:
            await self.ws.close()
        except:
            Log.error("无法关闭与舰长监控服务器的连接")
        if not self.ws.closed:
            Log.error("舰长监控服务器状态 %s" % self.ws.closed)

    def handle_message(self, data):
        cmd = data["category"]
        raffle_name = data["name"]
        raffle_id = data["id"]
        room_id = data["roomid"]
        expireAt = data["expireAt"]

        # 大航海
        if cmd == "guard":
            if config["Raffle_Handler"]["GUARD"] != "False":
                Log.raffle("监控服务器检测到 %s 的 %s" % (room_id, raffle_name))
                RaffleHandler.push2queue((room_id,), GuardRaffleHandler.check)
                # 如果不是总督就设置为2(本房间)
                broadcast_type = 0 if raffle_name == "总督" else 2
                Statistics.add2pushed_raffles(raffle_name, broadcast_type)
        # PK(WIP)
        elif cmd == "pk":
            if config["Raffle_Handler"]["PK"] != "False":
                Log.raffle("监控服务器检测到 %s 的 %s" % (room_id, raffle_name))
                RaffleHandler.push2queue((room_id,), PkRaffleHandler.check)
                Statistics.add2pushed_raffles(raffle_name, 1)
        # 节奏风暴
        elif cmd == "storm":
            if config["Raffle_Handler"]["STORM"] != "False":
                Log.raffle("监控服务器检测到 %s 的 %s" % (room_id, raffle_name))
                RaffleHandler.push2queue((room_id,), StormRaffleHandler.check)
                Statistics.add2pushed_raffles(raffle_name, 1)
        # 天选
        elif cmd == "anchor":
            if config["Raffle_Handler"]["ANCHOR"] != "False":
                Log.raffle("监控服务器检测到 %s 的 天选时刻, 奖品为: %s" % (room_id, raffle_name))
                RaffleHandler.push2queue((room_id, raffle_name, raffle_id, expireAt), AnchorRaffleHandler.join)
                Statistics.add2pushed_raffles("天选时刻", 1)

        # 小电视类抽奖
        # else:
        #    if config["Raffle_Handler"]["TV"] != "False":
        #        Log.raffle("监控服务器检测到 %s 的 %s" % (room_id, raffle_name))
        #        Raffle_Handler.RaffleHandler.push2queue((room_id,), TvRaffleHandler.check)
        #        Statistics.add2pushed_raffles(raffle_name)


    async def run_forever(self):
        time_now = 0
        while True:
            if int(time.time()) - time_now <= 10:
                await asyncio.sleep(10)
            Log.info("正在连接监控服务器...")
            time_now = int(time.time())
            is_open = await self.open()
            if not is_open and not self.accepted:
                break
            self.task_main = asyncio.ensure_future(self.read_datas())
            tasks = [self.task_main]
            _, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            await self.close()
            Log.info("舰长监控退出，剩余任务处理完毕")

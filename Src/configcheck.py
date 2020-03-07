# BiliBiliHelper Python Version
# Copy right (c) 2019-2020 TheWanderingCoel
# 该代码对配置文件的有效性进行检查

import sys
import platform

if platform.system() == "Windows":
    from Windows_Log import Log
else:
    from Unix_Log import Log
from Config import *


class ConfigCheck:
    def __init__(self):
        # 错误计数
        self.error_count = 0
        self.check_null("Account", ["BILIBILI_USER", "BILIBILI_PASSWORD"])
        self.check_TF("Function", ["CAPSULE", "COIN2SILVER", "GIFTSEND", "GROUP", "SILVER2COIN", "SILVERBOX", "TASK",
                                   "RAFFLE_HANDLER"])
        self.check_int("Coin2Silver", "COIN")
        self.check_TF("Raffle_Handler", ["TV", "GUARD", "STORM"])
        self.check_TF("Other", ["INFO_MESSAGE", "SENTENCE"])
        self.error_exit()

    # 检查值是否为空
    def check_null(self, mainname, subname):
        for each in subname:
            if account[mainname][each] == "":
                Log.error(mainname + " -> " + each + " entered incorrectly!")
                self.error_count += 1

    # 检查值是否为True, False
    def check_TF(self, mainname, subname):
        for each in subname:
            if config[mainname][each] != "True" and config[mainname][each] != "False":
                Log.error(mainname + " -> " + each + " entered incorrectly!")
                self.error_count += 1

    # 检查是否为合法的整数(>0)
    def check_int(self, mainname, subname):
        if int(config[mainname][subname]) < 0:
            Log.error(mainname + " -> " + subname + " entered incorrectly!")
            self.error_count += 1

    # 有错误直接退出
    def error_exit(self):
        if self.error_count > 0:
            Log.raffle(str(self.error_count) + " errors in config reached! Exiting...")
            sys.exit(1)

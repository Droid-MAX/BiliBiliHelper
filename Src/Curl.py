import json
import requests
import platform

if platform.system() == "Windows":
    from Windows_Log import Log
else:
    from Unix_Log import Log
from Base import Sign
from Config import *


class Curl:
    def __init__(self):
        # 给一个初始值方便判断
        self.proxies = None
        if config["Proxy"]["PROXY_TYPE"] != "None":
            self.proxies = {
                "http": config["Proxy"]["PROXY_ADDRESS"],
                "https": config["Proxy"]["PROXY_ADDRESS"]
            }

    def request_json(self,
                     method,
                     url,
                     headers=None,
                     data=None,
                     params=None,
                     sign=True):
        i = 0
        while True:
            i += 1
            if i >= 10:
                Log.warning(url)
            try:
                if method == "GET":
                    if sign == True:
                        params = Sign(params)
                    if self.proxies != None:
                        r = requests.get(url, headers=headers, params=params, proxies=self.proxies)
                    else:
                        r = requests.get(url, headers=headers, params=params)
                    return json.loads(r.text)
                elif method == "POST":
                    if sign == True:
                        data = Sign(data)
                    if self.proxies != None:
                        r = requests.post(url, headers=headers, data=data, proxies=self.proxies)
                    else:
                        r = requests.post(url, headers=headers, data=data)
                    return json.loads(r.text)
            except Exception as e:
                Log.error(e)
                continue

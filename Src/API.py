# BiliBiliHelper Python Version
# Copy right (c) 2019-2020 TheWanderingCoel
# BiliBiliHelper API核心模块

import os
import sys
import tailer
import logging
import platform

if platform.system() == "Windows":
    from Windows_Log import Log
else:
    from Unix_Log import Log
from flask import Flask, jsonify, request, stream_with_context, Response
from Config import *
from Sentence import Sentence
from Version import version
from APIUtils import APIUtils


class API:

    def __init__(self):
        self.APIUtils = APIUtils()

    def get_log(self):
        for line in tailer.follow(open(sys.path[0] + "/Log/BiliBiliHelper.log")):
            data = {
                "message": line
            }
            yield str(data) + "\n"

    def work(self):

        app = Flask(__name__)

        logging.getLogger('werkzeug').disabled = True
        os.environ['WERKZEUG_RUN_MAIN'] = 'true'

        @app.route("/", methods=["GET"])
        def hello():
            data = {
                "hello": "BiliBiliHelper"
            }
            return jsonify(data)

        @app.route("/version", methods=["GET"])
        def version():
            data = {
                "version": version
            }
            return jsonify(data)

        @app.route("/sentence", methods=["GET"])
        def sentence():
            data = {
                "sentence": Sentence().get_sentence()
            }
            return jsonify(data)

        @app.route("/configs", methods=["GET", "PATCH", "PUT"])
        def configs():
            APIUtils.handle_route_configs()

        @app.route("/logs", methods=["GET", "DELETE"])
        def logs():
            APIUtils.handle_route_logs()

        @app.route("/gift", methods=["GET", "POST"])
        def gifts():
            APIUtils.handle_route_gift()

        app.logger.disabled = True
        # 从配置文件导入配置
        app.config.from_pyfile(sys.path[0] + "/Conf/Flask.conf")
        try:
            if config["API"]["ENABLE"] == "True":
                Log.info("正在启动API服务...")
                app.run(threaded=True, port=config["API"]["LISTEN_PORT"])
        except OSError as e:
            Log.error("API服务器启动错误: " + str(e))

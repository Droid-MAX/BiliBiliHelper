from flask import Flask, jsonify, stream_with_context, Response
from Config import *
from Utils import *


class APIUtils:

    def get_configs(self):
        data = {
            "Function": {
                "capsule": config["Function"]["CAPSULE"],
                "coin2silver": config["Function"]["COIN2SILVER"],
                "dailybag": config["Function"]["DAILYBAG"],
                "giftsend": config["Function"]["GIFTSEND"],
                "group": config["Function"]["GROUP"],
                "silver2coin": config["Function"]["SILVER2COIN"],
                "silverbox": config["Function"]["SILVERBOX"],
                "task": config["Function"]["TASK"],
                "raffle_handler": config["Function"]["RAFFLE_HANDLER"]
            },
            "Coin2Silver": {
                "coin": config["Coin2Silver"]["COIN"]
            },
            "Live": {
                "room_id": config["Live"]["ROOM_ID"]
            },
            "Raffle_Handler": {
                "tv": config["Raffle_Handler"]["TV"],
                "pk": config["Raffle_Handler"]["PK"],
                "guard": config["Raffle_Handler"]["GUARD"],
                "storm": config["Raffle_Handler"]["STORM"]
            },
            "Log": {
                "log_level": config["Log"]["LOG_LEVEL"]
            },
            "Other": {
                "info_message": config["Other"]["INFO_MESSAGE"],
                "sentence": config["Other"]["SENTENCE"]
            },
            "Proxy": {
                "proxy_type": config["Proxy"]["PROXY_TYPE"],
                "proxy_address": config["Proxy"]["PROXY_ADDRESS"],
            },
            "API": {
                "listen_port": config["API"]["LISTEN_PORT"],
                "allow_lan": config["API"]["ALLOW_LAN"]
            },
            "Server": {
                "address": config["Server"]["ADDRESS"],
                "password": config["Server"]["PASSWORD"]
            }

        }
        return jsonify(data)

    def reload_configs(self):
        try:
            account.reload()
            config.reload()
            return jsonify({"status": 0, "message": "OK"})
        except Exception as e:
            return jsonify({"status": 500, "message": str(e)})

    def delete_logs(self):
        try:
            Log.clean_log(http_delete=True)
            return jsonify({"status": 0, "message": "OK"})
        except Exception as e:
            return jsonify({"status": 500, "message": str(e)})

    # /configs
    def handle_route_configs(self, request):
        if request.method == "GET":
            return self.get_configs()
        elif request.method == "PATCH":
            return
        elif request.method == "PUT":
            return self.reload_configs()

    # /logs
    def handle_route_logs(self, request):
        if request.method == "GET":
            return Response(stream_with_context(self.get_log()), content_type='application/json')
        elif request.method == "DELETE":
            return self.delete_logs()

    # /gift
    def handle_route_gift(self, request):
        if request.method == "GET":
            return Utils.fetch_bag_list(raw=True)

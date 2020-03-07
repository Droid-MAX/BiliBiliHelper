# BiliBiliHelper Python Version
# Copy right (c) 2019-2020 TheWanderingCoel

import sys
from configobj import ConfigObj

account = ConfigObj(sys.path[0] + "/Conf/Account.conf", encoding="UTF8")
config = ConfigObj(sys.path[0] + "/Conf/BiliBiliHelper.conf", encoding="UTF8")
notification = ConfigObj(sys.path[0] + "/Config/Notification.conf", encoding="UTF8")

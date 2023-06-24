import json, os, requests

SCRIPTDIR = os.getcwd()
vless_reality_conf_path = f"{SCRIPTDIR}/xui-reality-conf.json"


class XUIApi:
    def __init__(
        self,
        address,
        panelPort,
        username,
        password,
        reality_port,
        private_key,
        public_key,
        uuid,
        short_ids,
    ) -> None:
        self.address = address
        self.panelPort = panelPort
        self.username = username
        self.password = password
        self.reality_port = reality_port
        self.private_key = private_key
        self.public_key = public_key
        self.uuid = uuid
        self.short_ids = short_ids
        self.cookie = None
        self.vless_conf = None
        self.inboundId = None

    def sendRequest(self, url, method, params={}, body={}, headers={}, cookies={}):
        req = requests.request(
            method, url, params=params, data=body, headers=headers, cookies=cookies
        )
        return req

    def login(self):
        url = f"http://{self.address}:{self.panelPort}/login"
        res = self.sendRequest(
            url, "POST", body={"username": self.username, "password": self.password}
        )
        response = res.json()

        if response["success"] != True:
            raise ValueError(f'Login failed, {response["msg"]}')

        self.cookie = res.cookies["session"]
        print("Logged into xui")

    def createRealityConf(self):
        vless_reality_conf = None
        with open(vless_reality_conf_path) as json_file:
            vless_reality_conf = json.load(json_file)

        temp_dest = "google.com"
        settings = {
            "publicKey": self.public_key,
            "fingerprint": "chrome",
            "serverName": self.address,
            "spiderX": "/",
        }

        vless_reality_conf["remark"] = vless_reality_conf["remark"] + str(
            self.reality_port
        )
        vless_reality_conf["port"] = self.reality_port
        vless_reality_conf["settings"]["clients"][0]["id"] = self.uuid
        vless_reality_conf["settings"]["clients"][0]["email"] = "user"
        vless_reality_conf["streamSettings"]["realitySettings"]["dest"] = (
            temp_dest + ":443"
        )
        vless_reality_conf["streamSettings"]["realitySettings"]["serverNames"] = [
            temp_dest
        ]
        vless_reality_conf["streamSettings"]["realitySettings"][
            "privateKey"
        ] = self.private_key
        vless_reality_conf["streamSettings"]["realitySettings"][
            "shortIds"
        ] = self.short_ids
        vless_reality_conf["streamSettings"]["realitySettings"]["settings"] = settings

        vless_reality_conf["settings"] = json.dumps(vless_reality_conf["settings"])
        vless_reality_conf["streamSettings"] = json.dumps(
            vless_reality_conf["streamSettings"]
        )
        vless_reality_conf["sniffing"] = json.dumps(vless_reality_conf["sniffing"])

        self.vless_conf = vless_reality_conf
        return vless_reality_conf

    def createRealityInbound(self):
        print("Creating INBOUND for port", self.reality_port)

        vless_conf = self.createRealityConf()
        url = f"http://{self.address}:{self.panelPort}/panel/api/inbounds/add"
        res = self.sendRequest(
            url, "POST", body=vless_conf, cookies={"session": self.cookie}
        )

        response = res.json()

        if response["success"] != True:
            raise ValueError(f'Creating inbound failed, {response["msg"]}')

        self.inboundId = response["obj"]["id"]

    def setRealitySNI(self, sni: str):
        vless_conf = self.vless_conf

        vless_conf["streamSettings"] = json.loads(vless_conf["streamSettings"])
        vless_conf["streamSettings"]["realitySettings"]["dest"] = sni + ":443"
        vless_conf["streamSettings"]["realitySettings"]["serverNames"] = [sni]
        vless_conf["streamSettings"] = json.dumps(vless_conf["streamSettings"])

        url = f"http://{self.address}:{self.panelPort}/panel/api/inbounds/update/{self.inboundId}"
        res = self.sendRequest(
            url, "POST", body=vless_conf, cookies={"session": self.cookie}
        )

        response = res.json()

        if response["success"] != True:
            raise ValueError(f'Creating inbound failed, {response["msg"]}')

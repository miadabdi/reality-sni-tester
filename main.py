import requests, json, os, time
from service import start_proxy_service
from proxy_setting import ProxySetting
from create_config import create_proxy_config
from upload_speed import upload_speed_test
from download_speed import download_speed_test
from socket_tools import get_free_port
from subprocess import Popen
from xui_api import XUIApi
from xray_commands import getUUID, getKeys

uuid = getUUID()
keys = getKeys()
short_ids = ["39fb4b92"]

print("uuid", uuid)
print("public key: ", keys["public_key"])
print("private key: ", keys["private_key"])


SCRIPTDIR = os.getcwd()
xray_path = f"{SCRIPTDIR}/xray"

config_path = f"{SCRIPTDIR}/config.json"
configs = None
with open(config_path) as json_file:
    configs = json.load(json_file)

xui = XUIApi(
    configs["address"],
    configs["panel_port"],
    configs["username"],
    configs["password"],
    configs["reality_port"],
    keys["private_key"],
    keys["public_key"],
    uuid,
    short_ids,
)
xui.login()
xui.createRealityInbound()

for sni in configs["snis"]:
    print("\n\n")
    print(f"================ testing for: {sni} =======================")
    print("Set SNI")
    xui.setRealitySNI(sni)
    time.sleep(0.5)

    port = get_free_port()

    proxy_setting = ProxySetting(
        configs["address"],
        configs["reality_port"],
        uuid,
        keys["public_key"],
        short_ids[0],
    )
    conf_path = create_proxy_config(sni, port, proxy_setting, "configs")

    process, proxies = start_proxy_service(conf_path, xray_path, 5)
    print("Started Xray")
    time.sleep(1)

    def no_and_kill(sni: str, message: str, process: Popen):
        process.kill()
        return f"NO {sni:15s} {message}"

    if configs["type"] == "both" or configs["type"] == "upload":
        try:
            print("Starting Upload Test")
            up_speed, up_latency = upload_speed_test(
                n_bytes=configs["upload_bytes"], proxies=proxies, timeout=30
            )
            print("Upload Ended")
            print("Upload Speed: ", round(up_speed, 3), "mbps")
            print("Upload Latency: ", round(up_latency, 3), "secs")

        except requests.exceptions.ReadTimeout:
            fail_msg = no_and_kill(sni, "Upload read timeout", process)
            print(fail_msg)
        except requests.exceptions.ConnectTimeout:
            fail_msg = no_and_kill(sni, "Upload connect timeout", process)
            print(fail_msg)
        except requests.exceptions.ConnectionError:
            fail_msg = no_and_kill(sni, "Upload connection error", process)
            print(fail_msg)
        except Exception as e:
            fail_msg = no_and_kill(sni, "Upload unknown error", process)
            print(fail_msg)

        print("\n")

    if configs["type"] == "both" or configs["type"] == "download":
        try:
            print("Starting Download Test")
            up_speed, up_latency = download_speed_test(
                n_bytes=configs["download_bytes"], proxies=proxies, timeout=30
            )
            print("Download Ended")
            print("Download Speed: ", round(up_speed, 3), "mbps")
            print("Download Latency: ", round(up_latency, 3), "secs")

        except requests.exceptions.ReadTimeout:
            fail_msg = no_and_kill(sni, "Download read timeout", process)
            print(fail_msg)
        except requests.exceptions.ConnectTimeout:
            fail_msg = no_and_kill(sni, "Download connect timeout", process)
            print(fail_msg)
        except requests.exceptions.ConnectionError:
            fail_msg = no_and_kill(sni, "Download connection error", process)
            print(fail_msg)
        except Exception as e:
            fail_msg = no_and_kill(sni, "Download unknown error", process)
            print(fail_msg)

    process.kill()

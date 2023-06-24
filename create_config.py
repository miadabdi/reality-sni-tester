from proxy_setting import ProxySetting
import json
import random
import string
import os

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

SCRIPTDIR = os.getcwd()
template_path = f'{SCRIPTDIR}/template.json'

def create_proxy_config(
    sni,
    localport,
    proxy_setting: ProxySetting,
    config_dir: str,
) -> str:
    # Opening JSON file
    template = None
    with open(template_path) as json_file:
        template = json.load(json_file)

    template["inbounds"][0]["port"] = localport
    template["outbounds"][0]['settings']['vnext'][0]['address'] = proxy_setting.address
    template["outbounds"][0]['settings']['vnext'][0]['port'] = proxy_setting.port
    template["outbounds"][0]['settings']['vnext'][0]['users'][0]['id'] = proxy_setting.user_id
    template["outbounds"][0]['streamSettings']['realitySettings']['publicKey'] = proxy_setting.public_key
    template["outbounds"][0]['streamSettings']['realitySettings']['shortId'] = proxy_setting.short_id
    template["outbounds"][0]['streamSettings']['realitySettings']['serverName'] = sni

    file_name = get_random_string(8) + '.json'
    file_path = f'{SCRIPTDIR}/{config_dir}/{file_name}'
    with open(file_path, 'w') as fp:
        json.dump(template, fp)

    return file_path

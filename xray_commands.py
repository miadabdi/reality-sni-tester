import subprocess


def getKeys():
    useless_cat_call = subprocess.Popen(
        ["./xray", "x25519"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    output, errors = useless_cat_call.communicate()
    useless_cat_call.wait()
    lines = output.splitlines()
    private_key = lines[0].replace("Private key: ", "")
    public_key = lines[1].replace("Public key: ", "")

    return {"private_key": private_key, "public_key": public_key}


def getUUID():
    useless_cat_call = subprocess.Popen(
        ["./xray", "uuid"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    output, errors = useless_cat_call.communicate()
    useless_cat_call.wait()
    uuid = output.splitlines()[0]

    return uuid

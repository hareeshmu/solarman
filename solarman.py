"""
Collect PV data from the Solarman API and send Power and Energy data (W+kWh) to MQTT
"""

__version__ = "1.0.0"

import http.client
import json
import hashlib
import os
import sys
import time
import signal
import mqtt

CONFIG_PATH = os.environ.get('CONFIG_PATH', os.getcwd() + "/")

def signal_handler(signal, frame):
    print(f"{time_stamp()}: 🛑 [SIGINT] Exiting...")
    time.sleep(1)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def load_config(file):
    """
    Load configuration
    :return:
    """
    with open(file, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
        return config


def time_stamp():
    """
    Return current time in YYYY-MM-DD hh:mm:ss
    :return:
    """
    return time.strftime("%Y-%m-%d %H:%M:%S")


def get_token(url, appid, secret, username, password, orgId=None):
    """
    Get a token from the API
    :return: access_token
    """
    print(f"{time_stamp()}: 🕵️  Getting token from: {url}")

    try:
        passhash = hashlib.sha256(password.encode())
        passhash = passhash.hexdigest()
        conn = http.client.HTTPSConnection(url)
        if orgId:
            print(f"{time_stamp()}: 🕵️  Using organization ID: {orgId}")
            payload = json.dumps({"appSecret": secret, "email": username, "password": passhash, "orgId": orgId})
        else:
            payload = json.dumps({"appSecret": secret, "email": username, "password": passhash})
        headers = {"Content-Type": "application/json"}
        url = f"//account/v1.0/token?appId={appid}&language=en"
        conn.request("POST", url, payload, headers)
        res = conn.getresponse()
        data = json.loads(res.read())
        print(f"{time_stamp()}: 🔥 Token received successfully")
        return data["access_token"]
    except Exception as error:  # pylint: disable=broad-except
        print(f"{time_stamp()}: 😡 Unable to fetch token: {str(error)}")
        return None


def get_station_realtime(url, stationid, token):
    """
    Return station realtime data
    :return: realtime data
    """
    print(f"{time_stamp()}: 🕵️  Fetching station realtime data for station: {stationid}")
    try:
        conn = http.client.HTTPSConnection(url)
        payload = json.dumps({"stationId": stationid})
        headers = {"Content-Type": "application/json", "Authorization": "bearer " + token}
        conn.request("POST", "//station/v1.0/realTime?language=en", payload, headers)
        res = conn.getresponse()
        data = json.loads(res.read())
        print(f"{time_stamp()}: 🔥 Station realtime data received successfully")
        return data
    except Exception as error:  # pylint: disable=broad-except
        print(f"{time_stamp()}: 😡 Unable to fetch station realtime data: {str(error)}")
        return None


def get_device_current_data(url, device_sn, token):
    """
    Return device current data
    :return: current data
    """
    print(f"{time_stamp()}: 🕵️  Fetching data for device: {device_sn}")
    try:
        conn = http.client.HTTPSConnection(url)
        payload = json.dumps({"deviceSn": device_sn})
        headers = {"Content-Type": "application/json", "Authorization": "bearer " + token}
        conn.request("POST", "//device/v1.0/currentData?language=en", payload, headers)
        res = conn.getresponse()
        data = json.loads(res.read())
        print(f"{time_stamp()}: 🔥 Device data received successfully")
        return data
    except Exception as error:  # pylint: disable=broad-except
        print(f"{time_stamp()}: 😡 Unable to fetch device current data: {str(error)}")
        return None

def restruct_and_separate_current_data(data, device):
    """
    Return restructured and separated device current data
    Original data is removed
    :return: new current data
    """
    print(f"{time_stamp()}: 🕵️  Processing data... {device}")

    if data is None:
        print(f"{time_stamp()}: 😡 Error: Unable to process data for device: {device}, data is empty")

    try:
        new_data_list = {}
        if data["dataList"]:
            data_list = data["dataList"]
            for i in data_list:
                del i["key"]
                name = i["name"]
                name = name.replace(" ", "_")
                del i["name"]
                new_data_list[name] = i["value"]
            del data["dataList"]
        return new_data_list
    except Exception as error:  # pylint: disable=broad-except
        print(f"{time_stamp()}: 😡 Error while processing data: {str(error)}")
        return None

def run(config):
    """
    Output current watts and kilowatts
    :return:
    """

    token = get_token(config["url"], config["appid"], config["secret"], config["username"], config["password"], config["orgId"])

    if token is None:
        print(f"{time_stamp()}: 😡 Unable to get token")
        return

    if config["debug"]:
        print(f"{time_stamp()}: 🕵️  Token: {token}")
    
    station_data = get_station_realtime(config["url"], config["stationId"], token)
    inverter_data = get_device_current_data(config["url"], config["inverterId"], token)
    logger_data = get_device_current_data(config["url"], config["loggerId"], token)

    inverter_data_list = restruct_and_separate_current_data(inverter_data, "Inverter")
    logger_data_list = restruct_and_separate_current_data(logger_data, "Logger")

    if config["debug"]:
        print(f"{time_stamp()}: ⚡ Station data:")
        print(json.dumps(station_data, indent=4, sort_keys=True))

        print(f"{time_stamp()}: ⚡ Inverter data:")
        print(json.dumps(inverter_data, indent=4, sort_keys=True))

        print(f"{time_stamp()}: ⚡ Inverter Data List:")
        print(json.dumps(inverter_data_list, indent=4, sort_keys=True))

        print(f"{time_stamp()}: ⚡ Logger data:")
        print(json.dumps(logger_data, indent=4, sort_keys=True))

        print(f"{time_stamp()}: ⚡ Logger Data List:")
        print(json.dumps(logger_data_list, indent=4, sort_keys=True))

    discard = ["code", "msg", "requestId", "success"]
    topic = config["mqtt"]["topic"]

    inverter_device_state = inverter_data["deviceState"] if inverter_data is not None and  "deviceState" in inverter_data else None

    if inverter_device_state is None or station_data is None or logger_data is None or station_data is None:
        print(f"{time_stamp()}: 😡 Error: Unable to get inverter data")
        return

    if inverter_device_state == 1:
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: ⚡ Inverter DeviceState: {inverter_device_state} -> Publishing MQTT...")
        print(f"{time_stamp()}: ⚡ Sending station data to mqtt")
        for i in station_data:
            if station_data[i]:
                if i not in discard:
                    mqtt.message(config["mqtt"], topic + "/station/" + i, station_data[i], config["debug"])
        print(f"{time_stamp()}: ⚡ Sending inverter data to mqtt")
        for i in inverter_data:
            if inverter_data[i]:
                if i not in discard:
                    mqtt.message(config["mqtt"], topic + "/inverter/" + i, inverter_data[i], config["debug"])
        print(f"{time_stamp()}: ⚡ Sending inverter data list to mqtt")
        if inverter_data_list:
            mqtt.message(config["mqtt"], topic + "/inverter/attributes", json.dumps(inverter_data_list), config["debug"])
        print(f"{time_stamp()}: ⚡ Sending logger data to mqtt")
        for i in logger_data:
            if logger_data[i]:
                if i not in discard:
                    mqtt.message(config["mqtt"], topic + "/logger/" + i, logger_data[i], config["debug"])
        print(f"{time_stamp()}: ⚡ Sending logger data list to mqtt")
        if logger_data_list:
            mqtt.message(config["mqtt"], topic + "/logger/attributes", json.dumps(logger_data_list), config["debug"])
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: ⚡ Inverter DeviceState: {inverter_device_state} -> Publishing MQTT Completed")
    else:
        print(f"{time_stamp()}: ⚡ Device is not online (may be due to nighttime shutdown), sending only status to mqtt")
        mqtt.message(config["mqtt"], topic + "/inverter/deviceState", inverter_data["deviceState"], config["debug"])
        mqtt.message(config["mqtt"], topic + "/logger/deviceState", logger_data["deviceState"], config["debug"])
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: ⚡ Inverter DeviceState: {inverter_device_state} -> Only Status MQTT publish")


if __name__ == "__main__":
    
    if sys.version_info < (3, 5):
        raise Exception("🐍 This script requires Python 3.5+")

    print(f"{time_stamp()}: ⚡ Starting Solarman data fetching...")

    config_file = CONFIG_PATH + "config.json"

    print(f"{time_stamp()}: 🕵️  Loading config file: {config_file}")

    if os.path.exists(config_file):
        config = load_config(config_file)
        interval = config.get("interval", 300)
        if(len(sys.argv) > 1):
            if(sys.argv[1] == "--repeat"):
                while True:     
                    run(config)
                    print(f"{time_stamp()}: 💀 Sleeping for {interval} seconds...")
                    time.sleep(interval)
            else:
                print(f"{time_stamp()}: ❓ Unrecognized parameter '" + sys.argv[1] + "'. Expected '--repeat', Stopping now.")
        else:
            print(f"{time_stamp()}: 🔥 Starting single run, use the argument '--repeat' to repeat at interval...")
            run(config)
    else:
        print(f"{time_stamp()}: 😡 Error reading config.json, sleeping 60sec before exit...")
        time.sleep(60)
        sys.exit(1)
    
    print(f"{time_stamp()}: 💀 Exiting...")
    time.sleep(1)
    sys.exit(0)
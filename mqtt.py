"""
MQTT connect and publish
"""

import logging
import random
import time
from paho.mqtt import client as mqtt_client

def time_stamp():
    """
    Return current time in YYYY-MM-DD hh:mm:ss
    :return:
    """
    return time.strftime("%Y-%m-%d %H:%M:%S")

def connect_mqtt(broker, port, username, password):
    """
    Create an MQTT connection
    :param broker: MQTT broker
    :param port: MQTT broker port
    :param username: MQTT username
    :param password: MQTT password
    :return:
    """
    print(f"{time_stamp()}: 🔥 Connecting mqtt: {broker} on port: {port} as user: {username}")
    client_id = f'solarman-{random.randint(0, 1000)}'
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.connect(broker, port)
    return client


def publish(client, topic, msg, debug):
    """
    Publish a message on a MQTT topic
    :param client: Connect parameters
    :param topic: MQTT topic
    :param msg: Message payload
    :return:
    """
    if debug:
        print(f"{time_stamp()}: 🔥 Publishing message to mqtt: {msg} on topic: {topic}")
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        print(f"{time_stamp()}: 🔥 MQTT message published to topic: {topic}")
    else:
        print(f"{time_stamp()}: 😡 Failed to send mqtt message to topic: {topic}")


def message(config, topic, msg, debug):
    """
    MQTT Connect and send
    :param config: Broker configuration
    :param topic: MQTT topic
    :param msg: Message payload
    """
    try:
        client = connect_mqtt(config["broker"], config["port"], config["username"], config["password"])
        publish(client, topic, msg, debug)
    except Exception as error:  # pylint: disable=broad-except
        print(f"{time_stamp()}: 😡 Unable to connect mqtt: {str(error)}")

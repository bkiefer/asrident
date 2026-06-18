#!/usr/bin/env -S python3 -u

# This test script assumes that an MQTT broker and an asrident docker image are
# running.

# test_msgs contains MQTT messages to process a file, then set the speaker id,
# then process the same file again, so that the recognised speaker should be
# the same.

# The ASR can also be tested interactively using the app MQTT_Explorer
# https://mqtt-explorer.com/ to check the produced messages. Make sure your
# audio setup is correctly reflected in the config file

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import logging
import time
import yaml
import argparse
import json
import threading

# configure logger
logging.basicConfig(
    format="%(asctime)s: %(levelname)s: %(message)s",
    level=logging.INFO)
logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)

DELAY_SECONDS = 2

class TestClass():
    """
    This picks up all communication on the topics specified in the config
    under `topics` and dumps the incoming strings (this is a strong assumption) into a file, with timestamp.
    """

    def __init__(self):
        self.pid = "asrident_test"
        self.topics = { 'whisperasr/asrresult/en': self.on_asrresult }
        self.__init_client()

    def __init_client(self):
        self.client = mqtt.Client(CallbackAPIVersion.VERSION2)
        # self.client.username_pw_set(self.mqtt_username, self.mqtt_password)
        # self.client.on_connect = self.__on_mqtt_connect
        self.client.on_message = self._on_message
        self.client.on_connect = self._on_connect
        self.client.on_subscribe = self._on_subscribe
        self.client.on_disconnect = self._on_disconnect

    def mqtt_connect(self, wait_forever=False):
        host = 'localhost'
        port = 1883
        logger.info(f"connecting to: {host}:{port}")
        self.client.connect(host, port)
        if wait_forever:
            self.client.loop_forever()
        else:
            self.client.loop_start()

    def mqtt_disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        logger.info(f'CONNACK received with code {str(reason_code)}')
        # subscribe to all registered topics/callbacks
        for topic in self.topics:
            qos = 0
            if topic is tuple:
                qos = topic[1]
                topic = topic[0]
            self.client.subscribe(topic, qos)

    def _on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        logger.debug("Subscribed: "+str(properties)+" "+str(reason_code_list))

    def _on_message(self, client, userdata, message):
        logger.debug(f"Received message {str(message.payload)} on topic {message.topic} with QoS {str(message.qos)}")
        if message.topic not in self.topics:
            self.topics[message.topic] = None
            for topic in self.topics:
                if mqtt.topic_matches_sub(topic, message.topic):
                    self.topics[message.topic] = self.topics[topic]
        cb = self.topics[message.topic]
        if cb is not None:
            if cb is tuple:
                cb = cb[0]  # second is qos
            cb(client, userdata, message)
        return

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        logger.info('Disconnecting...')
        self.is_running = False

    def publish(self, topic: str, message: str):
        self.client.publish(topic, message)

    def send_wav(self, state=1, delay:float=DELAY_SECONDS):
        event = threading.Event()
        event.wait(delay)
        self.state = state
        self.publish('whisperasr/control',
                     'process_file:audio/play_the_next_song.wav')

    def on_asrresult(self, client, userdata, message):
        asrresult = json.loads(message.payload)
        if self.state == 1:
            if asrresult['text'].strip().lower().find('play the next song') >= 0:
                print(f"Success {self.state}")
            else:
                print(f"Failure {self.state}")
            id = asrresult["id"]
            self.publish('whisperasr/speakeridentification',
                         f'{{ "id": "{id}", "speaker": "MainSpeaker" }}')
            self.send_wav(2, DELAY_SECONDS / 2)
        elif self.state == 2:
            if asrresult['speaker'] == 'MainSpeaker':
                print(f"Success {self.state}")
            else:
                print(f"Failure {self.state}")
            self.publish('whisperasr/control', 'exit')
            self.mqtt_disconnect()

    def run(self, wait_forever=True):
        try:
            self.is_running = True
            # start thread that sends out the first message after n seconds
            send_thread = threading.Thread(target=self.send_wav)
            send_thread.start()
            self.mqtt_connect(wait_forever=wait_forever)
        except Exception as e:
            logger.error('Exception: {}'.format(e))
        finally:
            if self.client.is_connected():
                self.publish('whisperasr/control', 'exit')
            self.mqtt_disconnect()


def main():
    tc = TestClass()
    tc.run()

if __name__ == '__main__':
    main()

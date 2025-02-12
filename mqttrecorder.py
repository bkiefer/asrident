#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import time
import yaml
import argparse


class MqttRecorder():
    """
    This picks up all communication on the topics specified in the config
    under `topics` and dumps the incoming strings (this is a strong assumption) into a file, with timestamp.
    """


    def __init__(self, config, out_filename):
        self.config = config
        self.callbacks = {}
        self.out = out_filename
        self.__init_client()

    def __init_client(self):
        self.client = mqtt.Client(CallbackAPIVersion.VERSION2)
        # self.client.username_pw_set(self.mqtt_username, self.mqtt_password)
        # self.client.on_connect = self.__on_mqtt_connect
        self.client.on_message = self._on_message
        self.client.on_connect = self._on_connect
        self.client.on_subscribe = self._on_subscribe

    def __subscribe_topics(self, topics):
        for topic in topics:
            self.register_callback(topic, self.dump_string)


    def dump_string(self, message):
        now = time.time()
        msg = str(message.payload.decode("utf-8"))
        now = str(now)
        self.out.write(now + '\t' + message.topic + '\t' + msg + '\n')


    def mqtt_connect(self, background=False):
        host = 'localhost'
        port = 1883
        if 'mqtt_address' in self.config:
            hostport = self.config['mqtt_address'].split(':')
            host = hostport[0]
            if len(hostport) > 1:
                port = int(hostport[1])
        print("connecting to: " + host + " ", end="")
        self.client.connect(host, port)
        if background:
            self.client.loop_forever()
        else:
            self.client.loop_start()

    def mqtt_disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        print('CONNACK received with code %s. ' % str(reason_code), end="")
        self.__subscribe_topics(config['topics'])

    def _on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        print("Subscribed: "+str(mid)+" "+str(reason_code_list))

    def _on_message(self, client, userdata, message):
        if message.topic not in self.callbacks.keys():
            self.callbacks[message.topic] = None
            for topic in self.callbacks:
                if mqtt.topic_matches_sub(topic, message.topic):
                    self.callbacks[message.topic] = self.callbacks[topic]
        cb = self.callbacks[message.topic]
        if cb is not None:
            cb(message)
        return

    def publish(self, topic: str, message: str):
        self.client.publish(topic, message)

    def register_callback(self, topic: str, fn):
        self.client.subscribe(topic)
        self.callbacks[topic] = fn

    def run(self, background=False):
        try:
            self.is_running = True
            self.out = open(self.out, 'w', encoding='utf-8')
            self.mqtt_connect(background=background)
        except Exception as e:
            print('Error in initialization: {}'.format(e))
            self.out.close()
        finally:
            if not background:
                self.out.close()
                print('Disconnecting...')
                self.is_running = False
                self.mqtt_disconnect()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='MQTT Recorder',
        description='Listen to mqtt topics and dump messages published there to a log file',
        epilog='')
    parser.add_argument("-c", "--config", type=str,
                        required=True, help='config file')
    parser.add_argument("-o", "--output-file", type=str,
                        required=False, help='message dump file')
    parser.add_argument('files', metavar='files', type=str, nargs='*')
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    if args.output_file:
        output_file = args.output_file
    elif args.files:
        output_file = args.files[0]
    else:
        output_file = 'out.log'
    m = MqttRecorder(config, output_file)
    m.run(background=True)
    m.mqtt_disconnect()

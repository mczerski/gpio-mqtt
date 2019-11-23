#!/usr/bin/env python
from sysfs.gpio import Controller, INPUT
import paho.mqtt.client as mqtt
import time
import json
import argparse
import os


class GPIO_MQTT:
    def __init__(self, brokerHost, brokerPort, rootTopic, gpioPins):
        self._rootTopic = rootTopic
        self._mqttClient = mqtt.Client()
        self._mqttClient.on_connect = self._mqtt_on_connect
        self._mqttClient.on_message = self._mqtt_on_message
        self._brokerHost = brokerHost
        self._brokerPort = brokerPort
        Controller.available_pins = gpioPins
        self._gpioPins = {pin: Controller.alloc_pin(pin, INPUT) for pin in gpioPins}
        self._gpioValues = {pin: gpio.read() for pin, gpio in self._gpioPins.items()}

    def _mqtt_on_connect(self, client, userdata, flags, rc):
        print('connected to [%s:%s] with result code %d' % (self._brokerHost, self._brokerPort, rc))
        self._mqttClient.subscribe(self._rootTopic + "in/#")
        for gpioPin in self._gpioPins:
            self._sendGpioValue(gpioPin)

    def _mqtt_on_message(self, client, obj, msg):
        payload = msg.payload.decode("utf-8")
        print ('received topic: %s. payload: %s' % (msg.topic, payload))
        parts = msg.topic.split("/")[1:]
        gpioPin = int(parts[0])
        if gpioPin not in self._gpioPins:
            print('unknown pin %d' % gpioPin)
        command = parts[1]
        if command == 'get':
            self._sendGpioValue(gpioPin)
        else:
            print('unknown command %s' % command)

    def _makeTopic(self, gpioPin):
        return "/".join([self._rootTopic+'out', str(gpioPin), 'state'])

    def _sendMessage(self, topic, payload):
        print('sending topic: %s. payload: %s' % (topic, payload))
        self._mqttClient.publish(topic, payload)

    def _sendGpioValue(self, gpioPin):
        value = str(self._gpioValues[gpioPin])
        topic = self._makeTopic(gpioPin)
        self._sendMessage(topic, value)

    def _gpioLoop(self):
        while True:
            for gpioPin, gpio in self._gpioPins.items():
                prev = self._gpioValues[gpioPin]
                curr = gpio.read()
                self._gpioValues[gpioPin] = curr
                if prev != curr:
                    topic = self._makeTopic(gpioPin)
                    self._sendMessage(topic, str(curr))
            time.sleep(1)

    def run(self):
        self._mqttClient.connect_async(self._brokerHost, self._brokerPort)
        self._mqttClient.loop_start()
        while True:
            try:
                self._gpioLoop()
            except KeyboardInterrupt:
                self._mqttClient.loop_stop()
                break

configPath = "/etc/gpio-mqtt.json"
config = {}
if os.path.exists(configPath):
    config = json.load(open(configPath))

parser = argparse.ArgumentParser()
parser.add_argument('--broker-host', default='localhost')
parser.add_argument('--broker-port', type=int, default=1883)
parser.add_argument('--gpio-pins', default=config.get('pins', []), type=int, nargs='+')
args = parser.parse_args()

rootTopic = 'gpio'

gpio_mqtt = GPIO_MQTT(args.broker_host, args.broker_port, rootTopic, args.gpio_pins)
gpio_mqtt.run()


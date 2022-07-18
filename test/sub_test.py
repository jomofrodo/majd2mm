#!/usr/bin/python
import paho.mqtt.client as mqtt

broker_url = "localhost"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

testPayload='{"email":"jomofrodo@gmail.com", "listName":"ccb_genrl"}'
client.publish(topic="SubscribeList", payload=testPayload, qos=1, retain=False)

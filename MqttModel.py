import paho.mqtt.client as mqtt


class MQTTModel:
    subTopics = ["info/switch/LS01"]

    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def Connect(self, host, port=1883, keepalive=60):
        self.client.connect(host, port, keepalive)

    def Run(self):
        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        self.client.loop_forever()

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        for subTopic in self.subTopics:
            client.subscribe(subTopic)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print("%s: %s" % (msg.topic, msg.payload))

    def SetMessageEvent(self, func):
        self.client.on_message = func

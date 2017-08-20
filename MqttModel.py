import paho.mqtt.client as mqtt


class MQTTModel:
    subTopics = []

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

    def subscribe(self, topic):
        is_found = False
        listen_topic = 'info/' + topic
        for sub_topic in self.subTopics:
            if listen_topic == sub_topic:
                is_found = True
                break
        if not (is_found):
            self.subTopics.append(listen_topic)
            self.client.subscribe(listen_topic)

    def unsubscribe(self, topic):
        self.client.unsubscribe('info/' + topic)

    def publish(self, topic, payload):
        self.client.publish(topic, payload)

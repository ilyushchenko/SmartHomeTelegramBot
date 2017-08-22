import logging
import threading
import config.settings as config
from BotModel import BotModel
from MqttModel import MQTTModel

def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    mqttclient = MQTTModel()
    bot = BotModel(config.token, mqttclient)
    mqttclient.Connect(config.MQTTAddress)
    mqttThread = threading.Thread(target=mqttclient.Run)
    botThread = threading.Thread(target=bot.run)
    mqttThread.start()
    botThread.start()

if __name__ == "__main__":
    main()
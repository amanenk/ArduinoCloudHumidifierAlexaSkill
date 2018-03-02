#it must be installed locally use: pip install paho-mqtt -t ./
import paho.mqtt.client as mqtt
import logging


# The callback for when the client receives a CONNACK response from the server.
class MQTT_client:
    result = None
    #type of message that client need to send 0 - undefined, 1 - turn on, 2- tutn off, 3 - set color
    subscribeTopic = None
    publishTopic = None
    client = mqtt.Client()
    message = None
    logger = logging.getLogger()

    def on_connect(self, client, userdata, flags, rc):
        self.logger.info("Connected with result code "+str(rc))
        self.logger.debug("subscribe to " + self.subscribeTopic)
        self.logger.debug("publish to " + self.publishTopic)

        client.subscribe(self.subscribeTopic)
        if self.message is None:   
            client.publish(self.publishTopic,"")
        else:
            client.publish(self.publishTopic, self.message)


    def on_disconnect(self, client, userdata, rc):
        self.logger.info("on_disconnect")
        client.disconnect()


    def on_message(self, client, userdata, msg):
        self.logger.info(msg.topic+" "+str(msg.payload))
        self.result = msg.payload
        client.disconnect()

    def on_publish(self, client, userdata, mid):
        self.logger.info("on_publish")

    def send_message(self, subTopic, pubTopic, msg):
        self.publishTopic = pubTopic
        self.subscribeTopic = subTopic
        self.message = msg
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish

        self.client.connect("test.mosquitto.org", 1883, 2)
        self.client.reconnect_delay_set(999)

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.     

        self.logger.info("before loop")
        self.client.loop_forever()
        self.logger.info("after loop")
        self.logger.debug("result: "+str(self.result))
        return self.result

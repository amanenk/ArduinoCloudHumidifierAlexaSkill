
from mqtt_client import MQTT_client
from response import Response
import skill_utils
import logging


# topics are used to controll the device
state_report = "humidifier/stateReport"
on_topic = "humidifier/on"
off_topic = "humidifier/off"
report_state = "humidifier/reportState"


logger = logging.getLogger()

#main method of device handle
def handle(request):
    request_namespace = request["directive"]["header"]["namespace"]
    request_name = request["directive"]["header"]["name"]

    if request_namespace == "Alexa.PowerController":
        if request_name == "TurnOn":
            client = MQTT_client()            
            result = None
            while result == None:
                result = client.send_message(state_report, on_topic, None)
            result = result.decode('UTF-8')
            logger.debug(result)
            if result == '1':
                logger.debug("device is turned on")
                value = "ON"
            else:
                logger.debug("device is turned off")
                value = "OFF"
        else:
            client = MQTT_client()
            result = None
            while result == None:
                result = client.send_message(state_report, off_topic, None)
            result = result.decode('UTF-8')
            logger.debug(result)
            if result == '1':
                logger.debug("device is turned on")
                value = "ON"
            else:
                logger.debug("device is turned off")
                value = "OFF"

        context = {
            "properties": [
                {
                    "namespace": "Alexa.PowerController",
                    "name": "powerState",
                    "value": value,
                    "timeOfSample": skill_utils.get_utc_timestamp(),
                    "uncertaintyInMilliseconds": 5000
                }
            ]
        }

        response_object = Response(request)
        response_object.set_context(context)
        response = response_object.get_response()
        return response

    elif request_namespace == "Alexa":
        if request_name == "ReportState":
            client = MQTT_client()
            result = client.send_message(
                state_report, report_state, None)
            result = result.decode('UTF-8')
            logger.debug(result)
            if result == '1':
                logger.debug("device is turned on")
                value = "ON"
            else:
                logger.debug("device is turned off")
                value = "OFF"

            context = {
                "properties": [
                    {
                        "namespace": "Alexa.PowerController",
                        "name": "powerState",
                        "value": value,
                        "timeOfSample": skill_utils.get_utc_timestamp(),
                        "uncertaintyInMilliseconds": 5000
                    }
                ]
            }

            response_object = Response(request)
            response_object.set_context(context)            
            response_object.set_response_type("StateReport")
            response = response_object.get_response()
            return response

import colorsys
from mqtt_client import MQTT_client
from response import Response
import skill_utils
import logging


# topics are used to controll the device
state_report = "humidifier/colorStateReport"
color_topic = "humidifier/color"
report_state = "humidifier/reportColorState"

logger = logging.getLogger()

#main method of device handle
def handle(request):
    request_namespace = request["directive"]["header"]["namespace"]
    request_name = request["directive"]["header"]["name"]

    if request_namespace == "Alexa.PowerController":
        if request_name == "TurnOn":
            client = MQTT_client()
            result = client.send_message(state_report, color_topic, bytes([10, 10, 10]))
            
            h, l, s = result_to_HLS(result)

            logger.debug("hls")
            for x in h, l, s:
                logger.debug(x)
            if l > 0:
                logger.debug("device is turned on")
                value = "ON"
            else:
                logger.debug("device is turned off")
                value = "OFF"
        else:
            client = MQTT_client()
            result = client.send_message(state_report, color_topic, bytes([0, 0, 0]))
            
            h, l, s = result_to_HLS(result)

            logger.debug("hls")
            for x in h, l, s:
                logger.debug(x)
            if l > 0:
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

    elif request_namespace == "Alexa.BrightnessController":
        if request_name == "SetBrightness":
            client = MQTT_client()

            result = client.send_message(state_report, report_state, None)
            
            h, l, s = result_to_HLS(result)

            logger.debug("hls")
            for x in h, l, s:
                logger.debug(x)
            
            l = int(request["directive"]["payload"]["brightness"])/100/2

            logger.debug("hls new")
            for x in h, l, s:
                logger.debug(x)

            r, g, b = colorsys.hls_to_rgb(h, l, s)

            logger.debug("rgb")
            for x in r, g, b:
                logger.debug(x)

            result = client.send_message(state_report, color_topic, bytes(
                [int(r*255), int(g*255), int(b*255)]))
            
            h, l, s = result_to_HLS(result)

            logger.debug("hls")
            for x in h, l, s:
                logger.debug(x)

            context = {
                "properties": [
                    {
                        "namespace": "Alexa.BrightnessController",
                        "name": "brightness",
                        "value": int(l*100*2) if int(l*100*2) <= 100 else 100,
                        "timeOfSample": skill_utils.get_utc_timestamp(),
                        "uncertaintyInMilliseconds": 5000
                    }
                ]
            }

            response_object = Response(request)
            response_object.set_context(context)
            response = response_object.get_response()
            return response
        elif request_name == "AdjustBrightness":
            client = MQTT_client()

            result = client.send_message(state_report, report_state, None)
            
            h, l, s = result_to_HLS(result)

            logger.debug("hls")
            for x in h, l, s:
                logger.debug(x)
            
            l =  l + int(request["directive"]["payload"]["brightnessDelta"])/100/2
            if l < 0: l = 0
            if l > 1: l = 1

            logger.debug("hls new")
            for x in h, l, s:
                logger.debug(x)

            r, g, b = colorsys.hls_to_rgb(h, l, s)

            logger.debug("rgb")
            for x in r, g, b:
                logger.debug(x)

            result = client.send_message(state_report, color_topic, bytes(
                [int(r*255), int(g*255), int(b*255)]))
            
            h, l, s = result_to_HLS(result)

            logger.debug("hls")
            for x in h, l, s:
                logger.debug(x)

            context = {
                "properties": [
                    {
                        "namespace": "Alexa.BrightnessController",
                        "name": "brightness",
                        "value": int(l*100*2) if int(l*100*2) <= 100 else 100,
                        "timeOfSample": skill_utils.get_utc_timestamp(),
                        "uncertaintyInMilliseconds": 5000
                    }
                ]
            }

            response_object = Response(request)
            response_object.set_context(context)
            response = response_object.get_response()
            return response
    elif request_namespace == "Alexa.ColorController":
        if request_name == "SetColor":
            client = MQTT_client()

            result = client.send_message(
                state_report, report_state, None)

            h = request["directive"]["payload"]["color"]["hue"]/360
            l = request["directive"]["payload"]["color"]["brightness"]/2
            s = request["directive"]["payload"]["color"]["saturation"]

            logger.debug("hls")
            for x in h, l, s:
                logger.debug(x)

            r, g, b = colorsys.hls_to_rgb(h, l, s)

            logger.debug("rgb")
            for x in r, g, b:
                logger.debug(x)

            result = client.send_message(
                state_report, color_topic, bytes([int(r*255), int(g*255), int(b*255)]))

            
            h, l, s = result_to_HLS(result)

            context = {
                "properties": [
                    {
                        "namespace": "Alexa.ColorController",
                        "name": "color",
                        "value": {
                            "hue": int(h*360),
                            "saturation": s,
                            "brightness": l*2 if l*2 <= 1 else 1
                        },
                        "timeOfSample": skill_utils.get_utc_timestamp(),
                        "uncertaintyInMilliseconds": 5000
                    }
                ]
            }
            response_object = Response(request)
            response_object.set_context(context)
            response = response_object.get_response()
            return response

    elif request_namespace == "Alexa.ColorTemperatureController":
        if request_name == "SetColorTemperature":
            client = MQTT_client()

            from temperature_util import temperatureToRgb
            r, g, b = temperatureToRgb(
                request["directive"]["payload"]["colorTemperatureInKelvin"])

            logger.debug("rgb")
            for x in r, g, b:
                logger.debug(x)

            result = client.send_message(
                state_report, color_topic, bytes([r, g, b]))

            
            h, l, s = result_to_HLS(result)

            logger.debug("hls")
            for x in h, l, s:
                logger.debug(x)

            context = {
                "properties": [
                    {
                        "namespace": "Alexa.ColorTemperatureController",
                        "name": "colorTemperatureInKelvin",
                        "value": request["directive"]["payload"]["colorTemperatureInKelvin"] ,
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

            result = client.send_message(state_report, report_state, None)
            
            h, l, s = result_to_HLS(result)

            for x in h, l, s:
                logger.debug(x)

            context = {
                "properties": [
                    {
                        "namespace": "Alexa.ColorController",
                        "name": "color",
                        "value": {
                                "hue": int(h*360),
                                "saturation": s,
                                "brightness": l*2 if l*2 <= 1 else 1
                        },
                        "timeOfSample": skill_utils.get_utc_timestamp(),
                        "uncertaintyInMilliseconds": 5000
                    },
                    {
                        "namespace": "Alexa.PowerController",
                        "name": "powerState",
                        "value": "ON" if l > 0 else "OFF",
                        "timeOfSample": skill_utils.get_utc_timestamp(),
                        "uncertaintyInMilliseconds": 5000
                    },
                    {
                        "namespace": "Alexa.BrightnessController",
                        "name": "brightness",
                        "value": int(l*100*2) if int(l*100*2) <= 100 else 100,
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


def result_to_HLS(c):
    if c is None:
        c = 0
    else:
        c = int(c)
    r, g, b = (c >> 16) & 255,(c >> 8) & 255, c & 255
    logger.debug("rgb")
    for x in (r,g,b):
        logger.debug(x)
    return colorsys.rgb_to_hls(r/255, g/255, b/255)

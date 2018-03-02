#simple response builder class
import json
import skill_utils

class Response:
    response = {}

    # TODO create class fro the event
    def set_event(self):
        self.response["event"] = {
            "header": {
                "namespace": "Alexa",
                "name": "Response",
                "payloadVersion": "3",
                "messageId": skill_utils.get_uuid(),
                "correlationToken": self.request["directive"]["header"]["correlationToken"]
            },
            "endpoint": {
                "scope": {
                    "type": "BearerToken",
                    "token": "access-token-from-Amazon"
                },
                "endpointId": self.request["directive"]["endpoint"]["endpointId"]
            },
            "payload": {}
        }
    
    def set_context(self, context):
        self.response["context"] = context

    def set_response_type(self, response_type):
        self.response["event"]["header"]["name"] = response_type

    def set_response_payload(self, payload):
        self.response["event"]["payload"] = payload

    def get_response(self):
        return self.response

    def __init__(self, request):
        self.request = request
        self.set_event()

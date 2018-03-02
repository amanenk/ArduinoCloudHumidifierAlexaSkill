# -*- coding: utf-8 -*-

# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Amazon Software License (the "License"). You may not use this file except in
# compliance with the License. A copy of the License is located at
#
#    http://aws.amazon.com/asl/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific
# language governing permissions and limitations under the License.

"""Alexa Smart Home Lambda Function Sample Code.

This file demonstrates some key concepts when migrating an existing Smart Home skill Lambda to
v3, including recommendations on how to transfer endpoint/appliance objects, how v2 and vNext
handlers can be used together, and how to validate your v3 responses using the new Validation
Schema.

Note that this example does not deal with user authentication, only uses virtual devices, omits
a lot of implementation and error handling to keep the code simple and focused.
"""
#ask lambda upload --function humidifier_test --src .\lambda\smartHome\

import logging
import json
import colorsys
import importlib

# Imports for v3 validation
from validation import validate_message
import skill_utils

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# To simplify this sample Lambda, we omit validation of access tokens and retrieval of a specific
# user's appliances. Instead, this array includes a variety of virtual appliances in v2 API syntax,
# and will be used to demonstrate transformation between v2 appliances and v3 endpoints.

sampleEndpoints = json.load(open('endpoints.json'))


def lambda_handler(request, context):
    """Main Lambda handler.

    Since you can expect both v2 and v3 directives for a period of time during the migration
    and transition of your existing users, this main Lambda handler must be modified to support
    both v2 and v3 requests.
    """

    try:
        logger.info("Directive:")
        logger.info(json.dumps(request, indent=4, sort_keys=True))

        if request["directive"]["header"]["name"] == "Discover":
            response = handle_discovery(request)
        elif request["directive"]["header"]["name"] == "AcceptGrant":
            response = handle_authorization(request)
        else:
            response = handle_actions(request)

        logger.info("Response:")
        logger.info(json.dumps(response, indent=4, sort_keys=True))

        logger.info("Validate v3 response")
        validate_message(request, response)

        return response
    except ValueError as error:
        logger.error(error)
        raise


def handle_discovery(request):
    endpoints = []
    for endpoint in sampleEndpoints:
        endpoints.append(endpoint["endpoint"])

    response = {
        "event": {
            "header": {
                "namespace": "Alexa.Discovery",
                "name": "Discover.Response",
                "payloadVersion": "3",
                "messageId": skill_utils.get_uuid()
            },
            "payload": {
                "endpoints": endpoints
            }
        }
    }
    return response


def handle_authorization(request):
    response = {
        "event": {
            "header": {
                "namespace": "Alexa.Authorization",
                "name": "AcceptGrant.Response",
                        "payloadVersion": "3",
                        "messageId": skill_utils.get_uuid()
            },
            "payload": {}
        }
    }
    return response


def handle_actions(request):
    endpoint = get_endpoint_by_endpoint_id(
        request["directive"]["endpoint"]["endpointId"])

    #if endpoint is not found respond with error
    if endpoint is None:
        response = {
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "ErrorResponse",
                    "messageId": skill_utils.get_uuid(),
                    "correlationToken": request["directive"]["header"]["correlationToken"],
                    "payloadVersion": "3"
                },
                "endpoint": request["directive"]["endpoint"],
                "payload": {
                    "type": "ENDPOINT_UNREACHABLE",
                    "message": "Unable to reach endpoint it is None"
                }
            }
        }
        return response


    #if endpoint hes no interface requested response with error
    if check_enpoint_capability(endpoint, request) == False:
        response = {
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "ErrorResponse",
                    "messageId": skill_utils.get_uuid(),
                    "correlationToken": request["directive"]["header"]["correlationToken"],
                    "payloadVersion": "3"
                },
                "endpoint": request["directive"]["endpoint"],
                "payload": {
                    "type": "INVALID_DIRECTIVE",
                    "message": "This endpoint can`t do this"
                }
            }
        }
        return response
    
    #import the file described in the endpoints.json and execute the hadle method
    handler = importlib.import_module('handlers.' + endpoint["handler"])
    response = handler.handle(request)
    return response


def get_endpoint_by_endpoint_id(endpoint_id):
    for endpoint in sampleEndpoints:
        if endpoint["endpoint"]["endpointId"] == endpoint_id:
            logger.debug("found endpoint")
            return endpoint
    logger.error("endpoint is not present")
    return None


def check_enpoint_capability(endpoint, request):
    sample_endpoint = get_endpoint_by_endpoint_id(endpoint["endpoint"]["endpointId"])
    for capability in sample_endpoint["endpoint"]["capabilities"]:
        if capability["interface"] == request["directive"]["header"]["namespace"]:
            return True
    logger.error("unknown interface")
    return False

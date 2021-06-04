# -*- coding: utf-8 -*-

import contact_store

store_location = 'Contacts'
contact_store = contact_store.ContactStore(store_location)


def lambda_handler(event, context):
    intent_name = event['currentIntent']['name']
    parameters = event['currentIntent']['slots']
    attributes = event['sessionAttributes'] if event['sessionAttributes'] is not None else {}

    response = lookup_phone(intent_name, parameters, attributes)

    return response


def lookup_phone(intent_name, parameters, attributes):
    first_name = parameters['FirstName']
    last_name = parameters['LastName']

    # dynamodb에서 전화 번호 읽기
    name = (first_name + ' ' + last_name).title()
    contact_info = contact_store.get_contact_by_name(name)

    if 'phone' in contact_info:
        attributes['Phone'] = contact_info['phone']
        attributes['FirstName'] = first_name
        attributes['LastName'] = last_name
        response = intent_success(intent_name, parameters, attributes)
    else:
        response = intent_failure(intent_name, parameters, attributes, 'Could not find contact information.')

    return response


#####
# AWS 렉스 도우미 함수
#####
def intent_success(intent_name, parameters, attributes):
    return {
        'sessionAttributes': attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': 'Fulfilled'
        }
    }


def intent_failure(intent_name, parameters, attributes, message):
    return {
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': 'Failed',
            'message': {
                'contentType': 'PlainText',
                'content': message
            }
        }
    }


def intent_delegation(intent_name, parameters, attributes):
    return {
        'sessionAttributes': attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': parameters,

        }
    }


def intent_elicitation(intent_name, parameters, attributes, parameter_name):
    return {
        'sessionAttributes': attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': parameters,
            'slotToElicit': parameter_name
        }
    }

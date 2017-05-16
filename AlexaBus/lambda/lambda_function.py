from db_handler import GtfsDb
import config
import requests
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

HELP_NO_LOCATION = "I can provide you with the next bus coming to a stop near" \
                   " you! Simply allow me to look at your location, and then" \
                   " ask me when the next bus is coming and I will" \
                   " do my best!"

HELP_WITH_LOCATION = "I can provide you with the next bus coming to a stop near" \
                     " you! Simply ask me when the next bus is coming and I will" \
                     " do my best!"

NEED_PERMISSION = "In order to tell you when the next bus is coming, I" \
                  " need permission to look at your device location, sorry"


def lambda_handler(event, context):
    if event['session']['application']['applicationId'] != "amzn1.ask.skill.36cc0cfb-b522-415c-aeb6-bb91d72ac997":
        raise ValueError("Invalid Application ID")

    token, device = get_tokens(event)
    latlon = False

    if token:
        location = get_location(token, device)
        latlon = get_lat_lng(location)

    if event['request']['type'] == 'IntentRequest':
        return on_intent(event['request'], latlon)
    else:
        return get_buses("Get Buses", latlon)


def on_intent(intent_request, latlon):
    intent_name = intent_request['intent']['name']

    if intent_name == "GetBuses":
        return get_buses("Get Buses", latlon)

    elif intent_name == "AMAZON.HelpIntent":
        if not latlon:
            return build_response({}, build_speechlet_response("Help", HELP_NO_LOCATION, "", True))
        else:
            return build_response({}, build_speechlet_response("Help", HELP_WITH_LOCATION, "", True))
    else:
        return build_response({}, build_speechlet_response("Stopping Buster Bus ",
                                                           "Bye", "", True))


def get_location(token, device):
    url = "https://api.amazonalexa.com/v1/devices/{deviceId}/settings/address".format(deviceId=device)

    resp = requests.get(url, headers={'Authorization': 'Bearer {token}'.format(token=token)}).json()

    return resp


def get_lat_lng(loc):
    address = "{0},+{1}+,{2}".format(loc['addressLine1'].replace(" ", "+"), loc['city'].replace(" ", "+"),
                                     loc['stateOrRegion'].replace(" ", "+"))
    url = "https://maps.googleapis.com/maps/api/geocode/json?address={addr}&key={key}".format(addr=address,
                                                                                              key=config.GOOGLE_API_KEY)
    return \
        requests.get("https://maps.googleapis.com/maps/api/geocode/json?address=" + address).json()['results'][0][
            'geometry'][
            'location']


def get_tokens(event):
    """
    Returns the token and device or false
    :param event:
    :return:
    """
    try:
        token = event['context']['System']['user']['permissions']['consentToken']
        device = event['context']['System']['device']['deviceId']
    except KeyError:
        return False, False

    return token, device


def get_buses(card_name, latlon):
    if not latlon:
        speech_output = NEED_PERMISSION

    else:
        db = GtfsDb(config.DB_ENDPOINT, config.DB_NAME, config.DB_USER, config.DB_PASSWORD, config.DB_PORT)

        latlng = (latlon['lat'], latlon['lng'])

        # print (db.get_bus_times_at_stop(stop_id))
        closest_stops = db.get_closest_stops(latlng, 1)

        if len(closest_stops) != 0:
            closest_stop = closest_stops[0]
            closest_id = closest_stop[-2]

            closest_gtfs = closest_stop[-1]

            speech_output = "The closest stop is {0} which is {1} meters away.".format(closest_stop[0],
                                                                                       int(round(closest_stop[1], -1)))

            next_buses = db.get_bus_times_at_stop(closest_id, closest_gtfs)

            word = "is" if len(next_buses) == 1 else "are"

            speech_output += " There {0} {1} bus lines still running to this stop right now.".format(word,
                                                                                                     len(next_buses))
            if len(next_buses) == 0:
                speech_output += " There is a chance I am missing data on this bus service."
            for line in next_buses:
                speech_output += " The next {0} line bus that I know about will arrive at around {1}.".format(line[2],
                                                                                                              line[
                                                                                                                  0].strftime(
                                                                                                                  "%-I:%M %p"))
        else:
            speech_output = "I can't find any bus stops within 500 meters of your location, sorry."

        db.conn.close()

    return build_response({}, build_speechlet_response(
        card_name, speech_output, "", True))


# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


if __name__ == "__main__":
    lambda_handler(None, None)

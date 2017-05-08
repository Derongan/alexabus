from db_handler import GtfsDb
import config
import requests
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.36cc0cfb-b522-415c-aeb6-bb91d72ac997"):
        raise ValueError("Invalid Application ID")

    if event['request']['type'] == 'IntentRequest':
        try:
            token = event['context']['System']['user']['permissions']['consentToken']
            device = event['context']['System']['device']['deviceId']
        except:
            return build_response({}, build_speechlet_response(
                event['request']['intent']['name'], "I need permission to look at your device location, sorry", "",
                True))

        loc = get_location(token, device)
        latlon = get_lat_lng(loc)

        return on_intent(event['request'], event['session'], latlon)


def on_intent(intent_request, ses, latlon):
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    if intent_name == "GetBuses":
        return get_buses(intent, latlon)


def get_location(token, device):
    url = "https://api.amazonalexa.com/v1/devices/{deviceId}/settings/address".format(deviceId=device)

    resp = requests.get(url, headers={'Authorization': 'Bearer {token}'.format(token=token)}).json()

    return resp


def get_lat_lng(loc):
    # 1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=YOUR_API_KEY
    address = "{0},+{1}+,{2}".format(loc['addressLine1'].replace(" ", "+"), loc['city'].replace(" ", "+"),
                                     loc['stateOrRegion'].replace(" ", "+"))
    return \
        requests.get("https://maps.googleapis.com/maps/api/geocode/json?address=" + address).json()['results'][0][
            'geometry'][
            'location']

def get_buses(intent, latlon):
    db = GtfsDb(config.DB_ENDPOINT, config.DB_NAME, config.DB_USER, config.DB_PASSWORD, config.DB_PORT)

    latlng = (latlon['lat'], latlon['lng'])

    # print (db.get_bus_times_at_stop(stop_id))
    closest_stops = db.get_closest_stops(latlng, 1)

    if len(closest_stops) != 0:
        closest_stop = closest_stops[0]
        closest_id = closest_stop[-1]

        closest_gtfs = closest_stop[-2]

        speech_output = "The closest stop is {0} which is {1} meters away.".format(closest_stop[0],
                                                                                   int(round(closest_stop[1], -1)))

        next_buses = db.get_bus_times_at_stop(closest_id, closest_gtfs)

        speech_output += " There are {0} bus lines still running to this stop right now.".format(len(next_buses))
        for line in next_buses:
            speech_output += " The next {0} line bus that I know about will arrive at around {1}".format(line[0], line[
                1].strftime("%-I:%M %p"))

    else:
        speech_output = "I can't find any bus stops near you, sorry"

    db.conn.close()

    return build_response({}, build_speechlet_response(
        intent['name'], speech_output, "", True))


# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
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

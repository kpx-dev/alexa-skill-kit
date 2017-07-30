import logging
import boto3
import json
import requests
import time
import aniso8601
import requests
from base64 import b64decode
from datetime import datetime

__version__ = '1.0.0'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

kms = boto3.client('kms')
base_url = 'https://api.amazonalexa.com/v1'


class VerificationError(Exception):
    pass


class AlexaSkillKit:
    def __init__(self, event):
        self.event = event
        request = event['request']
        session = event['session']
        context = event['context']
        perm = session['user']['permissions']

        self.device_id = context['System']['device']['deviceId']

        self.app_id = session['application']['applicationId']
        self.user_id = session['user']['userId']
        self.new_session = session['new']
        self.token = perm['consentToken'] if 'consentToken' in perm else False

        self.request_id = request['requestId']
        self.timestamp = request['timestamp']
        self.request_type = request['type']
        self.intent = request['intent']['name']
        self.slots = request['intent']['slots']

    def launch(self):
        return self.request_type == 'LaunchRequest'

    def intent(self):
        return self.request_type == 'IntentRequest'

    def session_ended(self):
        return self.request_type == 'SessionEndedRequest'

    def card(self, title, content, small_img=None, large_img=None):
        if small_img or large_img:
            card = self._standard_card(
                title=title,
                content=content,
                small_img=small_img,
                large_img=large_img
            )
        else:
            card = self._simple_card(title=title, content=content)

        return card

    def success(self, speech_text, card=None, speech_text_reprompt=None,
                session_attributes={}):
        speechlet = self._speechlet(
            speech_text=speech_text,
            card=card,
            speech_text_reprompt=speech_text_reprompt
        )

        return self._response(speechlet=speechlet)

    def decrypt(self, key):
        return kms.decrypt(
            CiphertextBlob=b64decode(key))['Plaintext'].decode('utf-8')

    def zipcode(self):
        url = '{}/v1/devices/{}/settings/address/countryAndPostalCode'.format(
            base_url, self.device_id)
        header = {'Authorization': 'Bearer {}'.format(self.token)}

        try:
            res = requests.get(url, headers=header).json()
            # print('zip code detected is ', res['postalCode'])

            return res['postalCode']
        except Exception as e:
            logger.error('Problem getting zipcode', e)

            return None

    def validate(self, app_id):
        if self._validate_app_id(app_id=app_id) and self._validate_timestamp():
            return True

        return False

    def _track_dynamodb(self, table, **kwargs):
        try:
            item = {
                'request_id': self.request_id,
                'date': self.timestamp,
                'user_id': self.user_id,
                'device_id': self.device_id,
                'event': self.event,
                # 'card': kwargs.get('card', {})
            }

            return table.put_item(Item=item)
        except Exception as e:
            logger.error(e)

    def _track_slack(self, webhook, message):
        payload = {'text': message}
        err_msg = 'Problem tracking to Slack'

        try:
            res = requests.post(url=webhook, data=json.dumps(payload))
            if not res.ok:
                logger.error(err_msg, res.text)
        except Exception as e:
            logger.error(err_msg, e)

    def _validate_app_id(self, app_id):
        return app_id == self.app_id

    def _validate_timestamp(self):
        try:
            ts = aniso8601.parse_datetime(self._timestamp())
            dt = datetime.utcnow() - ts.replace(tzinfo=None)

            if abs(dt.total_seconds()) > 150:
                return False
        except Exception as e:
            logger.error('Problem validating request timestamp', e)

            return False

        return True

    def _simple_card(self, title, content):
        return {'type': 'Simple', 'title': title, 'content': content}

    def _standard_card(self, title, content, small_img=None, large_img=None):
        payload = {'type': 'Standard', 'title': title, 'text': content}

        if small_img or large_img:
            # recommend: small 720w x 480h, large 1200w x 800h
            payload['image'] = {
                'smallImageUrl': small_img,
                'largeImageUrl': large_img
            }

        return payload

    def _link_card(self):
        return {'type': 'LinkAccount'}

    def _speechlet(self, speech_text, card=None, speech_text_reprompt=None):
        payload = {
            'outputSpeech': {
                'type': 'PlainText',
                'text': speech_text
            },
            'shouldEndSession': True
        }

        if card:
            payload['card'] = card

        if speech_text_reprompt:
            payload['reprompt'] = {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': speech_text_reprompt
                }
            }

            payload['shouldEndSession'] = False

        return payload

    def _response(self, speechlet, session_attributes={}):
        return {
            'version': '1.0',
            'sessionAttributes': session_attributes,
            'response': speechlet
        }

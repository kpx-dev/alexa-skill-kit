import logging
import boto3
import json
import requests
import time
import aniso8601
import requests
import yaml
import sys
import os

from base64 import b64decode
from datetime import datetime
from pathlib import Path
from functools import wraps

__version__ = '1.0.1'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

kms = boto3.client('kms')
base_url = 'https://api.amazonalexa.com/v1'


class AlexaSkillKit:
    def __init__(self, app_id=None, requires_permission=False):
        self.app_id = app_id
        self.requires_permission = requires_permission

    def init(self, event, requires_permission=False, script_path='alexa_skill_kit/script.yml'):
        self.event = event
        request = event['request']
        session = event['session']
        context = event['context']
        perm = session['user']['permissions']

        self.device_id = context['System']['device']['deviceId']

        self.request_app_id = session['application']['applicationId']
        self.user_id = session['user']['userId']
        self.new_session = session['new']
        self.token = perm['consentToken'] if 'consentToken' in perm else False

        self.request_id = request['requestId']
        self.timestamp = request['timestamp']
        self.request_type = request['type']

        if 'intent' in request:
            self.intent_name = request['intent']['name']
            self.slots = request['intent']['slots']
        else:
            self.intent_name = False
            self.slots = False

        with Path.cwd().joinpath(script_path).open() as f:
            self.script = yaml.load(f)
            # print('script is ', self.script)

    def launch(self):
        return self.request_type == 'LaunchRequest'

    def intent(self):
        return self.request_type == 'IntentRequest'

    def session_ended(self):
        return self.request_type == 'SessionEndedRequest'

    def help(self):
        return self.intent_name and self.intent_name == 'AMAZON.HelpIntent'

    def stop(self):
        return self.intent_name and self.intent_name == 'AMAZON.StopIntent'

    def cancel(self):
        return self.intent_name and self.intent_name == 'AMAZON.CancelIntent'

    def on_trigger(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            self.init(event=kwargs.get('event'))
            valid = self._validate()
            if not valid:
                raise VerificationError('Failed validation.')
            return f(*args, **kwargs)

        return wrapper

    def on_intent(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper

    def on_help(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper

    def on_session_ended(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper

    def on_stop(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper

    def on_cancel(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper

    def on_launch(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # print(self.script['launch'])
            res = f(*args, **kwargs)
            if res:
                return res
            else:
                return self.success(message=self.script['launch'])

        return wrapper

    def success(self, message, message_reprompt=None, card_title=None, card_content=None, small_img=None, large_img=None):
        card = None
        if small_img or large_img:
            card = self._standard_card(title=card_title, content=card_content, small_img=small_img, large_img=large_img)
        elif card_content:
            card = self._simple_card(title=card_title, content=card_content)

        speechlet = self._speechlet(message=message, message_reprompt=message_reprompt, card=card)

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

    def _validate(self):
        if not os.environ.get('ASK_VERIFY'):
            return True

        if self._validate_app_id() and self._validate_timestamp() and self._validate_token():
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

    def _validate_token(self):
        if self.requires_permission:
            if self.token:
                return True
            else:
                return False

    def _validate_app_id(self):
        return self.request_app_id == self.app_id

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
            payload['image'] = {}
            if small_img:
                payload['image']['smallImageUrl'] = small_img
            if large_img:
                payload['image']['largeImageUrl'] = large_img

        return payload

    def _link_card(self):
        return {'type': 'LinkAccount'}

    def _speechlet(self, message, message_reprompt=None, card=None):
        payload = {
            'outputSpeech': {
                'type': 'PlainText',
                'text': message
            },
            'shouldEndSession': True
        }

        if card:
            payload['card'] = card

        if message_reprompt:
            payload['reprompt'] = {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': message_reprompt
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


class VerificationError(Exception):
    pass

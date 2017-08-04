# alexa-skill-kit

Alexa Skill Kit in Python

## Installation

```shell
# install this package from pip
pip install alexa-skill-kit
```

## Usage

**Simple example:**

```python
# your app.py
from alexa_skill_kit import AlexaSkillKit

ask = AlexaSkillKit()

@ask.on_launch
def launch():
    return ask.success(message='Thank you for enabling my skill! You can say this and that.')

@ask.on_intent
def intent():
    return ask.success(message='I got it!', card_title='Card title shows up on Alexa app', card_content='content')

@ask.on_help
def help():
    return ask.success(message='some help message', message_reprompt='This message will play again after a while')

@ask.on_session_ended
def session_ended():
    return ask.success(message='good bye!')

@ask.on_stop
def stop():
    return ask.success(message='good bye!')

@ask.on_trigger
def main(event, context):
# This is the main entry of your Lambda function

    if ask.launch():
        return launch()
    elif ask.intent():
        return intent()
    elif ask.session_ended():
        return session_ended()
    elif ask.help():
        return help()
    elif ask.stop() or ask.cancel():
        return stop()

if __name__ == '__main__':
    # fake event for local development. Look into tests/data/*.json for fake json files
    event = {}
    main(event=event, context={})

```

**Advanced example:**

https://github.com/KNNCreative/EatMe-Alexa-Food-Skill

## Deploy your skill

Set the environment key: `ASK_VERIFY=True`

Deploy using SAM (https://github.com/KNNCreative/EatMe-Alexa-Food-Skill/blob/master/eatme/eatme.yml)

## Development

```shell
# install Pipenv
pip install --upgrade pipenv

# activate shell
pipenv shell --three

# install packages
pipenv install

# run tests make sure everything is working
./script/test
```
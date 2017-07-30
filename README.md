# alexa-skill-kit

Alexa Skill Kit in Python

## Installation

```shell
# install this package from pip
pip install alexa-skill-kit
```

## Usage

Simple example:

```python
# your app.py
from alexa_skill_kit import AlexaSkillKit

def main(event, context):
  ask = AlexaSkillKit(event=event)

  if ask.launch():
    return on_launch()
  elif ask.intent():
    return on_intent()
  elif ask.session_ended()
    return on_session_ended()

def on_launch():
  # handle on launch event. Ex: Alexa Open EatMe
  ask.success(speech_text='Welcome to my skill!')


def on_intent():
  # handle the intent. Ex: Alexa ask EatMe where to eat?
  ask.success(speech_text='You can eat at XYZ')


def on_session_ended():
  # handle ended session. Ex: user doesn't say anything for a while
  ask.success(speech_text='Goodbye, bon appetit!')


if __name__ == '__main__':
    # fake event for local development
    event = {}
    main(event=event, context={})

```

Advanced example:

https://github.com/KNNCreative/EatMe-Alexa-Food-Skill

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
import json
from alexa_skill_kit import AlexaSkillKit
from pathlib import Path

fixture = Path.cwd().joinpath('tests/data/location.json')
with fixture.open() as f:
    event = json.load(f)
ask = AlexaSkillKit(event=event)


def test_init():
    assert ask.device_id == 'xyz'


def test_card():
    title = 'title'
    content = 'content'
    card = ask.card(title=title, content=content)

    assert card['type'] == 'Simple'
    assert card['title'] == title
    assert card['content'] == content


def test_success():
    speech_text = 'speech_text'
    res = ask.success(speech_text=speech_text)

    assert res['response']['outputSpeech']['type'] == 'PlainText'
    assert res['response']['outputSpeech']['text'] == speech_text
    assert res['response']['shouldEndSession'] is True


def test_validate():
    app_id = 'app_id'
    # TODO: freeze time
    # assert ask.validate(app_id=app_id) is True

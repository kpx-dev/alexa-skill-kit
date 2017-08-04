import json
from alexa_skill_kit import AlexaSkillKit

ask = AlexaSkillKit(app_id='amzn1.ask.skill.64f32e53-97ef-4f27-b478-18be3862e5a7', requires_permission=True)

@ask.on_launch
def launch():
    pass
    # return ask.success(message='hola', message_reprompt='what?', )
    # return ask.success(message='hola', message_reprompt='what?', card_title='title', card_content='content')
    # return ask.success(message='hola', message_reprompt='what?', card_title='title', card_content='content', small_img='xyz.jpg', large_img='big.jpg')

@ask.on_intent
def intent():
    pass

@ask.on_help
def help():
    pass

@ask.on_session_ended
def session_ended():
    pass

@ask.on_stop
def stop():
    pass

@ask.on_trigger
def main(event, context):
    # if self.requires_permission and not self.token:
            # return self.success(speech_text=self.script['requires_permission'])

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
    # test_file = 'tests/data/location.json'
    test_file = 'tests/data/launch.json'

    with open(test_file, 'r') as f:
        event = json.load(f)

    res = main(event=event, context={})
    print(json.dumps(res, indent=3))
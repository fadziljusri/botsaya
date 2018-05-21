
from flask import Flask, request
from googletrans import Translator
import requests

# create a Flask app instance
app = Flask(__name__)
app.config.from_object('settings')

translator = Translator()

# method to reply to a message from the sender
def reply(data):
    # Post request using the Facebook Graph API v2.6
    resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" +
                         app.config["ACCESS_TOKEN"], json=data)
    print(resp.content)


# method to translate message from the sender
def translate(user_id, msg):

    data = {"recipient": {"id": user_id}}

    if (msg.lower().find("hi") >= 0) or (msg.lower().find("hello") >= 0):
        data["message"] = {
            "text": "Bot Saya.\nI'm here to translate your english to (bahasa melayu, chinese, or tamil).\n\nLet's start by typing 'Whats up'.."
        }
    elif (msg.lower().find("info") >= 0):
        data["message"] = {
            "attachment":{
                "type":"template",
                "payload": {
                    "template_type": "media",
                    "elements": [
                        {
                        "media_type": "image",
                        "url": "https://www.facebook.com/2053834724835116/photos/a.2053834754835113.1073741825.2053834724835116/2053834784835110/?type=3&theater",
                        "buttons": [
                            {
                                "type": "web_url",
                                "url": "https://www.facebook.com/Bot-Saya-2053834724835116/",
                                "title": "View Website",                                
                            },
                            {
                                "type":"phone_number",
                                "title":"Call Me",
                                "payload":"+60106505576"
                            }
                        ]
                        }
                    ]
                }
            }
        } 

    else:

        bahasa = translator.translate(msg, src='en', dest='ms')
        chinese_simplified = translator.translate(msg, src='en', dest='zh-cn')
        tamil = translator.translate(msg, src='en', dest='ta')
        

        if (msg.lower() == bahasa.text.lower()) and (msg.lower() == chinese_simplified.text.lower()) and (msg.lower() == tamil.text.lower()):
            # normal text
            data["message"] = {"text": "What are you saying?\nI can only understand English"}
        
        else:
            data["message"] = {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": "Translate '" + msg + "' to?",
                        "buttons": [
                            {
                                "type": "postback",
                                "title": "Bahasa Melayu",
                                "payload": bahasa.text.capitalize(),
                            },
                            {
                                "type": "postback",
                                "title": "Chinese - Simplified",
                                "payload": chinese_simplified.text,
                            },
                            {
                                "type": "postback",
                                "title": "Tamil",
                                "payload": tamil.text,
                            }
                        ]
                    }
                }
            }
    
    reply(data)
    

# GET request to handle the verification of tokens
@app.route('/', methods=['GET'])
def handle_verification():
    if request.args['hub.verify_token'] == app.config['VERIFY_TOKEN']:
        return request.args['hub.challenge']
    else:
        return "Invalid verification token"

# POST request to handle in coming messages then call reply()
@app.route('/', methods=['POST'])
def handle_incoming_messages():
    data = request.json
    # print(data)
    sender = data['entry'][0]['messaging'][0]['sender']['id']
    try:
        message = data['entry'][0]['messaging'][0]['message']['text']
        translate(sender, message)
    except KeyError:
        payload = data['entry'][0]['messaging'][0]['postback']['payload']
        # print(payload)

        data = {
            "recipient": {"id": sender},
            "message": {"text": payload, }
        }
        reply(data)

    return "ok"


# Run the application.
if __name__ == '__main__':
    app.run(debug="true")

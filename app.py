
from flask import Flask, request
from googletrans import Translator
import requests

# create a Flask app instance
app = Flask(__name__)
app.config.from_object('settings')

translator = Translator()

# method to reply to a message from the sender
def reply(user_id, msg):

    translated = translator.translate(msg, src='en', dest='ms')
    # print(translated)

    if msg == translated.text:
        sendMsg = "What are you saying?\nI can only understand English... at the moment\n\nSincerely,\nBotter"
    else:
        sendMsg = (translated.text).capitalize() + '\n\nIkhlas,\nBotter'
    
    data = {
        "recipient": {"id": user_id},
        "message": {"text": sendMsg}
    }
    # Post request using the Facebook Graph API v2.6
    resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + app.config["ACCESS_TOKEN"], json=data)
    print(resp.content)

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
    message = data['entry'][0]['messaging'][0]['message']['text']
    reply(sender, message)

    return "ok"

# Run the application.
if __name__ == '__main__':
    app.run(debug=True)
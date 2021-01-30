from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


# set up Flask
app = Flask(__name__)

# set up Twilio
# might not need
account_sid = 'ACa5ad00afdf14b5cc8ea01dfaf2a6d9ff'
auth_token = 'e1caac81c5d7a47628d804ec7f06dc8e'

# set up Firestore
cred = credentials.Certificate('pk.json')
firebase_admin.initialize_app(cred)
db = firestore.client()


@app.route("/", methods=['GET', 'POST'])
def sms():
    print('in sms view')
    # receive message contents
    message_content = request.values.get('Body')

    # maybe update database


    # reply to message
    resp = MessagingResponse()

    if message_content == 'COMMANDS':
        resp_message = 'TODO: display list of pending tasks\n' + 'COMPLETED: display list of completed tasks\n' + 'Task Commands:\n' + 'Add Task: add [task name] [time interval]' + '\n' + 'Cancel Task: cancel [task name]' + '\n' + 'Complete Task: complete [task name]'
        resp.message(resp_message)
    else:
        resp.message('Unknown command: text \'COMMANDS\' for list of commands')

    return str(resp)

if __name__ == "__main__":
    app.run()
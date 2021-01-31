from flask import Flask, request, render_template
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

    # task_format = {
    #     'name': str,
    #     'interval': str
    # }

    try:
        if message_content == 'COMMANDS':
            resp_message = 'TODO: display list of pending tasks\n' + 'COMPLETED: display list of completed tasks\n' + 'Task Commands:\n' + 'Add task: add [task name] [time interval]' + '\n' + 'Cancel task: cancel [task name]' + '\n' + 'Complete task: complete [task name]'
        
        elif message_content == 'TODO':
            # query firestore and return pending tasks
            pending_tasks = []
            docs = db.collection('pending').stream()

            for doc in docs:
                doc_dict = doc.to_dict()
                pending_tasks.append((doc_dict['name'], doc_dict['interval']))

            if len(pending_tasks) == 0:
                resp_message = 'no pending tasks!'
            else:
                resp_message = 'pending tasks:\n'
                for task in pending_tasks:
                    resp_message += f'{task[0]}: {task[1]}\n'
                resp_message += 'keep at it!'
        
        elif message_content == 'COMPLETED':
            # query firestore and return completed tasks
            completed_tasks = []
            docs = db.collection('completed').stream()

            for doc in docs:
                doc_dict = doc.to_dict()
                completed_tasks.append((doc_dict['name'], doc_dict['interval']))

            if len(completed_tasks) == 0:
                resp_message = 'no completed tasks'
            else:
                resp_message = 'completed tasks:\n'
                for task in completed_tasks:
                    resp_message += f'{task[0]}: {task[1]}\n'
                resp_message += 'good work!'

        elif message_content.startswith('Add task:'):
            task = message_content.split(': ')[1].split(' ')
            db.collection('pending').document().set({
                'name': task[0],
                'interval': task[1]
            })
            resp_message = f'successfully added task: {task[0]} for {task[1]}'

        elif message_content.startswith('Cancel task:'):
            task_name = message_content.split(': ')[1]
            docs = db.collection('pending').stream()

            for doc in docs:
                doc_dict = doc.to_dict()
                if doc_dict['name'] == task_name:
                    db.collection('pending').document(doc.id).delete()
            
            resp_message = f'successfully canceled task: {task_name}'
        
        elif message_content.startswith('Complete task:'):
            task_name = message_content.split(': ')[1]
            docs = db.collection('pending').stream()

            for doc in docs:
                doc_dict = doc.to_dict()
                if doc_dict['name'] == task_name:
                    db.collection('completed').document().set({
                        'name': doc_dict['name'],
                        'interval': doc_dict['interval']
                    })
                    db.collection('pending').document(doc.id).delete()
            
            resp_message = f'successfully completed task: {task_name}'

        else:
            resp_message = 'Unknown command: text \'COMMANDS\' for list of commands and syntax'

    except:
        resp_message = 'Something went wrong. Probably a syntax error. Check carefully for spacing and try again.'


    resp.message(resp_message)
    return str(resp)


@app.route("/dashboard", methods=['GET'])
def dashboard():
    pending_tasks = []
    docs = db.collection('pending').stream()

    for doc in docs:
        doc_dict = doc.to_dict()
        pending_tasks.append((doc_dict['name'], doc_dict['interval']))

    return render_template('dashboard.html', pending_tasks=pending_tasks)


if __name__ == "__main__":
    app.run()
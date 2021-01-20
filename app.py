from flask import Flask, render_template, request, session
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from messenger import receiver, publisher
import multiprocessing
from threading import Thread, Event
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = "my secret key"

socketio = SocketIO(app)

messageList = []
web_app = None
receiver_process = None
logged_in = ""
url = "amqp://guest:guest@localhost:5672"
exchange = "conversation"
thread: Thread = None
threads = []
web_apps = {}

# Function to be passed to the receiver class as its message handler.


def on_message_handler(ch: BlockingChannel, deliveryArgs: Basic.Deliver, properties: BasicProperties, body: bytes):
    message = body.decode()

    # It is assumed that every message will have a "sender" header associated with the sender's username.
    sender = properties.headers.get("sender")
    print(sender)
    print(f"EMMITING MESSAGE {logged_in}:{message}")
    message = f"{sender}: {message}"
    socketio.emit("newMessage", {"message": message})
    ch.basic_ack(
        delivery_tag=deliveryArgs.delivery_tag, multiple=True)


# webapp class
class webapp():
    _publisher: publisher = None
    _username = ""

    def setup(self, username):
        self._username = username
        self._publisher = publisher(url, exchange, username)

        def start():
            _receiver = receiver(url, exchange, username, on_message_handler)
        global thread
        if thread is None:
            thread = socketio.start_background_task(start)

    def publish_message(self, message):
        self._publisher.publish_message(message)


@app.route('/', methods=["GET"])
def index():
    return render_template("index.html", messages=messageList)


@app.route('/username', methods=["POST", "GET"])
def get_username():
    form_data = request.form
    username = form_data.getlist("username")[0]
    session['username'] = username
    print(session)
    web_app = webapp()
    web_app.setup(username)
    web_apps[session['username']] = web_app
    global logged_in
    logged_in = username
    print("LOGGED IN AS " + username)
    return render_template("index.html", hasUsername=1, username=username)


@socketio.on('MESSAGE')
def my_test(data):
    print(len(threads))
    print(data)
    try:
        web_apps.get(session['username']).publish_message(data)
    except:
        print("cant find that user!")


if __name__ == "__main__":
    web_app = webapp()
    socketio.run(app)

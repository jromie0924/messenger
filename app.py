from flask import Flask, render_template, request, session
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from messenger import receiver, publisher
from threading import Thread
from flask_socketio import SocketIO
import uuid

app = Flask(__name__)
app.secret_key = "my secret key"

socketio = SocketIO(app)

web_app = None
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
    message = f"{sender}: {message}"
    socketio.emit("newMessage", {"message": message})
    ch.basic_ack(
        delivery_tag=deliveryArgs.delivery_tag, multiple=True)


# webapp class
class webapp():
    _publisher: publisher = None

    def setup(self, username):
        self._publisher = publisher(url, exchange, username)

        def start():
            guid = str(uuid.uuid4())
            _receiver = receiver(url, exchange, guid, on_message_handler)
        global thread
        if thread is None:
            thread = socketio.start_background_task(start)

    def publish_message(self, message):
        self._publisher.publish_message(message)


# Website user entry point
@app.route('/', methods=["GET"])
def index():
    return render_template("index.html")


# Capture username and instantiate a webapp instance.
@app.route('/username', methods=["POST", "GET"])
def get_username():
    form_data = request.form
    username = form_data.getlist("username")[0]
    session['username'] = username
    web_app = webapp()
    web_app.setup(username)
    web_apps[session['username']] = web_app
    return render_template("index.html", hasUsername=1, username=username)


# Captures messages received from AMQP
@socketio.on('MESSAGE')
def my_test(data):
    try:
        web_apps.get(session['username']).publish_message(data)
    except:
        print("User cannot be found.")


if __name__ == "__main__":
    web_app = webapp()
    socketio.run(app)

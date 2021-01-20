from flask import Flask, render_template, request
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from messenger import receiver, publisher
import multiprocessing
from threading import Thread, Event
from flask_socketio import SocketIO, emit

app = Flask(__name__)

socketio = SocketIO(app, logger=True, engineio_logger=True)

messageList = []
web_app = None
receiver_process = None
logged_in = ""
url = "amqp://guest:guest@localhost:5672"
exchange = "conversation"
thread = Thread()

# Function to be passed to the receiver class as its message handler.


def on_message_handler(ch: BlockingChannel, deliveryArgs: Basic.Deliver, properties: BasicProperties, body: bytes):
    message = body.decode()

    # It is assumed that every message will have a "sender" header associated with the sender's username.
    sender = properties.headers.get("sender")
    global messageList
    print("EMMITING MESSAGE")
    socketio.emit("newMessage", {"message": message}, namespace="/incoming")
    print(messageList)
    ch.basic_ack(
        delivery_tag=deliveryArgs.delivery_tag, multiple=True)


# webapp class
class webapp():
    _publisher: publisher = None

    def setup(self, username):
        print(username)
        self._publisher = publisher(url, exchange, username)

    def publish_message(self, message):
        self._publisher.publish_message(message)


@app.route('/', methods=["GET"])
def index():
    return render_template("index.html", messages=messageList)


@app.route('/username', methods=["POST", "GET"])
def get_username():
    form_data = request.form
    username = form_data.getlist("username")[0]
    web_app.setup(username)
    global logged_in
    logged_in = username
    print("LOGGED IN AS " + username)
    return render_template("index.html", hasUsername=1, username=username)


@app.route("/message", methods=["GET", "POST"])
def send_message():
    form_data = request.form
    message = form_data.getlist("message")[0]
    print("SENDING MESSAGE: " + message)
    web_app.publish_message(message)
    return render_template("index.html", hasUsername=1, messages=messageList, )


@socketio.on("connect", namespace="/incoming")
def setup_receiver():
    def start():
        _receiver = receiver(url, exchange, logged_in, on_message_handler)
    global thread
    thread = socketio.start_background_task(start)


if __name__ == "__main__":
    web_app = webapp()
    app.run(debug=True)

import pika
import multiprocessing
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from pika.spec import Basic, BasicProperties
from flask import Flask


# Receiver class handles all listening configuration for the messaging app.
class receiver():
    _channel: BlockingChannel = None
    _connection: BlockingConnection = None
    _exchange = ""
    _queue = ""
    _on_message = None

    def __init__(self, url, exchange, username, messageHandler):
        self._connection = self.open_connection(url)
        self._on_message = messageHandler
        self._exchange = exchange
        self._queue = username
        self.setup_channel()
        self._channel.start_consuming()

    # Open connection with RabbitMQ
    def open_connection(self, url):
        return pika.BlockingConnection(pika.URLParameters(url))

    # Get channel from connection and declare and bind exchange and queue
    def setup_channel(self):
        self._channel = self._connection.channel()
        self._channel.exchange_declare(
            exchange=self._exchange, exchange_type="fanout")

        self._channel.queue_declare(queue=self._queue)

        self._channel.queue_bind(
            queue=self._queue, exchange=self._exchange, routing_key=self._queue)
        self._channel.basic_consume(
            queue=self._queue, on_message_callback=self._on_message)


# Publisher class handles publishing messages and listening for user input.
class publisher():
    _connection: BlockingConnection = None
    _channel: BlockingChannel = None
    _exchange = ""
    _routing_key = ""
    _username = ""

    def __init__(self, url, exchange, username):
        self._connection = self.open_connection(url)
        self._exchange = exchange
        self._routing_key = username
        self._username = username
        self._channel = self._connection.channel()
        print("PUBLISHER SETUP COMPLETE")
        # self.prompt_messages()

    # Open connection to RabbitMQ
    def open_connection(self, url):
        return pika.BlockingConnection(parameters=pika.URLParameters(url))

    # Enters intinite while-loop, prompting user for a message to send. Upon receiving a message, it calls publish_message
    def prompt_messages(self):
        while True:
            message = input()
            self.publish_message(message)

    # Publishes message, consumed from user in prompt_messages above
    def publish_message(self, message):
        # Message will contain a header of "sender": username so recipients can identify the origin.
        self._channel.basic_publish(self._exchange, routing_key="message", body=message,
                                    properties=pika.BasicProperties(headers={"sender": self._username}))


# Runner more or less bootstraps everrything together.
class runner():
    def __init__(self):
        url = "amqp://guest:guest@localhost:5672"
        exchange = "conversation"
        username = input("Enter username: ")
        print("\n--------------------\n")

        # Because telling a channel to listen on a queue is a blocking statement,
        # we need to put the receiver instance in a multiprocess so that it can allow the program to continue.
        # Otherwise, it would hang upon initialization of the receiver and we would never be able to publish messages.
        _receiver = multiprocessing.Process(
            target=receiver, args=(url, exchange, username))

        _receiver.start()
        _publisher = publisher(url, exchange, username)


if __name__ == "__main__":
    messenger = runner()

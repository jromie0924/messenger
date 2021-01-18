import multiprocessing
import pika
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from pika.spec import Basic, BasicProperties
import time
import sys


class receiver():
    _channel: BlockingChannel = None
    connection: BlockingConnection = None
    exchange = ""
    queue = ""

    def __init__(self, url, exchange, username):
        self.connection = self.open_connection(url)
        self.exchange = exchange
        self.queue = username
        self.setup_channel()
        try:
            self._channel.start_consuming()
        except KeyboardInterrupt:
            self.connection.close()

    def open_connection(self, url):
        return pika.BlockingConnection(parameters=pika.URLParameters(url))

    def setup_channel(self):
        self._channel = self.connection.channel()
        self._channel.exchange_declare(
            exchange=self.exchange, exchange_type="direct")
        self._channel.queue_declare(queue=self.queue)
        self._channel.queue_bind(
            queue=self.queue, exchange=self.exchange, routing_key=self.queue)

        self._channel.basic_consume(
            queue=self.queue, on_message_callback=self.on_message)

    def on_message(self, ch, deliveryArgs: Basic.Deliver, properties: BasicProperties, body: bytes):
        message = body.decode()
        sender = properties.headers.get("sender")
        print("FROM " + sender + " :: " + message + "\n")
        self._channel.basic_ack(delivery_tag=deliveryArgs.delivery_tag)


class publisher(object):
    _connection: BlockingConnection = None
    _channel: BlockingChannel = None
    _exchange = ""
    _routing_key = ""
    _username = ""

    def __init__(self, url, exchange, friend, username):
        self._connection = self.open_connection(url)
        self._exchange = exchange
        self._routing_key = friend
        self._username = username
        self._channel = self._connection.channel()
        self.prompt_messages()

    def open_connection(self, url):
        return pika.BlockingConnection(parameters=pika.URLParameters(url))

    def prompt_messages(self):
        while True:
            message = input("> ")
            self.publish_message(message)

    def publish_message(self, message):
        self._channel.basic_publish(self._exchange, routing_key=self._routing_key, body=message,
                                    properties=pika.BasicProperties(headers={"sender": self._username}))


def main():
    url = "amqp://guest:guest@localhost:5672"
    exchange = "conversation"
    username = input("Enter username: ")
    print("\n\n")
    friend = ""
    if username == "jackson":
        friend = "taumer"
    elif username == "taumer":
        friend = "jackson"

    _receiver = multiprocessing.Process(
        target=receiver, args=(url, exchange, username))
    _receiver.start()

    _publisher = publisher(url, exchange, friend, username)


if __name__ == "__main__":
    main()

import multiprocessing
import pika
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from pika.spec import Basic, BasicProperties


class receiver():
    _channel: BlockingChannel = None
    connection: BlockingConnection = None
    exchange = ""
    queue = ""

    def __init__(self, url, exchange, username):
        print("receiver init")
        self.connection = self.open_connection(url)
        self.exchange = exchange
        self.setup_channel()
        self.queue = username
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
        print("FROM " + sender + " :: " + message)
        self._channel.basic_ack(delivery_tag=deliveryArgs.delivery_tag)


class publisher(object):
    def __init__(self, url, exchange):
        print("publisher init")


def main():
    url = "amqp://guest:guest@localhost:5672"
    exchange = "conversation"
    username = input("Enter username\n")
    r = receiver(url, exchange)
    p = publisher(url, exchange)


if __name__ == "__main__":
    main()

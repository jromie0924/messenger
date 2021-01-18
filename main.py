import pika
# from pika.spec import BasicProperties

connection = None
channel = None
username = None


def establishConnection():
    global connection
    global channel
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("localhost"))
    channel = connection.channel()


def createSession():
    channel.exchange_declare("sessions", exchange_type="fanout")
    channel.queue_declare(queue=username + "_session")
    channel.queue_bind(queue=username + "_session", exchange="sessions")

    channel.basic_publish(exchange="sessions",
                          routing_key="newSession", body=username)

    channel.exchange_declare("conversation", exchange_type="direct")
    channel.queue_declare(queue=username)
    channel.queue_bind(
        queue=username, exchange="conversation", routing_key=username)


def listen():
    channel.basic_consume(queue=username + "_session",
                          on_message_callback=sessionCallback)
    channel.start_consuming()


def sessionCallback(ch, method, properties, body):
    body = body.decode()
    if body != username:
        print(" [x] %r has entered the chat" % body)
        channel.basic_ack(method.delivery_tag, multiple=True)


def chatCallback(ch, method, properties, body):
    print(body)


if __name__ == "__main__":
    print("Enter username")
    username = input()
    establishConnection()
    createSession()
    listen()

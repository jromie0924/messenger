import pika

username = ""


def establishConnection():
    global connection
    global channel
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("localhost"))
    channel = connection.channel()


def createSession():
    channel.exchange_declare("sessions", exchange_type="fanout")
    channel.queue_declare(queue="{username}_session")
    channel.queue_bind(queue="{username}_session", exchange="sessions")

    channel.exchange_declare("conversation", exchange_type="direct")
    channel.queue_declare(queue=username)
    channel.queue_bind(
        queue=username, exchange="conversation", routing_key=username)


if __name__ == "__main__":
    print("Enter username")
    username = input()
    establishConnection()
    createSession()

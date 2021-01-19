# Messenger
A primitive messaging application centered around RabbitMQ

## How it works
No pre-configuration is required on the RabbitMQ side - the application creates a single fanout exchange, and a queue for each user that joins, bound to the exchange. This, as a result, allows multiple users to converse in a group session.

Moreover, if a user has chatted before, and they disconnect from an ongoing conversation, messages sent in the time the user has been disconnected will remain in their corresponding queue in chronological order, thereby allowing them to see what has been talked about while they were gone.

## Setup
### Get RabbitMQ Set Up
```docker pull rabbitmq:3.8-rc-management```
```docker run -d --name <ANY NAME NOT USED IN ANOTHER CONTAINER> -p 5672:5672 -p 15672:15672 rabbitmq:3.8-rc-management```
In about 30-ish seconds, you should be able to login to RabbitMQ on the browser (credentials are U: guest, P: guest) on http://localhost:15672

Note that after you kill this process, you can simply restart the container by running:
```docker start <NAME PROVIDED IN RUN COMMAND>```

### Run the Python Code
Once you're able to open the RabbitMQ management webpage in a browser, change directories to the root of the code repository and activate the virtual environment:

Note that this app should be compatible with Python 3.6.8 and up.

Install pipenv if it's not already installed:
```pip3 install --user pipenv```
If pipenv does not show as an existing command, you can run ```python3 -m site --user-base```
For a Mac, add the resulting directory with an appended ```/bin``` to your $PATH.
On Windows, replace ```/site-packages``` with ```/scripts``` and add it to your PATH.
You can also skip the $PATH stuff and just run it like ```python3 -m pipenv```

Install required packages:
```pipenv install -r requirements.txt```

Run the app:
```pipenv run python messenger.py```

You'll be prompted for a username - enter whatever name you like. Then it'll hang. At this point you can send messages by simply typing and hitting enter.

You can open another session by running the app in another command window and providing a different username. The two instances should be communicating with each other.
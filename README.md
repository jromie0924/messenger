# Messenger
A primitive messaging application centered around RabbitMQ

## How it works (briefly)
No pre-configuration is required on the RabbitMQ side - the application creates a single fanout exchange, and a single queue. This flask app is configured to only have one instance of the queue listener; each message contains a header that contains the sender so that they can be identified.

This makes it possible for more than two users to converse in a session.

The application creates a publisher for each user, and stores it in a dictionary, keyed by the username. This way, each publisher instance will be assigned to its user, and publish messages on behalf of said user.

Because Flask refreshes the DOM upon each endpoint request, we needed to get crafty on how to display incoming messages on the fly. There is a JavaScript file that starts a socket connection with the flask application (using Flask-SocketIO - https://flask-socketio.readthedocs.io/en/latest/). The message handler function sends a message through a socket to that JavaScript script, and it subsequently updates the DOM on the fly. This way there's no inconsistency in how the messages are delivered.

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
If pipenv does not show as an existing command, you can run ```python3 -m site --user-base```. 
For a Mac, add the resulting directory with an appended ```/bin``` to your $PATH.
On Windows, replace ```/site-packages``` with ```/scripts``` and add it to your PATH.
You can also skip the $PATH stuff and just run it like ```python3 -m pipenv```

Change directories to the repository root: ```cd /path/to/repo```

Install required packages:
```pipenv install```

Run the app:
```pipenv run python messenger.py```

Open two browser windows side-by-side and browse to http://localhost:5000

You'll be presented with a login input field; on each field enter a different name - these can be anything you like. As a result of the first pressing submit, you'll see a new queue created in the AMQP management with a UUID name.

With both users "logged in," they can communicate with the current input. The "submit" button needs to be clicked with a mouse rather than with the "enter" or "return" key. You'll see the messages sent displayed, and originated user identified.

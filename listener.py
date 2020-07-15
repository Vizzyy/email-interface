import re
import time
import requests
from config import *
from imapclient import IMAPClient

server = IMAPClient(HOST)
server.login(USERNAME, PASSWORD)
server.select_folder('INBOX')
LIGHT_HOSTS = {
    "bedroom": LIGHT_BEDROOM,
    "inside": LIGHT_INSIDE,
    "outside": LIGHT_OUTSIDE
}


def read_incoming_message():
    try:
        with IMAPClient(host=HOST) as c:  # Open a new connection
            c.login(USERNAME, PASSWORD)
            c.select_folder("INBOX")
            messages = c.gmail_search(f"newer_than:1d")
            messages.reverse()  # Newest message should be 0 position
            if len(messages) > 0:  # If there are any messages
                for mail_id, data in c.fetch(messages[0], ['RFC822']).items():  # Get first message
                    rfc = data[b'RFC822'].decode("utf-8")  # RFC = headers + body
                    command_regex = r'((light|door) \w+ ?\w*)'
                    sender_regex = r'('+SENDER_REGEX+')'
                    if re.search(sender_regex, rfc):  # Is trigger from approved source?
                        print(rfc)
                        match = re.search(command_regex, rfc)  # Does body include valid command?
                        if not match:
                            print("No execution keyword found.")
                            return
                        print(f"message: {match.group(1)}")
                        execute_message(match.group(1))  # If valid, then execute
                    else:
                        print("Mail not sent from approved sender.")
            else:
                print("No messages returned from gmail query.")
    except Exception as e:
        print(e)


def execute_message(message):
    try:
        tokenized_message = message.strip().split(" ")
        request_url = ""
        print(f"tokenized_message: {tokenized_message}")
        if tokenized_message[0] == "light":
            print("Execute Lights")
            request_url = f"{LIGHT_HOSTS[tokenized_message[1]]}{tokenized_message[2]}"
        if tokenized_message[0] == "door":
            print("Execute Door")
            request_url = f"{DOOR_HOST}{tokenized_message[1]}{LOG_ENTRY}"
        print(request_url)
        r = requests.get(request_url, verify=False)  # Make REST call to local microservice
        print(r)
    except Exception as e:
        print(e)


server.idle()  # Start IDLE mode
print("Connection is now in IDLE mode.")
start_time = time.monotonic()  # Start timer

while True:
    try:
        responses = server.idle_check(timeout=TIMEOUT_SECONDS)  # Long poll for message
        if time.monotonic() - start_time > 13*60:  # Apparently 13min is sweet-spot for refreshing idle
            print("Resetting IMAP idle.")
            server.idle_done()
            server.idle()
            start_time = time.monotonic()
        if responses:
            if responses[0][1].decode("utf-8") == "EXISTS":  # Response-state = EXISTS == new email
                print(f"Server sent:{responses}")
                read_incoming_message()
    except Exception as e:
        print(e)



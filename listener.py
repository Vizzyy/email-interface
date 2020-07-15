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
    with IMAPClient(host=HOST) as c:
        c.login(USERNAME, PASSWORD)
        c.select_folder("INBOX")
        messages = c.gmail_search(f"from:{USERNAME} newer_than:1d")
        messages.reverse()
        if len(messages) > 0:
            for mail_id, data in c.fetch(messages[0], ['BODY[TEXT]']).items():
                body = data[b'BODY[TEXT]'].decode("utf-8")
                print(body)
                #regex = r'(<div dir="ltr">)(.+)(<br><\/div>)'
                regex = r'((light|door) \w+ \w*)'
                if re.search(regex, body):
                    match = re.search(regex, body)
                    print(match)
                    print(f"message: {match.group(1)}")
                    execute_message(match.group(1))
        else:
            print("No messages returned from gmail query.")


def execute_message(message):
    try:
        tokenized_message = message.strip().lower().split(" ")
        request_url = ""
        print(f"tokenized_message: {tokenized_message}")
        if tokenized_message[0] == "light":
            print("Execute Lights")
            request_url = f"{LIGHT_HOSTS[tokenized_message[1]]}{tokenized_message[2]}"
        if tokenized_message[0] == "door":
            print("Execute Door")
            request_url = f"{DOOR_HOST}{tokenized_message[1]}{LOG_ENTRY}"
        print(request_url)
        r = requests.get(request_url, verify=False)
        print(r)
    except Exception as e:
        print(e)


# Start IDLE mode
server.idle()
print("Connection is now in IDLE mode.")
start_time = time.monotonic()

while True:
    try:
        responses = server.idle_check(timeout=TIMEOUT_SECONDS)
        if time.monotonic() - start_time > 13*60:
            print("Resetting IMAP connection.")
            server.idle_done()
            server.idle()
            start_time = time.monotonic()
        if responses:
            if responses[0][1].decode("utf-8") == "EXISTS":
                print(f"Server sent:{responses}")
                read_incoming_message()
    except Exception as e:
        print(e)
        server.idle_done()
        print("\nIDLE mode done")
        server.logout()
        break



# Email Interface

* This service allows AppleWatch (or any other device with an email client) to interface with home RESTful infrastructure without having to install x509 certificate, navigate a web browser, or install any other form of client/app. 
* IMAPClient library allows idling of email folder so as to avoid constant polling requests eating up our IO or blocking cpu
* Authentication is via having the email account already synced and logged-in on the device. 
* Populating the "Default Replies" on the watch with all the possible derivations of commands allows for quick execution 
* This is much more of a backup to making direct 2way-SSL REST calls to the reverse-proxy or authenticating via browser to primary web-portal, as it requires exact text to be emailed originating from exact email address. This flow is clunky but works pretty effortlessly with Default Replies.


Config file format looks something like this: 
```
HOST = 'imap.gmail.com'
USERNAME = 'john.smith@gmail.com'
PASSWORD = 'someAppSpecificPW'
TIMEOUT_SECONDS = 30
DOOR_HOST = "http://somehost1/"
LIGHT_BEDROOM = "https://somehost2/"
LIGHT_INSIDE = "http://somehost3/"
LIGHT_OUTSIDE = "http://somehost4/"
LOG_ENTRY = "?entry=TOGGLED: OVERRIDE BY EMAIL"
SENDER_REGEX = "From: John Smith <john.smith@gmail.com>"
```


Script is enabled as a Systemd service:

```[Unit]
Description=Email Interface service for Apple Watch
After=network.target
StartLimitIntervalSec=0
[Service]
WorkingDirectory=/home/barney/email-interface
Type=simple
Restart=always
RestartSec=1
User=barney
ExecStart=/usr/bin/python3 -u /home/barney/email-interface/listener.py >> /home/barney/email-interface/log

[Install]
WantedBy=multi-user.target
```

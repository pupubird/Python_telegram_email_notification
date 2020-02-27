import email
import imaplib
import getpass
import json
import requests
import re
import os
from email.header import Header, decode_header, make_header


EMAIL = ""
PASSWORD = ""
SERVER = ""
MAX_DEPTH = 0
API_KEY = ""
CHAT_ID = ""
LAST_ID = 0
CHANNEL_NAME = ""


def login():
    update_config()
    print("Starting", SERVER, "server")
    mail = imaplib.IMAP4_SSL(SERVER)
    print("Logging in with", EMAIL)
    mail.login(EMAIL, PASSWORD)
    print("Logged in")
    mail.select('[Gmail]/Important')
    return mail


def main():
    mail = login()
    global EMAIL, PASSWORD, SERVER, MAX_DEPTH, LAST_ID, INTERVAL
    update_config()

    _, data = mail.search(None,'All')

    mail_ids = []

    for block in data:
        mail_ids += block.split()

    messages = [""]
    subject_arr = [""]
    for i in range(len(mail_ids), 1, -1):
        if abs(len(mail_ids) - i) >= MAX_DEPTH or i == LAST_ID or LAST_ID > len(mail_ids):
            break
        i = bytes(str(i), encoding='utf-8')

        _, data = mail.fetch(i, '(RFC822)')
        for response_part in data:

            if isinstance(response_part, tuple):
                message = email.message_from_bytes(response_part[1])
                mail_from = message['from']

                # validate if the mail is in blacklist
                if is_black_listed(mail_from):
                    continue

                mail_from = re.sub('<.*>', "", mail_from).replace("\"", "")
                mail_subject = message['subject']
                mail_subject = make_header(decode_header(mail_subject))

                # avoid duplicate subject
                if mail_subject in subject_arr:
                    continue

                subject_arr.append(mail_subject)

                email_from = f"📧 From: `{mail_from}`"
                subject = f"_Subject_:\n\t> \t\t*{mail_subject}*"
                content = f"{email_from}\n{subject}\n\n"

                for j in range(len(messages)):
                    if len(content) + len(messages[j]) < 4096:
                        messages[j] += content
                        break
                else:
                    print("Message too large, send in a new message")
                    messages.append(content)
                print("Appended", email_from)

    for message in messages:
        send_message(message)
    set_config(len(mail_ids))
    print("All latest emails notification sent.") if LAST_ID != len(
        mail_ids) else print("No new emails")
    return True

def is_black_listed(mail_from):
    with open("blacklist.txt",'r') as f:
        blacklists = f.readlines()
        for blacklist in blacklists:
            blacklist = blacklist.strip()
            if blacklist in mail_from:
                return True
    return False
def send_message(mail_contents):
    global API_KEY, CHAT_ID
    if not CHAT_ID:
        CHAT_ID = CHANNEL_NAME
    data = {
        "chat_id": CHAT_ID,
        "text": mail_contents,
        "parse_mode": "Markdown"
    }
    _ = requests.post(
        f'https://api.telegram.org/bot{API_KEY}/sendMessage?chat_id=@{CHANNEL_NAME}', data=data, json=data)


def update_config():
    global EMAIL, PASSWORD, SERVER, MAX_DEPTH, CHAT_ID, API_KEY, LAST_ID, CHANNEL_NAME
    try:
        with open('config.json', 'r') as f:
            strings = ""
            for line in f.readlines():
                strings += line
            json_payload = json.loads(strings)
            EMAIL = json_payload['EMAIL']
            PASSWORD = json_payload['PASSWORD']
            SERVER = json_payload['SERVER']
            CHANNEL_NAME = json_payload['CHANNEL_NAME']

            # Only apply when there is no last id
            if int(json_payload['LAST_ID']) == 0:
                MAX_DEPTH = json_payload['MAX_DEPTH']
            else:
                MAX_DEPTH = json_payload['MAX_DEPTH']*100000

            API_KEY = json_payload['API_KEY']
            LAST_ID = json_payload['LAST_ID']

            updates = requests.get(
                f'https://api.telegram.org/bot{API_KEY}/getUpdates')

            results = json.loads(updates.content)['result']
            for result in results:
                if result.get('channel_post', False):
                    CHAT_ID = result['channel_post']['chat']['id']
                    break
            

    except FileNotFoundError:
        with open('config.json', 'w') as f:
            json_payload = json.dumps({
                "API_KEY": input("API KEY: "),
                "EMAIL": input("Email: "),
                "PASSWORD": getpass.getpass("Password: "),
                "SERVER": "imap.gmail.com",
                "MAX_DEPTH": int(input("Maximum Depth of emails (Recommend 10): ")),
                "LAST_ID": 0,
                "CHANNEL_NAME": input("Input channel name (You may change the channel to private after the test message was sent): ")
            }, indent=2)
            f.write(json_payload)
        update_config()


def set_config(last_id):
    global EMAIL, PASSWORD, SERVER, MAX_DEPTH, API_KEY, CHAT_ID, CHANNEL_NAME
    with open('config.json', 'w') as f:
        json_payload = json.dumps({
            "API_KEY": API_KEY,
            "EMAIL": EMAIL,
            "PASSWORD": PASSWORD,
            "SERVER": SERVER,
            "MAX_DEPTH": int(MAX_DEPTH/100000),
            "CHAT_ID": CHAT_ID,
            "LAST_ID": last_id,
            "CHANNEL_NAME": CHANNEL_NAME
        }, indent=2)
        f.write(json_payload)

if __name__ == "__main__":
    main()
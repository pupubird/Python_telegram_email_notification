import email
import imaplib
import getpass
from email.header import Header, decode_header, make_header

EMAIL = input("Input email: ")
PASSWORD = getpass.getpass("Enter password: ")
SERVER = 'imap.gmail.com'
MAX_DEPTH = 10

mail = imaplib.IMAP4_SSL(SERVER)
mail.login(EMAIL, PASSWORD)
mail.select('[Gmail]/Important')

status, data = mail.search(None, 'ALL')

mail_ids = []

for block in data:
    mail_ids += block.split()

LAST_ID = None
try:
    with open('last_id.txt', 'r+') as f:
        try:
            LAST_ID = int(f.read())
        except ValueError:
            pass
except FileNotFoundError:
    with open('last_id.txt', 'w+') as f:
        f.write(str(len(mail_ids)))

for i in range(len(mail_ids), 1, -1):
    if abs(len(mail_ids) - i) >= MAX_DEPTH or i == LAST_ID:
        break
    i = bytes(str(i), encoding='utf-8')

    status, data = mail.fetch(i, '(RFC822)')
    for response_part in data:

        if isinstance(response_part, tuple):
            message = email.message_from_bytes(response_part[1])
            mail_from = message['from']
            mail_subject = message['subject']
            mail_subject = make_header(decode_header(mail_subject))
            if message.is_multipart():
                mail_content = ''
                for part in message.get_payload():
                    if part.get_content_type() == 'text/plain':
                        mail_content += part.get_payload()
            else:
                mail_content = message.get_payload()

            # Send message here
            print(f'From: {mail_from}, Subject: {mail_subject}')

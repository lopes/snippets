#!/usr/bin/env python3
import re
import logging


from imaplib import IMAP4_SSL
from email import message_from_bytes
from email.parser import HeaderParser
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime, localtime

from json import dumps
from os.path import abspath


'''
Connects to a mailbox using IMAP4 and parses all messages
in a given box.  The headers are translated into JSON for
further analysis.

All actions are logged and printed on screen and the final
JSON output is written in a file.

This script was based on:
https://github.com/lnxg33k/email-header-analyzer/

USAGE
To be written.
'''
__author__ = 'Joe Lopes'
__license__ = 'MIT'
__date__ = '2020-01-30'


def trim(s):
    'Removes special characters -\n\r\t...- and double spaces.'
    return ' '.join(s.split())


class Abuse(object):
    def __init__(self, url, user, password, workingbox):
        logging.info('Connecting to server')
        self.server = IMAP4_SSL(url)
        self.server.login(user, password)
        status,data = self.server.select(workingbox)
        if status != 'OK':
            raise SystemError(f'Could not access box {self.workingbox}')
        logging.info('Retrieving messages')
        self.uids = self.server.uid('SEARCH','ALL')[1][0].split()

    def parse(self):
        re_email_addr = re.compile(r'[a-zA-Z-0-9_\-\.]+@[a-zA-Z-0-9_\-\.]+')
        response = {
            'scan': localtime().isoformat(),
            'notifications': dict()
        }

        for uid in self.uids:
            status,data = self.server.uid('FETCH', uid, '(RFC822)')
            mail = message_from_bytes(data[0][1])
            notifier = re_email_addr.findall(trim(mail['from']))[0]

            if notifier not in response['notifications']:
                response['notifications'][notifier] = list()

            logging.info(f'Processing {notifier}')

            for part in mail.walk():
                if part.get_content_type() == 'message/rfc822':
                    payload = part.get_payload()[0]
                    response['notifications'][notifier].append(Spam(payload.as_bytes()).to_dict())

        return response

    def delete(self):
        logging.info('Deleting messages')
        self.server.uid('STORE', b','.join(self.uids).decode(), '+FLAGS', '(\\Deleted)')
        self.server.expunge()

    # def __del__(self):
    #     self.server.logout()


class Spam(object):
    def __init__(self, raw):
        try:
            self.headers = HeaderParser().parsestr(raw.decode())
        except UnicodeDecodeError:
            self.headers = HeaderParser().parsestr(raw.decode('iso-8859-1'))
        try: self.subject = self.format(self.headers.get('Subject'))
        except TypeError: self.subject = None
        try: self.from_ = self.format(self.headers.get('From'))
        except TypeError: self.from_ = None
        try: self.to = self.format(self.headers.get('To'))
        except TypeError: self.to = None
        try: self.cc = self.format(self.headers.get('cc'))
        except TypeError: self.cc = None
        try: self.msgid = self.format(self.headers.get('Message-ID'))
        except TypeError: self.msgid = None
        self.date = parsedate_to_datetime(trim(str(make_header(decode_header(self.headers.get('Date')))))).isoformat()
        self.hops = self.get_hops()
        self.oheaders = list()  # Other headers [{'':''}]

    def get_hops(self):
        re_from = re.compile(r'^from\s+(.*?)\s+by\s+')
        re_by = re.compile(r'by\s+(.*?)\s+(?:with|via|id)')
        re_with = re.compile(r'(?:with|via)\s+(.*?)\s+id')
        re_date = re.compile(r';\s+(.*)$')
        hops = list()

        try:
            for raw in [trim(h) for h in self.headers.get_all('Received') if 'from' in h or 'by' in h]:
                try: f = re_from.findall(raw)[0]
                except IndexError: f = None
                try: b = re_by.findall(raw)[0]
                except IndexError: b = None
                try: w = re_with.findall(raw)[0]
                except IndexError: w = None
                try: d = parsedate_to_datetime(re_date.findall(raw)[0]).isoformat()
                except (IndexError, TypeError): d = None
                hops.append({'from':f, 'by':b, 'with':w, 'date':d})
        except TypeError:
            pass

        return hops

    def to_dict(self):
        return {
            "subject": self.subject,
            "from": self.from_,
            "to": self.to,
            "cc": self. cc,
            "message-id": self.msgid,
            "date": self.date,
            "hops": self.hops,
            "other-headers": self.oheaders
        }

    def format(self, s):
        return trim(str(make_header(decode_header(s))))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s\tabused\t%(levelname)s\t%(message)s')

    abuse = Abuse('MAIL.DOMAIN', 'USERNAME', 'PASSWORD', 'INBOX/WORKBOX')
    parsed = abuse.parse()
    output = f'/tmp/abused-{parsed["scan"].replace(":",".")}.json'

    with open(output, 'w') as f:
        f.write(dumps(parsed, indent=4))

    abuse.delete()
    logging.info(f'Output recorded in {abspath(output)}')

# -*- coding: utf-8 -*-

import imaplib
import getpass
import email
import email.header
import threading
import sys
import smtplib
from validate_email import validate_email

import process

TEMPLATE = u"Привет, {}!\n\nМы уже получали письмо от вас. Мы работаем над вашим запросом. Если через 10 дней не будет положительного ответа, мы с вами свяжемся."

class Gmail(object):
    def __init__(self):
        email_addr = None
        while True:
            email_addr = raw_input("Please, enter your email address:")
            if not validate_email(email_addr):
                print "INVALID E-MAIL!"
                continue
            else:
                self.email_account = email_addr
                break

        self.conn = imaplib.IMAP4_SSL('imap.gmail.com')
        self.smtp = smtplib.SMTP('smtp.gmail.com:587')

        try:
            self._pwd = getpass.getpass()
            rv, data = self.conn.login(self.email_account, self._pwd)
        except imaplib.IMAP4.error:
            print "LOGIN FAILED!!! "
            sys.exit(1)

        self.address_book = {}
        self.seen_num = 1

        print rv, data

    def process_mail(self, letters, sending=False):
        letters_count = len(letters.split())
        print "\nProcessing address book:"
        for num in letters.split():
            rv, data = self.conn.fetch(num, '(RFC822)')

            if rv != 'OK':
                print "ERROR getting message", num
                continue

            msg = email.message_from_string(data[0][1])
            decode = email.header.decode_header(msg['From'])

            rv, data = self.conn.store(num, '+FLAGS', '\\Seen')

            fetch_funcs = [process.case_pair, process.case_single, process.case_fetch_str]

            for f in fetch_funcs:
                if f(decode):
                    mail, name = f(decode)
                    break

            if not mail:
                print "UNKNOWN GROUP SYNTAX:\n", decode
                break

            if mail not in self.address_book:
                self.address_book[mail] = name
            else:
                if sending and process.if_reply_available(mail):
                    self.send_mail(mail, name)

            self.seen_num = letters_count

    def get_init_emails(self):
        '''
        Initial method for getting all addresses and names from letters headers 
        from main directory
        '''
        self.conn.select()
        rv, messages = self.conn.search(None, 'ALL')
        if rv != 'OK':
            print "NO MESSAGES FOUND!"
            return

        self.process_mail(messages[0])

        return self.address_book

    def recent(self, repeat=False):
        self.conn.select()
        rv, messages = self.conn.search(None, '(UNSEEN)')
        if messages:
            self.process_mail(messages[0], sending=True)
            return self.address_book
        if repeat:
            threading.Timer(5.0, self.recent).start()

    def send_mail(self, recipient, user_name):
        if not user_name:
            user_name = 'dear user'

        FROM = self.email_account
        TO = recipient if type(recipient) is list else [recipient]
        SUBJECT = 'Subject'
        TEXT = TEMPLATE.format(user_name)

        # Prepare actual message
        msg = "\r\n".join(["From: {}".format(FROM),
                           "To: {}".format(TO),
                           "Subject: {}".format(SUBJECT),
                           "",
                           TEXT])

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(self.email_account, self._pwd)
            server.sendmail(FROM, TO, msg)
            server.close()
            print 'successfully sent the mail'
        except:
            print "failed to send mail"


my_gmail = Gmail()
print my_gmail.get_init_emails()
my_gmail.recent(repeat=True)

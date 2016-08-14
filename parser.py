# -*- coding: utf8 -*-
from os.path import join, expanduser, basename
from HTMLParser import HTMLParser
from datetime import datetime
from os import listdir
import locale as lc
import re


URL_RE = \
    r'((?:https?:\/\/)?(?:[\da-z\.-]+)\.(?:[a-z\.]{2,6})(?:[\/\w \.-]*)*\/?)'


class MessageParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.seq = []
        self.text = ''
        self._contact_filled = False
        self._time_filled = False
        self.time = None
        self.contact = None
    
    def handle_starttag(self, tag, attrs):
        self.seq.append(tag)
    
    def handle_endtag(self, tag):
        self.seq.pop()

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self.text += '\n'

    def handle_data(self, data):
        if not self._time_filled:
            try:
                self.time = datetime.strptime(data, '(%X)')
                self._time_filled = True
                return
            except ValueError:
                pass
        if not self._contact_filled and self.seq and self.seq[-1] == 'b':
            self.contact = data.strip().rstrip(':')
            return

        self.text += data

    def feed(self, data):
        HTMLParser.feed(self, data)
        self.text = self.text.strip()


class Message(object):
    def __init__(self, raw_line, date):
        """Message class.

        :param str raw_line: raw star with message data
        :param datetime date: date of chat session
        """
        parser = MessageParser()
        parser.feed(raw_line)
        self.contact = parser.contact
        if parser.time and date:
            self.time = date.replace(hour=parser.time.hour,
                                     minute=parser.time.minute,
                                     second=parser.time.second)
        elif parser.time:
            self.time = parser.time
        else:
            self.time = date
        self.text = parser.text

        match = re.search(URL_RE, self.text)
        self.links = match.groups() if match else tuple()


class ChatSession(object):
    def __init__(self, filename, contact=None):
        """Chat session class

        :param str filename: path to filename with session
        :param str contact: name of contact
        """

        self.messages = []
        self.start_dt = datetime.strptime(basename(filename)[:16],
                                          '%Y-%m-%d.%H%M%S')
        self.contact = contact

        with open(filename) as fd:
            for line in fd:
                if line.startswith('<html><head><meta'):
                    self.contact, self._start_dt = self._parse_head_line(line)
                elif re.match(r'<font color="#\w{6}">', line):
                    self.messages.append(Message(line, self.start_dt))

        self.messages.sort(key=lambda m: m.time)

    @staticmethod
    def _parse_head_line(line):
        match = re.search(
            r'<title>Conversation with (.+) at (.+?) on .+?</title>',
            line
        )
        return match.group(1), datetime.strptime(match.group(2), '%c')


class Parser(object):
    def __init__(self, contact_dir, locale=None):
        """Constructor for parser

        :param str contact_dir: like ~/.purple/logs/jabber/<jid>/
        :param tuple[str, str] locale: tuple with locale name and encoding,
        if None then local locale will be used
        """
        if locale is None:
            if lc.getlocale() == (None, None):
                lc.setlocale(lc.LC_ALL, lc.getdefaultlocale())
        self.sessions = []
        contact_dir = expanduser(contact_dir)
        contact = basename(contact_dir)
        for filename in listdir(contact_dir):
            if filename.endswith('.html'):
                self.sessions.append(
                    ChatSession(join(contact_dir, filename), contact)
                )

        self.sessions.sort(key=lambda x: x.start_dt)

    def iter_messages(self):
        """Return sorted iterator over all messages"""
        for session in self.sessions:
            for msg in session.messages:
                yield msg

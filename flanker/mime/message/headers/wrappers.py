""" Useful wrappers for headers with parameters,
provide some convenience access methods
"""
from __future__ import absolute_import

import regex as re
import flanker.addresslib.address

from email.utils import make_msgid

from flanker.str_analysis import sta


class WithParams(tuple):

    def __new__(self, value, params=None):
        return tuple.__new__(self, (value, params or {}))

    @property
    def value(self):
        return tuple.__getitem__(self, 0)

    @property
    def params(self):
        return tuple.__getitem__(self, 1)


class ContentType(tuple):

    def __new__(self, main, sub, params=None):
        return tuple.__new__(
            self, (main.lower() + '/' + sub.lower(), params or {}))

    def __init__(self, main, sub, params={}):
        self.main = main
        self.sub = sub

    @property
    def value(self):
        return tuple.__getitem__(self, 0)

    @property
    def params(self):
        return tuple.__getitem__(self, 1)

    @property
    def format_type(self):
        return tuple.__getitem__(self, 0).split('/')[0]

    @property
    def subtype(self):
        return tuple.__getitem__(self, 0).split('/')[1]

    def is_content_type(self):
        return True

    def is_boundary(self):
        return False

    def is_end(self):
        return False

    def is_singlepart(self):
        return self.main != 'multipart' and\
            self.main != 'message' and\
            not self.is_headers_container()

    def is_multipart(self):
        return self.main == 'multipart'

    def is_headers_container(self):
        return self.is_feedback_report() or \
            self.is_rfc_headers() or \
            self.is_message_external_body() or \
            self.is_disposition_notification()

    def is_rfc_headers(self):
        return self == 'text/rfc822-headers'

    def is_message_external_body(self):
        return self == 'message/external-body'

    def is_message_container(self):
        return self == 'message/rfc822' or self == 'message/news'

    def is_disposition_notification(self):
        return self == 'message/disposition-notification'

    def is_delivery_status(self):
        return self == 'message/delivery-status'

    def is_feedback_report(self):
        return self == 'message/feedback-report'

    def is_delivery_report(self):
        return self == 'multipart/report'

    def get_boundary(self):
        return self.params.get("boundary")

    def get_boundary_line(self, final=False):
        return "--{0}{1}".format(
            self.get_boundary(), "--" if final else "")

    def get_charset(self):
        default = 'ascii' if self.main == 'text' else None
        c = self.params.get("charset", default)
        if c:
            c = c.lower()
        return c

    def set_charset(self, value):
        self.params["charset"] = value.lower()

    def __str__(self):
        return "{0}/{1}".format(self.main, self.sub)

    def __eq__(self, other):
        if isinstance(other, ContentType):
            return self.main == other.main \
                and self.sub == other.sub \
                and self.params == other.params
        elif isinstance(other, tuple):
            return tuple.__eq__(self, other)
        elif isinstance(other, (unicode, str)):
            return str(self) == other
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "ContentType('{}', '{}', {!r})".format(self.main, self.sub,
                                                      self.params)


class MessageId(str):

    RE_ID = re.compile("<([^<>]+)>", re.I)
    MIN_LENGTH = 5
    MAX_LENGTH = 256

    def __new__(cls, *args, **kw):
        sta(args)  # {u'(uc/a)': 95}
        return str.__new__(cls, *args, **kw)

    def __clean(self):
        sta(self)  # {u'str/a': 164}
        return self.replace('"', '').replace("'", '')

    def __hash__(self):
        return hash(self.__clean())

    def __eq__(self, other):
        if isinstance(other, MessageId):
            return self.__clean() == other.__clean()
        else:
            return self.__clean() == str(other)

    @classmethod
    def from_string(cls, string):
        sta(string)  # {u'uc/a': 86}
        if not isinstance(string, (str, unicode)):
            return None
        for message_id in cls.scan(string):
            return message_id

    @classmethod
    def generate(cls, domain=None):
        sta(domain)
        message_id = make_msgid().strip("<>")
        if domain:
            local = message_id.split('@')[0]
            message_id = "{0}@{1}".format(local, domain)
        return cls(message_id)

    @classmethod
    def is_valid(cls, s):
        sta(s)  # {u'str/a': 1, u'uc/a': 6}
        return cls.MIN_LENGTH < len(s) < cls.MAX_LENGTH and \
            flanker.addresslib.address.is_email(s)

    @classmethod
    def scan(cls, string):
        sta(string)  # {u'uc/a': 140}
        for m in cls.RE_ID.finditer(string):
            message_id = m.group(1)
            if cls.is_valid(message_id):
                yield cls(message_id)


class Subject(unicode):
    RE_RE = re.compile("((RE|FW|FWD|HA)([[]\d])*:\s*)*", re.I)

    def __new__(cls, *args, **kw):
        sta(args)  # OK {u'(uc/a)': 1}
        return unicode.__new__(cls, *args, **kw)

    def strip_replies(self):
        sta(self)  # {u'uc/a': 1}
        return self.RE_RE.sub('', self)

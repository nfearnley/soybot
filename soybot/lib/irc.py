import socket
import re

NEWLINE = "\r\n"

MSG_RE = re.compile(r"""
    # Get the IRCv3 prefix
    # TODO: Parse tags properly
    (?:(?P<tags>@[+A-Za-z0-9.\-:/=;]+)\ +)?
    # Get the "nick!user@host" prefix
    (?:
        # nick
        :(?P<nick>[A-Za-z0-9.\-:_]+)
        # optional user@host
        (?:
            !(?P<user>[^ \x00\r\n]+)
            @(?P<host>[A-Za-z0-9.\-:/]+)
        )?
        \ +
    )?
    # Get command
    (?P<command>[A-Za-z0-9]+)
""", re.VERBOSE)
TRAILING_RE = re.compile(" +:([^\x00\r\n]*)")
PARAM_RE = re.compile(" +([^ \x00\r\n]*)")


class Message:
    def __init__(self, nick=None, user=None, host=None, command=None, params=None, tags=None, raw=None):
        self.command = command or ""
        self.nick = nick or ""
        self.user = user or ""
        self.host = host or ""
        self.params = params or []
        self.tags = tags or ""
        self.raw = raw or ""

    @property
    def content(self):
        if self.command != "PRIVMSG":
            return None
        return self.params[1]

    @classmethod
    def parse(cls, s):
        raw = s
        m = MSG_RE.match(s)
        tags = m.group("tags")
        nick = m.group("nick")
        user = m.group("user")
        host = m.group("host")
        command = m.group("command")
        s = s[m.end():]

        # Get params
        params = []
        while s:
            # Check if we've found the trailing param
            m = TRAILING_RE.match(s)
            # If so, add to the list of params and stop looking for new params
            if m:
                params.append(m.group(1))
                break

            # If not, check if we've found a regular param
            m = PARAM_RE.match(s)
            # If not, then we're done matching params
            if not m:
                break

            # If we've found a param, add it to the list and move forward in the string
            params.append(m.group(1))
            s = s[m.end():]

        # Create the message
        msg = Message(nick, user, host, command, params, tags, raw)
        return msg

    def __str__(self):
        if self.command == "PRIVMSG":
            return f"{self.nick}: {self.content}"
        return f"{self.raw}"


class IRC:
    def __init__(self, oauth, streamername, botname, displayname):
        self.oauth = oauth
        self.streamername = streamername
        self.botname = botname
        self.displayname = displayname
        self.socket = socket.socket()
        self.readbuffer = b""

    def connect(self):
        self.socket.connect(("irc.twitch.tv", 6667))
        self.send(f"PASS {self.oauth}")
        self.send(f"NICK {self.botname}")
        self.send(f"JOIN #{self.streamername}")

    def readmsg(self):
        while True:
            # Look for the next endline
            msgend = self.readbuffer.find(b"\r\n")
            # If endline is found, parse next message
            if msgend != -1:
                break
            # If endline is not found, read 1024 more bytes, and check again
            self.readbuffer = self.readbuffer + self.socket.recv(1024)

        # If there's an endline, then get the new message, and leave the rest of the data for later
        msgbytes = self.readbuffer[:msgend]
        self.readbuffer = self.readbuffer[msgend + 2:]

        # Parse the message string into a Message object and return it
        msgstr = str(msgbytes, "utf-8")
        msg = Message.parse(msgstr)
        return msg

    def sendmsg(self, message):
        try:
            self.send(f"PRIVMSG #{self.streamername} :{message}")
            print("***" + self.displayname + ": " + message)
        except:
            print("***" + self.displayname + ": <Couldn't send message.>")

    def pong(self):
        self.send("PONG")

    def send(self, s):
        self.socket.send(f"{s}\r\n".encode())

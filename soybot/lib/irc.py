import socket
import re

NEWLINE = "\r\n"

MSG_RE = re.compile(r"""
    # Get the "nick!user@host" prefix
    (?:
        # nick
        :(?P<nick>[A-Za-z0-9.-]+)
        # optional user@host
        (?:
            !(?P<user>[^ \x00\r\n]+)
            @(?P<host>[A-Za-z0-9.-]+)
        )?
        \ +
    )?
    # Get command
    (?P<command>[A-Za-z0-9]+)
""", re.VERBOSE)
TRAILING_RE = re.compile(" +:([^\x00\r\n]*)")
PARAM_RE = re.compile(" +([^ \x00\r\n])")


class Message:
    def __init__(self, command=None, nick=None, user=None, host=None, params=None):
        self.command = command or ""
        self.nick = nick or ""
        self.user = user or ""
        self.host = host or ""
        self.params = params or []

    def parse(cls, s):
        m = MSG_RE.match(s)
        nick = m.group("nick")
        user = m.group("user")
        host = m.group("host")
        command = m.group("command")
        s = s[m.endpos:]

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
            s = s[m.endpos:]

        # Create the message
        msg = Message(nick, user, host, command, params)
        return msg


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
        self.socket.send(("PASS " + self.oauth + NEWLINE).encode())
        self.socket.send(("NICK " + self.botname + NEWLINE).encode())
        self.socket.send(("JOIN #" + self.streamername + NEWLINE).encode())

    def readmsg(self):
        # Read the next 1024 bytes (or less)
        self.readbuffer = self.readbuffer + self.socket.recv(1024)
        # Look for the next endline
        msgend = self.readbuffer.find(b'\r\n')
        # If no endline, then we haven't found a new message yet
        if msgend == -1:
            return None

        # If there's an endline, then get the new message, and leave the rest of the data for later
        msgend += 2
        msgbytes = self.readbuffer[:msgend]
        self.readbuffer = self.readbuffer[msgend:]

        # Parse the message string into a Message object and return it
        msgstr = str(msgbytes, "utf-8")
        msg = Message.parse(msgstr)
        return msg

    def sendmsg(self, message):
        try:
            self.socket.send(("PRIVMSG #" + self.streamername + " :" + message + NEWLINE).encode())
            print("***" + self.displayname + ": " + message)
        except:
            print("***" + self.displayname + ": <Couldn't send message.>")

    def pong(self):
        self.socket.send(("PONG %s\r\n").encode())

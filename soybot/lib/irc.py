import socket

NEWLINE = "\r\n"


class IRC:
    def __init__(self, oauth, streamername, botname, displayname):
        self.oauth = oauth
        self.streamername = streamername
        self.botname = botname
        self.displayname = displayname
        self.socket = socket.socket()

    def connect(self):
        self.socket.connect(("irc.twitch.tv", 6667))
        self.socket.send(("PASS " + self.oauth + NEWLINE).encode())
        self.socket.send(("NICK " + self.botname + NEWLINE).encode())
        self.socket.send(("JOIN #" + self.streamername + NEWLINE).encode())

    def sendmsg(self, message):
        self.socket.send(("PRIVMSG #" + self.streamername + " :" + message + NEWLINE).encode())
        print("***" + self.displayname + ": " + message)

    def pong(self):
        self.socket.send("PONG %s\r\n")

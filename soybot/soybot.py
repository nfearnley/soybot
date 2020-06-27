#!/usr/bin/env python
# i have no idea what i'm doing here
# ripped a touch of this code from https://www.youtube.com/watch?v=5Kv3_V5wFgg

# command ideas:
# delete my last message because APPARENTLY NORMAL USERS CAN'T DO THAT LIKE ON MIXER AAAAAAAAAAAAAAAAA
# timed messages
# quote db?

import socket
import time
import re
import threading
# import asyncio

# Globals. Change this.
botnamepreferred = "Soybot"
botname = streamername = confirm = timedmsgconfirm = ""
s = socket.socket()


# eventually these will go to an external file but for now let's get it even working
timerlist = [
    "I don't know why you'd want to do this, but here's alleZSoyez's Twitter if you want to follow. https://twitter.com/alleZSoyez",
    "Stream archives and various cringe: https://www.youtube.com/channel/UCIYXXmcyfdyNgxF-oBMP3dw",
    "You can type !quote to show a random quote. Just beware of mature content.",
    "It's not expected or required, but if you'd like to support these streams... https://allezsoyez.streamjar.gg/tip"
]


#### sifts through the garbage to get the important bits of the messages
def getmsg(line):
    # only get the message
    msgsplitter = line.split(":")
    incomingmsg = msgsplitter[-1]

    # getting JUST the username is awful, just keep splitting...
    usrsplitter = msgsplitter
    incomingusr = usrsplitter[-2]
    incomingusr = incomingusr.split(" ")
    # may as well grab the command used in case we need it?
    incomingcmd = incomingusr[1]
    incomingusr = incomingusr[0].split("!")
    incomingusr = incomingusr[0]

    return incomingusr, incomingmsg, incomingcmd


#### make messages easy & print em to console
def sendmsg(message):
    global s
    global streamername
    global botnamepreferred
    s.send(("PRIVMSG #" + streamername + " :" + message + "\r\n").encode())
    print("***" + botnamepreferred + ": " + message)


################# TIMED COMMANDS #################
def timedmsg(timerlist):
    counter = 0

    while True:
        itemcount = len(timerlist)

        # 15 mins
        time.sleep(5)

        if counter < itemcount:
            sendmsg(timerlist[counter])
            counter = counter + 1
        else:
            counter = 0
################# END TIMED COMMANDS #################


def main():
    ################ STICK CREDS HERE #################
    print("Welcome to Soybot.\n")

    # grab auth key
    f = open("../soybot_oauth", "r")
    oauth = f.read()
    global botnamepreferred, botname, streamername, confirm, timedmsgconfirm, s

    # connect
    while confirm != "y":
        streamername = input("Whose chat are we connecting to? ").lower()
        botname = input("Bot account name: ").lower()
        timedmsgconfirm = input("Would you like to use timed messages this session? [Y/N] ").lower()
        confirm = input("Connect With these settings now? [Y/N] ").lower()

    #### login & start
    print(botnamepreferred + " is running. To quit, just close this window.\n")

    #### empty stuff bc we'll need em
    readbuffer = "".encode()
    incomingusr = incomingcmd = incomingmsg = ""

    #### connect to chat
    s.connect(("irc.twitch.tv", 6667))
    s.send(("PASS " + oauth + " \r\n").encode())
    s.send(("NICK " + botname + " \r\n").encode())
    s.send(("JOIN #" + streamername + " \r\n").encode())

    #### online
    sendmsg(botnamepreferred + " is online.")
    print("Listening.")

    while True:
        # i think this receives the message?? it's a mess so we gotta split it
        readbuffer = readbuffer + s.recv(1024)
        temp = str(readbuffer, 'utf-8').split("r\n")

        # split msg even more
        for line in temp:

            incomingusr = getmsg(line)[0]
            incomingmsg = getmsg(line)[1]
            incomingcmd = getmsg(line)[2]

            # FINALLY print incoming messages to console
            print(incomingusr + ": " + incomingmsg)

            # uhh i guess leaving the ping thing from stolen code could be useful??
            if (incomingcmd == "PING"):
                s.send("PONG %s\r\n")
            else:
                if (incomingcmd == "PRIVMSG"):

                    ################# ACTUAL BOT COMMANDS HERE #################

                    ######## DON'T F%#*ING PING ME (but bot should ignore itself lmao)
                    def noping():
                        if incomingusr.lower() != botname.lower():
                            if (streamername or "@" + streamername) in incomingmsg.lower():
                                sendmsg("Don't ping the streamer, @" + incomingusr + "!")

                    ######## COUNTDOWN (!countdown <int>)
                    def countdown():
                        countdownmatch = re.compile(r"^!countdown( \d+)?", re.IGNORECASE)

                        if (countdownmatch.match(incomingmsg)):
                            sendmsg("Countdown starting!")
                            time.sleep(2)
                            c = str(re.findall(r"\d+", incomingmsg))
                            c = c.replace("[", "")
                            c = c.replace("]", "")
                            c = c.replace("'", "")

                            if c != "":
                                counter = int(c)
                            else:
                                counter = 3

                            while counter > 0:
                                sendmsg(str(counter) + "!")
                                time.sleep(1.5)
                                counter = counter - 1
                            sendmsg("GO!")

                    ######## NO BACKSEAT GAMING! (!backseat OR !bsg)
                    def backseatgaming():
                        backseatmatch = re.compile("^!(backseat|bsg)", re.IGNORECASE)

                        if (backseatmatch.match(incomingmsg)):
                            sendmsg("NO BACKSEAT GAMING!")

                    ################# END MANUAL BOT COMMANDS #################

                    # multithreading?? i've gone mad!
                    threading.Thread(name='noping', target=noping, daemon=True).start()
                    threading.Thread(name='countdown', target=countdown, daemon=True).start()
                    threading.Thread(name='backseatgaming', target=backseatgaming, daemon=True).start()

                    if timedmsgconfirm == "y":
                        threading.Thread(name='timedmsg', target=timedmsg(timerlist), daemon=True).start()

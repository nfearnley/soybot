#!/usr/bin/env python
# i have no idea what i'm doing here
#
# ripped a touch of this code from:
# https://www.youtube.com/watch?v=5Kv3_V5wFgg
# https://hackernoon.com/threaded-asynchronous-magic-and-how-to-wield-it-bba9ed602c32

# command ideas / things to fix:
# delete my last message because APPARENTLY NORMAL USERS CAN'T DO THAT LIKE ON MIXER AAAAAAAAAAAAAAAAA
# timed messages need to be independent of listening for messages
# quote db because i'm tired of scorpbot
# it doesn't like : character in messages. fix it
# actually the incoming message handing in general is... y i k e s

import time
import re
import threading

from soybot.lib.irc import IRC

# Globals. Change this.
displayname = "Soybot"
botname = streamername = confirm = timedmsgconfirm = ""


# eventually these will go to an external file but for now let's get it even working
timerlist = [
    "I don't know why you'd want to do this, but here's alleZSoyez's Twitter if you want to follow. https://twitter.com/alleZSoyez",
    "Stream archives and various cringe: https://www.youtube.com/channel/UCIYXXmcyfdyNgxF-oBMP3dw",
    "You can type !quote to show a random quote. Just beware of mature content.",
    "It's not expected or required, but if you'd like to support these streams... https://allezsoyez.streamjar.gg/tip"
]

timedmsgcount = int(len(timerlist))
timedmsgcurrent = 0


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


################# TIMED COMMANDS #################
def timedmsg(irc, timerlist):
	if timedmsgconfirm == "y":
		#15 mins... eventually, for now it's testing with 10 seconds
		global timedmsgcurrent, timedmsgcount
		time.sleep(10)

		irc.sendmsg(timerlist[timedmsgcurrent])
		timedmsgcurrent = timedmsgcurrent + 1

		if timedmsgcurrent > timedmsgcount:
			timedmsgcurrent = 0
	else:
		print("Timed messages disabled this session.")
################# END TIMED COMMANDS #################


def main():
    print("Welcome to Soybot.\n")

    # grab auth key
    f = open("../soybot_oauth", "r")
    oauth = f.read()
    global displayname, botname, streamername, confirm, timedmsgconfirm, s

    # connect
    while confirm != "y":
        streamername = input("Whose chat are we connecting to? ").lower()
        if streamername == "":
            streamername = "allezsoyez"
        botname = input("Bot account name: ").lower()
        if botname == "":
            botname = "allezsoybot"
        timedmsgconfirm = input("Would you like to use timed messages this session? [Y/N] ").lower()
        if timedmsgconfirm == "":
            timedmsgconfirm = "n"
        confirm = input("Connect With these settings now? [Y/N] ").lower()

    #### login & start
    print(displayname + " is running. To quit, just close this window.\n")

    #### empty stuff bc we'll need em
    readbuffer = "".encode()
    incomingusr = incomingcmd = incomingmsg = ""

    #### connect to chat
    irc = IRC(oauth = oauth, streamername = streamername, botname = botname, displayname = displayname)
    irc.connect()

    #### online
    irc.sendmsg(displayname + " is online.")
    print("Listening.")

    while True:
        # i think this receives the message?? it's a mess so we gotta split it
        readbuffer = readbuffer + irc.socket.recv(1024)
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
                irc.pong()
            else:
                if (incomingcmd == "PRIVMSG"):

                    ################# ACTUAL BOT COMMANDS HERE #################

                    def cute():
                        cutematch = re.compile(r"^!cute", re.IGNORECASE)

                        if ( cutematch.match(incomingmsg) ):
                            irc.sendmsg("CS is really cute!")

                    ######## DON'T F%#*ING PING ME (but bot should ignore itself lmao)
                    def noping():
                        if incomingusr.lower() != botname.lower():
                            if (streamername or "@" + streamername) in incomingmsg.lower():
                                irc.sendmsg("Don't ping the streamer, @" + incomingusr + "!")

                    ######## COUNTDOWN (!countdown <int>)
                    def countdown():
                        countdownmatch = re.compile(r"^!countdown( \d+)?", re.IGNORECASE)

                        if (countdownmatch.match(incomingmsg)):
                            irc.sendmsg("Countdown starting!")
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
                                irc.sendmsg(str(counter) + "!")
                                time.sleep(1.5)
                                counter = counter - 1
                            irc.sendmsg("GO!")

                    ######## NO BACKSEAT GAMING! (!backseat OR !bsg)
                    def backseatgaming():
                        backseatmatch = re.compile("^!(backseat|bsg)", re.IGNORECASE)

                        if (backseatmatch.match(incomingmsg)):
                            irc.sendmsg("NO BACKSEAT GAMING!")

                    ################# END MANUAL BOT COMMANDS #################

                    # multithreading?? i've gone mad!
                    threading.Thread(name='cute', target=cute, daemon=True).start()
                    threading.Thread(name='noping', target=noping, daemon=True).start()
                    threading.Thread(name='countdown', target=countdown, daemon=True).start()
                    threading.Thread(name='backseatgaming', target=backseatgaming, daemon=True).start()

                    if timedmsgconfirm == "y":
                        threading.Thread(name='timedmsg', target=timedmsg(irc, timerlist), daemon=True).start()

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python
# i have no idea what i'm doing here
#
# ripped a touch of this code from:
# https://www.youtube.com/watch?v=5Kv3_V5wFgg
# https://hackernoon.com/threaded-asynchronous-magic-and-how-to-wield-it-bba9ed602c32

# thank you to DigiDuncan for helping with this even though i'm stubborn about things a lot <3

# command ideas / things to fix:
# delete my last message because APPARENTLY NORMAL USERS CAN'T DO THAT LIKE ON MIXER AAAAAAAAAAAAAAAAA
# timed messages need to be independent of listening for messages AND not hold up the entire program aaaaaaAAAAAAAA
# quote db because i'm tired of scorpbot
# maybe the bot shouldn't run noping when someone else is running a command (like quotes)
# actually the incoming message handing in general is... y i k e s
# "oh boy 3 am" command needs to ask for time zone on boot (default to system time zone)

import time
import re
import threading

from datetime import datetime
from soybot.lib.irc import IRC

# Globals. Change this.
displayname = "Soybot"
botname = streamername = confirm = timedmsgconfirm = ""
timedmsgcount = int(len(timerlist))
timedmsgcurrent = 0

# eventually these will go to an external file but for now let's get it even working
timerlist = [
    "I don't know why you'd want to do this, but here's alleZSoyez's Twitter if you'd like to follow them: https://twitter.com/alleZSoyez",
    "Stream archives and various cringe: https://www.youtube.com/channel/UCIYXXmcyfdyNgxF-oBMP3dw",
    "You can type !quote to show a random quote. Just beware of mature content.",
    "It's not expected or required, but if you'd like to support these streams... https://allezsoyez.streamjar.gg/tip"
]

################# TIMED COMMANDS #################
def timedmsg(irc, timerlist):
	if timedmsgconfirm == "y":
		#15 mins... eventually, for now it's testing with 2 seconds
		global timedmsgcurrent, timedmsgcount
		time.sleep(2)

		irc.sendmsg(timerlist[timedmsgcurrent])
		timedmsgcurrent = timedmsgcurrent + 1

		if timedmsgcurrent == timedmsgcount:
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
           
            #### sifts through the garbage to get the important bits of the messages

            # split msg
            splitmsg = line.split("\r\n")
            splitmsg = splitmsg[-2]
            splitmsg = splitmsg[1:]
            
            # we got the username!
            splitmsgu = splitmsg.split("!")
            incomingusr = splitmsgu[0]

            # we got the command
            splitmsgc = splitmsg.replace(incomingusr+"!"+incomingusr+"@"+incomingusr+".tmi.twitch.tv ","")
            splitmsgc = splitmsgc.split(" #"+streamername)
            incomingcmd = splitmsgc[0]

            if incomingcmd == "PRIVMSG":
                # we got the message!
                splitmsgm = splitmsg.split(incomingusr+"!"+incomingusr+"@"+incomingusr+".tmi.twitch.tv PRIVMSG #"+streamername+" :")
                incomingmsg = str(splitmsgm[1])
            else:
                incomingmsg = ""


            # print incoming msg to console
            print(incomingusr + ": " + incomingmsg)

            # uhh i guess leaving the ping thing from stolen code could be useful??
            if (incomingcmd == "PING"):
                irc.pong()
            else:
                if (incomingcmd == "PRIVMSG"):

                    ################# ACTUAL BOT COMMANDS HERE #################

                    ######## ehehehehehe
                    def cute():
                        cutematch = re.compile(r"^!cute", re.IGNORECASE)

                        if ( cutematch.match(incomingmsg) ):
                            irc.sendmsg("CS is really cute!")

                    ######## DON'T F%#*ING PING ME (but bot should ignore itself lmao)
                    def noping():
                        if incomingusr.lower() != botname.lower():
                            if (streamername or "@" + streamername) in incomingmsg.lower():
                                irc.sendmsg("Don't ping the streamer, @" + incomingusr + "!")

                    ######## OH BOY 3 AM! (triggers at 3 am)
                    def threeam(): 
                        t = datetime.now().strftime("%H:%M:%S")
                        if t == "03:00:00":
                            irc.sendmsg("OH BOY 3 AM!")

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
                    # why yes i do have these arranged in a certain order so it's aesthetically pleasing ok
                    threading.Thread(name='cute', target=cute, daemon=True).start()
                    threading.Thread(name='noping', target=noping, daemon=True).start()
                    threading.Thread(name='threeam', target=threeam, daemon=True).start()
                    threading.Thread(name='countdown', target=countdown, daemon=True).start()
                    threading.Thread(name='backseatgaming', target=backseatgaming, daemon=True).start()
        
        # timed message sender, but we do NOT want it tied to command listener
        # too bad it still holds up the entire script since it's not asynchronous yet AAAAAAAAAAAAAAAAAAAAAAA
        if timedmsgconfirm == "y":
            threading.Thread(name='timedmsg', target=timedmsg(irc, timerlist), daemon=True).start()

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python

import time
from time import sleep
from datetime import datetime, timezone
import pytz

# allow shell execution of scripts launched from this file
import subprocess

from enum import Enum # Used for custom command Types from Youtube

### ytchat.py stuff ###
from youtubechat import YoutubeLiveChat, get_live_chat_id_for_stream_now

livechat_id = get_live_chat_id_for_stream_now("oauth_creds")
chat_obj = YoutubeLiveChat("oauth_creds", [livechat_id])
#######################


# USER PLEASE CHANGE #
FEED_INTERVAL_SECONDS = 30 # Set this to amount of time before same user can 
                           #    feed again 0 for instant
FEED_INTERVAL_MINUTES = 0  # Set to 0 to turn off
FEED_INTERVAL_HOURS = 0    # Set to 0 to turn off
FEED_INTERVAL_DAYS = 0     # Set to 0 to turn off
FEED_INTERVAL_TOTAL_SECONDS = FEED_INTERVAL_SECONDS \
    + (FEED_INTERVAL_MINUTES * 60) \
    + (FEED_INTERVAL_HOURS * 60 * 60) \
    + (FEED_INTERVAL_DAYS * 60 * 60 * 24)

# This Dictionary is to be maintained of all users who have issued commands
#       This will need to be expanded to allow for different timings on 
#       different commands
# Key: UserName | Value: DateTimeObject representing time of last command
DAILY_USER_DICT = {}

native_dt = datetime.now() # Reset Time to Local.. Not sure if needed pls test

CURRENT_DATE_TIME = datetime.now(pytz.utc) # Get timezone/offset aware datetime


VALID_COMMANDS = ['!feed']
    


def checkDictionary(key):
    global DAILY_USER_DICT
    
    updateDateTime();
    print(f"checking dictionary for {key}")
    if key in DAILY_USER_DICT:
        # Check to see if they fed more than FEED_INTERVAL_MINUTES + FEED_INTERVAL_SECONDS ago
        timeUserLastFed = DAILY_USER_DICT.get(key)
        print(f"{key} at time {timeUserLastFed}")
        print(f"Current time is:")
        print(CURRENT_DATE_TIME)
        
        return True

        
    else:
        print(f"{key} not found in dictionary")
        return False

       


# scan for all commands return a list
# emptylist on no commands found
def parseChatForCommands(msgText):
    commandsList = []
    words = msgText.split() # Split text on spaces
    for word in words:
        word = word.lower() # support both cases of given command
        if (word in VALID_COMMANDS):
            commandsList.append(word)
        
    return commandsList


def checkWaitedEnough(key, msgTime):
    timeUserLastFed = DAILY_USER_DICT.get(key)
    # Check difference between the Current time and timeUserLastFed
    
    timediff = CURRENT_DATE_TIME - timeUserLastFed
    print(f"Difference in time in days: {timediff.days}")
    timeDiffHoursCalculated = timediff.seconds /  (60 * 60)
    print(f"Difference in time in hours: {timeDiffHoursCalculated}")
    timeDiffMinutesCalculated = timediff.seconds / 60
    print(f"Difference in time in  minutes: {timeDiffMinutesCalculated}")
    print(f"Difference in time in seconds: {timediff.seconds}")
    
    if (timediff.seconds >= FEED_INTERVAL_TOTAL_SECONDS):
        timeRemaining = 0
        return timeRemaining
    else:
        timeRemaining = FEED_INTERVAL_TOTAL_SECONDS - timediff.seconds
        return timeRemaining


def richCommand(command, msgAuthorName, chatid):
    responseMessage = "Thanks %s, I'm processing your %s command now!" % (msgAuthorName, command)
    chat_obj.send_message(responseMessage, chatid)
    executeCommand(command)
    
    
def executeCommand(command):
    if (command == '!feed'):
        print("successful !feed command... trying subprocess.call")
        subprocess.call("/home/pi/Desktop/BirdFeeder/PythonScripts/StartFeedLoop.sh", shell=True)



# msg in this case is a LiveChatMessage object defined in ytchat.py
def respond(msgs, chatid):
    for msg in msgs:
        msgTime = msg.published_at
        # Strip off TimeZone needed for comparison later
        #msgTimeNaive = timestamp_from_datetime(msgTime)
        msgAuthorName = msg.author.display_name
        msgText = msg.display_message
        print(f"NEW MESSAGE: {msgTime} | {msgAuthorName} | {msgText}")
        
        # Check for presence of command
        commandsList = parseChatForCommands(msgText)
        if (commandsList): # Check that list is not empty
            # Check for user in dictionary
            for command in commandsList:
                # Build a key based on Author's Name and Command Used
                key = msgAuthorName + command
                print(f"key: {key}")
                dictionaryFound = checkDictionary(key)
                if (dictionaryFound):
                    # Check if user has waited long enough to use this specific command
                    timeRemaining = checkWaitedEnough(key, msgTime)
                    if (timeRemaining == 0):
                        print(f"User: {msgAuthorName} has waited long enough for the {command} command")
                        # update dictionary with new time for this key (user + command)
                        DAILY_USER_DICT[key] = msgTime
                        richCommand(command, msgAuthorName, chatid)
                    else: # User has not waited long enough
                        print(f"User: {msgAuthorName} needs to wait {timeRemaining} more seconds before using the {command} command")
                        responseMessage = "Sorry %s, you must wait %d seconds before using the %s command again :)" % (msgAuthorName, timeRemaining, command)
                        chat_obj.send_message(responseMessage, chatid)
                         
                else: # User + Command not found in dictionary
                    DAILY_USER_DICT[key] = msgTime # Add entry for user
                    print("feeding now")
                    richCommand(command, msgAuthorName, chatid)
                
        else: # Do nothing, no command found
            print("no command found")
        
        print("PRINTING DICTIONARY")
        print(DAILY_USER_DICT)
        print("END DICTIONARY")
            
            
            
            
        #print(msg)
        #msg.delete()
        #chat_obj.send_message("RESPONSE!", chatid)


# May be useful for converting datetimes Not used currently
def datetime_from_timestamp(ts):
    return datetime.fromtimestamp(ts, pytz.utc).replace(tzinfo=None)

def timestamp_from_datetime(dt):
    return dt.replace(tzinfo=pytz.utc).timestamp()

def updateDateTime():
    global CURRENT_DATE_TIME
    CURRENT_DATE_TIME = datetime.now(pytz.utc)

try:
    chat_obj.start()
    chat_obj.subscribe_chat_message(respond)
    chat_obj.join()

finally:
    chat_obj.stop()

#NANOV3.py


import requests
import json
import time

# Current Time Items
from datetime import datetime, timezone
native_dt = datetime.now()

# XBEE Stuff Below
import serial
from serial import Serial
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#Set Serial to your USB serial device (XBEE)
ser = serial.Serial('/dev/ttyUSB0', 9600,timeout=.5)

# END XBEE setup

#GLOBAL OTHER VARIABLES
feedCost = .04              # IN USD    controls minimum donation required to dispense food
lastNANOBalance = 0         # IN NANO   Tracks NANO wallet Balance from last cycle request
lastBTCBalance = 0          # IN BTC    Tracks BTC wallet Balance from last cycle request

#GLOBAL WALLET VARIABLES
WalletAddress_NANO = "nano_36wcd1s3ekway8s5ays1fj9ewgtxyyot1dkr8wo6f3k5mnqnigj8uc698zji"
WalletAddress_BTC = "172MQBZyt2UGfCPRwUpKCH4cmB4sRrhywy"
########################
API_URL = "http://charmantadvisory.com:5000/apiblock/%s/%s"
BITCOIN_API_URL = 'https://api.coinmarketcap.com/v1/ticker/bitcoin/'
NANO_API_URL = 'https://api.coinmarketcap.com/v1/ticker/raiblocks/'

## GLOBAL DATE AND TIME VARIABLES ##
dateString = ""
timeString = ""
hourString = ""                
minuteString = ""
secondString = ""
lastFeedHour = 0  # Sets to hourString if we have fed this hour. If Hour and lastFeedHour don't match, dispense food!
#############################

#Session Requests
sessionConnection = requests.session()

# Gets time for the PST timezone    
def updateDateTime():
    #tz = pytz.timezone('America/Los_Angeles')
    #timePST = datetime.now(tz)
    global hourString
    global minuteString
    global secondString
    
    utc_dt = datetime.now(timezone.utc)
    timePST = utc_dt.astimezone()
    
    hourString = timePST.hour
    minuteString = timePST.minute
    secondString = timePST.second
    
    return timePST
    

# Generic Function Get Wallet Balance
def getWalletBalance(ticker, wallet_address):
    query_url = API_URL % (ticker, wallet_address)
    
    #r = requests.get(query_url) OLD method which does not keep session
    r = sessionConnection.get(query_url)
    # Check that Request was Successfull, if not print HTTPCode
    if r.status_code != 200:
        print("Error:", r.status_code)
        loop()
        
    # Update Date and Time using this Response
    updateDateTime()
    #printTime()
    response = None
    
    while response is None:
        try:
            response = r.json()
        except:
            pass
    return response

# Prints the Global Time Variables
def printTime():
    print("hour: ", hourString)
    print("minute: ", minuteString)
    print("second: ", secondString)

# Gets Latest Nano Price from Exchange
def get_latest_nano_price():
    response = requests.get(NANO_API_URL)
    response_json = response.json()
    # Convert the price to a floating point number
    return float(response_json[0]['price_usd'])

# Gets Latest BTC Price from Exchange
def get_latest_btc_price():
    response = requests.get(BITCOIN_API_URL)
    response_json = response.json()
    # Convert the price to a floating point number
    return float(response_json[0]['price_usd'])


# This Function Will Determine Whether or Not to Dispense Food
# It does this by fetching Wallet Balance, and Current Exchange Price
def checkNANO():
    global lastNANOBalance
    global feedCost
    
    priceNANO = get_latest_nano_price()                                 # Gets Latest Nano Price from Exchange
    currentNANOBalance = getWalletBalance("NANO", WalletAddress_NANO)   # Generic Function Get Wallet Balance
    walletBalanceChange = currentNANOBalance - lastNANOBalance          # Get Change in Balance Since Last Checked
    walletBalanceChangeUSD = walletBalanceChange * priceNANO            # Convert that Change to USD
    
    writeToFile("priceNANO: {}".format(priceNANO))
    writeToFile("currentNANOBalance: {}".format(currentNANOBalance))
    writeToFile("walletBalanceChange: {}".format(walletBalanceChange))
    writeToFile("walletBalanceChangeUSD: {}".format(walletBalanceChangeUSD))
    
    determineDispense(walletBalanceChangeUSD)

    lastNANOBalance = currentNANOBalance


# This Function Will Determine Whether or Not to Dispense Food
# It does this by fetching Wallet Balance, and Current Exchange Price
def checkBTC():
    global lastBTCBalance
    global feedCost
    
    priceBTC = get_latest_btc_price()                                 # Gets Latest BTC Price from Exchange
    currentBTCBalance = getWalletBalance("BTC", WalletAddress_BTC)   # Generic Function Get Wallet Balance
    walletBalanceChange = currentBTCBalance - lastBTCBalance          # Get Change in Balance Since Last Checked
    walletBalanceChangeUSD = walletBalanceChange * priceBTC           # Convert that Change to USD
    
    writeToFile("priceBTC: {}".format(priceBTC))
    writeToFile("currentBTCBalance: {}".format(currentBTCBalance))
    writeToFile("walletBalanceChange: {}".format(walletBalanceChange))
    writeToFile("walletBalanceChangeUSD: {}".format(walletBalanceChangeUSD))
        
    determineDispense(walletBalanceChangeUSD)

    lastBTCBalance = currentBTCBalance


# Checks Change in Wallet Balance to Determine if we Should Dispense
# Also Checks if we have fed this hour
def determineDispense(walletBalanceChangeUSD):
    global feedCost
    
    if walletBalanceChangeUSD > feedCost:                               # Received more than minimum feedCost?
        print("!!!!! Got more than feedCost, Dispensing food")
        writeToFile("!!!!! Received Money")
        dispenseFood()
        

def checkHourlyFeed():
    global lastFeedHour
    # Check to See if we have fed this hour
    #print("Hour String: ", hourString)
    if lastFeedHour != hourString:
        # Set range to current range of Times you wish to Auto Feed
        if hourString in range(5, 19):
            print("!!!!! We Have not Fed this hour, Dispensing food")
            writeToFile("Hourly Dispense")
            dispenseFood()
            lastFeedHour = hourString
    #else:
        #print("We Have Already Fed this hour")

# This function communicates with the birdhouse outside, sending signal to dispense food
def dispenseFood():
    #Write this time to File
    writeToFile("!!!!! Sending signal to dispense food")
    #SEND ANTENNA SIGNAL OUTSIDE
    ser.write(str.encode('a'))
    #print("sent:", str.encode('a'));
    
def writeToFile(transactionString):
    timePST = updateDateTime()           # Grab Date and Time
    
    f = open("TransactionLog.txt", "a")  # Open File
    f.write('\n')                    # New log line 
    f.write("|{}:{}:{}|".format(timePST.hour, timePST.minute, timePST.second))      
    f.write(transactionString)           
    f.close()

def niceWait(seconds):
    print("Waiting {} Seconds".format(seconds), end='', flush=True)
    timeLeft = seconds
    while timeLeft != 0:
        print(".", end='', flush=True)
        timeLeft = timeLeft - 1
        time.sleep(1)
    print("")

def loop():
    print("Checking NANO... ", end='', flush=True)
    checkNANO()
    print("DONE")
    
    niceWait(5)    #Delay between requests... not sure if helps against ERROR 429 
    
    print("Checking BTC... ", end='', flush=True)
    checkBTC()
    print("DONE")
    
    print("Checking Hourly Feed... ", end='', flush=True)
    checkHourlyFeed()
    print("DONE")
    
    #time.sleep(10)
    niceWait(5)

def main():
    global lastNANOBalance
    global lastBTCBalance
    #Initialize these Globals for Comparison Later
    lastNANOBalance = getWalletBalance("NANO", WalletAddress_NANO)
    print("NANO Balance ", lastNANOBalance)
    lastBTCBalance = getWalletBalance("BTC", WalletAddress_BTC)
    print("BTC Balance ", lastBTCBalance)
    
    # TESTING ANTENNA
    while (0):
        dispenseFood()
        time.sleep(5)
    
    # Enter Loop, Checking Balance and Change Every 3 Seconds
    while (1):
        loop()


if __name__ == '__main__':
    main()


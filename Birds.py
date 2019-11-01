#Adding new API stuff to BirdFeeder!
#Birds.py


import requests
from requests.adapters import HTTPAdapter           # For Transport Adapter
from requests.exceptions import ConnectionError     # For Transport Adapter
from requests.packages.urllib3.util.retry import Retry  # For Retry object with connect amount and backoff_factor for 429 Error
import json
import time
from datetime import datetime, timezone             # Current Time Items

native_dt = datetime.now()                          # Reset Time to Local

##### XBEE Stuff Below ################
#import serial
#from serial import Serial
#import RPi.GPIO as GPIO
#GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
#Set Serial to your USB serial device (XBEE)
#ser = serial.Serial('/dev/ttyUSB0', 9600,timeout=.5)
##### END XBEE setup ##################
#######################################
##### GLOBAL OTHER VARIABLES ##########
feedCost = .05              # IN USD    controls minimum donation required to dispense food
lastNANOBalance = 0         # IN NANO   Tracks NANO wallet Balance from last cycle request
lastBTCBalance = 0          # IN BTC    Tracks BTC wallet Balance from last cycle request
lastNANOPrice = 0           # IN USD    Tracks NANO price from exchange... updated daily
lastBTCPrice = 0            # IN USD    Tracks BTC price from exchange... updated daily
#######################################
##### GLOBAL WALLET VARIABLES #########
WalletAddress_NANO_Natrium = "nano_36wcd1s3ekway8s5ays1fj9ewgtxyyot1dkr8wo6f3k5mnqnigj8uc698zji"    #ANDROID NATRIUM ADDRESS
WalletAddress_BTC_BlockChain = "172MQBZyt2UGfCPRwUpKCH4cmB4sRrhywy"                                 # Bitcoin BlockChain Address
WalletAddress_BTC_Blockio = "3MPnLgazAEZVMH7jyHvuBtJ79UZmtzJRqW"                                    # Bitcoin Blockio Service Address
WalletAddress_NANO_Snapyio = "xrb_3x9azks1d118ap7wmq1kpnuc7mb5i6axiaqd9k6uyd9i6sqcuipr5p5wdpx6"     #Snapy Service Address
#######################################
##### Legacy API Addresses ############
API_URL = "http://charmantadvisory.com:5000/apiblock/%s/%s"                             
BITCOIN_API_URL = 'https://api.coinmarketcap.com/v1/ticker/bitcoin/'        # These are still used to track current market value            
NANO_API_URL = 'https://api.coinmarketcap.com/v1/ticker/raiblocks/'         # These are still used to track current market value 
#######################################
##### API KEYS SUPER PRIVATE ##########
APIKeySnapyIO = ""                  # API Key from Snapy.io to be read in from Keys.txt line#2 0 INDEXING
APIKeyBlockIO = ""                  # API Key from Block.io to be read in from Keys.txt line#4 0 INDEXING
#######################################
##### New SNAPY API info items ########
headersNANO = "" #{'x-api-key': APIKeySnapyIO}       # API Key from Snapy.io this is created in function readKeys
SnapyWalletURL = "https://snapy.io/api/v1/wallets"   # Use this to generate a Wallet Got Seed: '2bb7bb6a04354c22903f9c6bf6f11c0ed29b1b9a14fd52fda89d549532f07f5b'
SnapyAddressURL = "https://snapy.io/api/v1/address"  # Use this to generate addresses for that wallet
SnapySendURL = "https://snapy.io/api/v1/send"        # Use this to send to an address
SnapyBalanceURL = "http://snapy.io/api/v1/balance/"  # Use this to check balance of all wallets. Concatenate an exact address to return one balance
#######################################
##### New Block.io API info items #####
BlockBalanceURL = ""                                 # Created in actual function "getBitcoinBalance" because complex string
#######################################
##### GLOBAL DATE AND TIME VARIABLES ##
dateString = ""
timeString = ""
hourString = ""
minuteString = ""
secondString = ""
lastFeedHour = 0                # Sets to hourString if we have fed this hour. If Hour and lastFeedHour don't match, dispense food!
lastPriceCheckHourNANO = 0      # Sets to hourString if we have queried the API for the latest Crypto Price
lastPriceCheckHourBTC = 0       # tracks last time queried API for latest BTC Price, same as above for NANO
#######################################
##### Session Requests ################
sessionConnectionSnapyIO = requests.session()            # Used by requests to keep the session rather than a new one every request
sessionConnectionBlockIO = requests.session()            # Used by requests for BlockIO API
sessionConnectionCharmant = requests.session()           # Used by requests for Charmant and current Market Prices
retry = Retry(connect=3, backoff_factor=.5)              # Incrementally sleeps until request works
transportAdapterSnapyIO = HTTPAdapter(max_retries=retry)    
transportAdapterBlockIO = HTTPAdapter(max_retries=retry)    # Setup Max Retries for Session Object
transportAdapterCharmant = HTTPAdapter(max_retries=retry)
sessionConnectionSnapyIO.mount(SnapyBalanceURL, transportAdapterSnapyIO)
sessionConnectionBlockIO.mount('https://block.io/', transportAdapterBlockIO)    # Use Transport Adapter for all endpoints that start with this URL
sessionConnectionCharmant.mount('https://api.coinmarketcap.com', transportAdapterCharmant)
#######################################
#######################################
#######################################


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
    
def smartRequest(type, query_url):
    try:
        if type == "BTC":
            r = sessionConnectionBlockIO.get(query_url, timeout = 10)
        elif type is "NANO":
            r = sessionConnectionSnapyIO.get(query_url, headers = headersNANO, timeout = 10)
            
    except ConnectionError as ce:
        print(ce)
        return smartRequest(type, query_url)
    except requests.exceptions.Timeout as to:
        print(to)
        return smartRequest(type, query_url)
    except Exception as e:
        print(e)
        return smartRequest(type, query_url)
    # Check that request was Successful, if not print HTTPCode
    if r.status_code != 200:
        print("Error:", r.status_code)
        
    return r


# Specific Function Queries Snapy.io for the balance of the address in global variable
def getNanoBalance():
    # Use the below URL to querey for any specific address created through Snapy.io
    query_url = SnapyBalanceURL + WalletAddress_NANO_Snapyio

    r = smartRequest("NANO", query_url)
    
    response = r.json()
    #print("Printing Response: {}".format(response))

    originalBalance = float(response['balance'])
    balanceAdjusted = originalBalance / 1000000
    #print("Printing Balance: {}".format(balanceAdjusted))
    return balanceAdjusted
    
# Specific Function Queries Block.io for the balance of the address in global variable
def getBitcoinBalance():
    # Use the below URL to querey for any specific address EVEN EXTERNAL from blockio service (not created by Blockio)
    query_url = "https://block.io/api/v2/get_address_balance/?api_key=" + APIKeyBlockIO + "&addresses=" + WalletAddress_BTC_BlockChain

    r = smartRequest("BTC", query_url)
           
    response = r.json()
    #print("Printing Response: {}".format(response))
    
    originalBalance = float(response['data']['available_balance'])  #Extract Balance from JSON dictionary response
    #print("Printing Balance: {}".format(originalBalance))
    return originalBalance


# Prints the Global Time Variables
def printTime():
    print("hour: ", hourString)
    print("minute: ", minuteString)
    print("second: ", secondString)

# Gets Latest Nano Price from Exchange
def get_latest_nano_price():
    global lastPriceCheckHourNANO
    global lastNANOPrice

    if lastPriceCheckHourNANO != hourString:                                  # If we haven't checked price this hour, check!
        try:
            response = sessionConnectionCharmant.get(NANO_API_URL, timeout = 5)
        except ConnectionError as ce:
            print(ce)
            
        response_json = response.json()
        lastPriceCheckHourNANO = hourString                                   # Update last time we checked for price
        lastNANOPrice = float(response_json[0]['price_usd'])                  #Update Global value for price
        return lastNANOPrice
    else:
        return lastNANOPrice

# Gets Latest BTC Price from Exchange
def get_latest_btc_price():
    global lastPriceCheckHourBTC
    global lastBTCPrice

    if lastPriceCheckHourBTC != hourString:                                  # If we haven't checked price this hour, check!
        try:
            response = sessionConnectionCharmant.get(BITCOIN_API_URL, timeout = 5)
        except ConnectionError as ce:
            print(ce)
            
        response_json = response.json()
        lastPriceCheckHourBTC = hourString                                # Update last time we checked for price
        lastBTCPrice = float(response_json[0]['price_usd'])     #Update Global value for price
        return lastBTCPrice
    else:
        return lastBTCPrice

# This Function Will Determine Whether or Not to Dispense Food
# It does this by fetching Wallet Balance, and Current Exchange Price
def checkNANO():
    global lastNANOBalance
    
    priceNANO = get_latest_nano_price()                                 # Gets Latest Nano Price from Exchange
    currentNANOBalance = getNanoBalance()                               # Check Snapy for NANO balance
    walletBalanceChange = currentNANOBalance - lastNANOBalance          # Get Change in Balance Since Last Checked
    walletBalanceChangeUSD = walletBalanceChange * priceNANO            # Convert that Change to USD
    
    #print("priceNANO: ", priceNANO)
    #print("currentNANOBalance: ", currentNANOBalance)
    #print("walletBalanceChange: ", walletBalanceChange)
    #print("walletBalanceChangeUSD: ", walletBalanceChangeUSD)
    
    if (walletBalanceChangeUSD >= feedCost):
        dispenseFood()

    lastNANOBalance = currentNANOBalance


# This Function Will Determine Whether or Not to Dispense Food
# It does this by fetching Wallet Balance, and Current Exchange Price
def checkBTC():
    global lastBTCBalance
    
    priceBTC = get_latest_btc_price()                                 # Gets Latest BTC Price from Exchange
    currentBTCBalance = getBitcoinBalance()                           # Check Snapy for BTC balance
    walletBalanceChange = currentBTCBalance - lastBTCBalance          # Get Change in Balance Since Last Checked
    walletBalanceChangeUSD = walletBalanceChange * priceBTC           # Convert that Change to USD
    
    #print("priceBTC: ", priceBTC)
    #print("currentBTCBalance: ", currentBTCBalance)
    #print("walletBalanceChange: ", walletBalanceChange)
    #print("walletBalanceChangeUSD: ", walletBalanceChangeUSD)
    
    if (walletBalanceChangeUSD >= feedCost):
        dispenseFood()

    lastBTCBalance = currentBTCBalance
        
# Checks to see if lastFeedHour matches hourString
def checkHourlyFeed():
    global lastFeedHour
    # Check to See if we have fed this hour
    #print("Hour String: ", hourString)
    if lastFeedHour != hourString:
        # Set range to current range of Times you wish to Auto Feed
        if hourString in range(5, 19):
            printBetter("!!!!! We Have not Fed this hour, Dispensing food")
            writeToFile("Hourly Dispense")
            dispenseFood()
            lastFeedHour = hourString
        else:
            writeToFile("Not within Time Range")
            niceWait(60 * 60)
            checkHourlyFeed()
    #else:
        #print("We Have Already Fed this hour")

# This function communicates with the birdhouse outside, sending signal to dispense food
def dispenseFood():
    #Write this time to File
    writeToFile("!!!!! Sending signal to dispense food")
    #SEND ANTENNA SIGNAL OUTSIDE
    #ser.write(str.encode('a'))
    #print("sent:", str.encode('a'));
    
# Generic wrapper to print which prints messages nicely with timestamp
def printBetter(String):
    timePST = updateDateTime()
    print("|{}:{}:{}|{}".format(timePST.hour, timePST.minute, timePST.second, String), end='', flush=True)
    
# Generic wrapper to f.write which logs messages nicely with timestamp
def writeToFile(transactionString):
    timePST = updateDateTime()           # Grab Date and Time
    
    f = open("TransactionLog.txt", "a")  # Open File
    f.write('\n')                        # New log line 
    f.write("|{}:{}:{}|".format(timePST.hour, timePST.minute, timePST.second))      
    f.write(transactionString)           
    f.close()

# Function which uses time.sleep but prints out a '.' (period) every second to visualize waiting
def niceWait(seconds):
    timePST = updateDateTime()
    print("|{}:{}:{}|Waiting {} Seconds".format(timePST.hour, timePST.minute, timePST.second, seconds), end='', flush=True)
    timeLeft = seconds
    while timeLeft != 0:
        print(".", end='', flush=True)
        timeLeft = timeLeft - 1
        time.sleep(1)
    print("")

# Main loop which will runs the whole program
def loop():
    # Check to see if loop should even run during this time.
    timePST = updateDateTime()
    while hourString not in range(5, 19):
        printBetter("Not within Time Range")
        niceWait(60 * 60)
        timePST = updateDateTime()
        
    printBetter("Checking NANO... ")
    checkNANO()
    print("DONE")
    
    niceWait(1)    #Delay between requests... not sure if helps against ERROR 429 
    
    printBetter("Checking BTC... ")
    checkBTC()
    print("DONE")

    printBetter("Checking Hourly Feed... ")
    checkHourlyFeed()
    print("DONE")

    niceWait(1)
    
# This function reads API keys from the Keys.txt file in the same directory.
def readKeys():
    global APIKeyBlockIO
    global APIKeySnapyIO
    global headersNANO
    filepath = 'Keys.txt'
    with open(filepath) as fp:
        line = fp.readline()
        cnt = 1
        while line:
            print("Line {}: {}".format(cnt, line.strip()))
            line = fp.readline()
            if cnt == 1:
                APIKeySnapyIO = line.rstrip()
                print(APIKeySnapyIO)
                headersNANO = {'x-api-key': APIKeySnapyIO} 
            elif cnt == 3:
                APIKeyBlockIO = line.rstrip()
                print(APIKeyBlockIO)
            cnt += 1
            
    
def main():
    global lastNANOBalance
    global lastBTCBalance
    
    # Read in Keys from Keys.txt
    readKeys()
    #print("Read this value for BlockIO key: ", APIKeyBlockIO)
    #print("Read this value for SnapyIO key: ", APIKeySnapyIO)
    #Initialize these Globals for Comparison Later
    lastNANOBalance = getNanoBalance()
    #print("NANO Balance ", lastNANOBalance)
    lastBTCBalance = getBitcoinBalance()
    #print("BTC Balance ", lastBTCBalance)
    
    # TESTING ANTENNA
    while (0):
        dispenseFood()
        time.sleep(5)
    
    # Enter Loop, Checking Balance and Change Every 3 Seconds
    while (1):
        loop()


if __name__ == '__main__':
    main()



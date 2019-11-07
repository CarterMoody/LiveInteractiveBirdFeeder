#SnapyInterface.py
# This will allow you to interact with Snapy.io and create wallets, generate addresses, check balance, and send NANO from it.
import requests
from requests.adapters import HTTPAdapter           # For Transport Adapter
from requests.exceptions import ConnectionError     # For Transport Adapter
from requests.packages.urllib3.util.retry import Retry  # For Retry object with connect amount and backoff_factor for 429 Error
import json
import time
from datetime import datetime, timezone             # Current Time Items

native_dt = datetime.now()                          # Reset Time to Local
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
SnapyPass = ""                      # Password used with Snapy.io to create address and use it
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


def generateWallet():

    jsonParameter = {"password":"SnapyPass"}
    r = requests.post(SnapyWalletURL, headers = headersNANO, json = jsonParameter)

    if r.status_code != 200:
        print("Error:", r.status_code)
        
    response = r.json()
    
    print("Printing Response: ")
    print(response)
    
def generateAddress():
    
    jsonParameter = {"password":"SnapyPass"}
    r = requests.post(SnapyAddressURL, headers = headersNANO)
    
    if r.status_code != 200:
        print("Error:", r.status_code)
        
    response = r.json()
    
    print("Printing Response: ")
    print(response)
    
def sendNano():
    
    # Remember that amount is actually 1 million times NANO amount (1 xrb raiblock = 1,000,000 Nano)
    amountToSendNANO = 10
    amountToSendNANO = amountToSendNANO * 1000000
    jsonParameter = {
                    "to":"nano_36wcd1s3ekway8s5ays1fj9ewgtxyyot1dkr8wo6f3k5mnqnigj8uc698zji",
                     "from":"xrb_3x9azks1d118ap7wmq1kpnuc7mb5i6axiaqd9k6uyd9i6sqcuipr5p5wdpx6",
                     "amount":"1",
                     "password":SnapyPass
                    }
                    
    r = requests.post(SnapySendURL, headers = headersNANO, json = jsonParameter)
    
    if r.status_code != 200:
        print("Error:", r.status_code)
        
    response = r.json()
    
    print("Printing Response: ")
    print(response)
    
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
        return smartRequest(type, query_url)
        
    return r
      
        
# Generic Function Get Wallet Balance
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
    
    


# Gets Latest Nano Price from Exchange
def get_latest_nano_price():
    # If haven't checked today:
    if (1):
        response = requests.get(NANO_API_URL)
        response_json = response.json()
        #Convert the price to a floating point number
        return float(response_json[0]['price_usd'])
    #If already Checked today
    return


# This Function Will Determine Whether or Not to Dispense Food
# It does this by fetching Wallet Balance, and Current Exchange Price
def checkNANO():
    global lastNANOBalance
    
    priceNANO = get_latest_nano_price()                                 # Gets Latest Nano Price from Exchange
    currentNANOBalance = getNanoBalance()                                 # Check Snapy for NANO balance
    walletBalanceChange = currentNANOBalance - lastNANOBalance          # Get Change in Balance Since Last Checked
    walletBalanceChangeUSD = walletBalanceChange * priceNANO            # Convert that Change to USD
    
    print("priceNANO: ", priceNANO)
    print("currentNANOBalance: ", currentNANOBalance)
    print("walletBalanceChange: ", walletBalanceChange)
    print("walletBalanceChangeUSD: ", walletBalanceChangeUSD)
    
    if (walletBalanceChangeUSD >= feedCost):
        feedOnce()

    lastNANOBalance = currentNANOBalance
    
# This function reads API keys from the Keys.txt file in the same directory.
def readKeys():
    global APIKeyBlockIO
    global APIKeySnapyIO
    global headersNANO
    global SnapyPass
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
            elif cnt == 5:
                SnapyPass = line.rstrip()
                print(SnapyPass)
                
            cnt += 1
             
    

def feedOnce():
    print("Sending Singal to Feed")

def main():
    global lastNANOBalance
    
    readKeys()

    #Initialize these Globals for Comparison Later
    lastNANOBalance = getNanoBalance()
    print("NANO Balance ", lastNANOBalance)
    

    #Admin Controls
    sendNano()    
    #generateWallet()
    #generateAddress()
    
    # Enter Loop check user input and generate wallets or something
    while (1):

        #getNanoBalance()
        checkNANO()
        time.sleep(3)

        


if __name__ == '__main__':
    main()

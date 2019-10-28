#SnapyInterface.py
# This will allow you to interact with Snapy.io and create wallets, generate addresses, check balance, and send NANO from it.
import requests
import json
import time


#GLOBAL OTHER VARIABLES
feedCost = .05              # IN USD    controls minimum donation required to dispense food
lastNANOBalance = 0         # IN NANO   Tracks NANO wallet Balance from last cycle request
lastBTCBalance = 0          # IN BTC    Tracks BTC wallet Balance from last cycle request
lastNANOPrice = 0           # IN USD    Tracks NANO price from exchange... updated daily
sessionConnection = requests.session()
#GLOBAL WALLET VARIABLES
WalletAddress_NANO_Natrium = "nano_36wcd1s3ekway8s5ays1fj9ewgtxyyot1dkr8wo6f3k5mnqnigj8uc698zji" #ANDROID NATRIUM ADDRESS
WalletAddress_BTC_BlockChain = "172MQBZyt2UGfCPRwUpKCH4cmB4sRrhywy"                                 # Bitcoin BlockChain Address
WalletAddress_BTC_Blockio = "3MPnLgazAEZVMH7jyHvuBtJ79UZmtzJRqW"                                    # Bitcoin Blockio Service Address
WalletAddress_NANO_Snapyio = "xrb_3x9azks1d118ap7wmq1kpnuc7mb5i6axiaqd9k6uyd9i6sqcuipr5p5wdpx6"       #Snapy Service Address
########################    

# Legacy API Addresses
API_URL = "http://charmantadvisory.com:5000/apiblock/%s/%s"                             
BITCOIN_API_URL = 'https://api.coinmarketcap.com/v1/ticker/bitcoin/'                    
NANO_API_URL = 'https://api.coinmarketcap.com/v1/ticker/raiblocks/'
#########

# New SNAPY API info items
headersNANO = {'x-api-key': 'YOUR SNAPY API KEY HERE'}
SnapyWalletURL = "https://snapy.io/api/v1/wallets" # Use this to generate a Wallet
                ##### Got Seed: 'YOUR SNAPY SEED HERE'
SnapyAddressURL = "https://snapy.io/api/v1/address" # Use this to generate addresses for that wallet
SnapySendURL = "https://snapy.io/api/v1/send"       # Use this to send to an address
SnapyBalanceURL = "http://snapy.io/api/v1/balance"

# New Block.io API info items
headersBTC = ""
api_key_BTC = ""



def generateWallet():
    global SnapyWalletURL
    global headers
    
    jsonParameter = {"password":"PASSWORD FOR YOUR WALLET MAKE IT LONG AND SECURE"}
    r = requests.post(SnapyWalletURL, headers = headersNANO, json = jsonParameter)

    if r.status_code != 200:
        print("Error:", r.status_code)
        
    response = r.json()
    
    print("Printing Response: ")
    print(response)
    
def generateAddress():
    global headers
    global SnapyAddressURL
    
    jsonParameter = {"password":"PASSWORD FOR YOUR WALLET MAKE IT LONG AND SECURE"}
    r = requests.post(SnapyAddressURL, headers = headersNANO)
    
    if r.status_code != 200:
        print("Error:", r.status_code)
        
    response = r.json()
    
    print("Printing Response: ")
    print(response)
    
def sendNano():
    global headers
    
    # Remember that amount is actually 1 million times NANO amount (1 xrb raiblock = 1,000,000 Nano)
    jsonParameter = {
                    "to":"nano_36wcd1s3ekway8s5ays1fj9ewgtxyyot1dkr8wo6f3k5mnqnigj8uc698zji",
                     "from":"xrb_3x9azks1d118ap7wmq1kpnuc7mb5i6axiaqd9k6uyd9i6sqcuipr5p5wdpx6",
                     "amount":"1",
                     "password":"SAME PASSWORD YOU USED TO CREATE THIS SPECIFIC WALLET"
                    }
                    
    r = requests.post(SnapySendURL, headers = headersNANO, json = jsonParameter)
    
    if r.status_code != 200:
        print("Error:", r.status_code)
        
    response = r.json()
    
    print("Printing Response: ")
    print(response)
    
        
        
# Generic Function Get Wallet Balance
def getNanoBalance():
    global sessionConnection
    global headers
    global SnapyBalanceURL
    
    
    # Use the below URL to querey for any specific address created through Snapy.io
    query_url = "http://snapy.io/api/v1/balance/" + WalletAddress_NANO_Snapyio
      
    #r = requests.get(query_url)
    jsonParameter = {'detailed':'true'}
    #r = sessionConnection.get(query_url, headers = headers, json = jsonParameter)
    r = sessionConnection.get(query_url, headers = headersNANO)
    # Check that Request was Succesfull, if not print HTTPCode
    if r.status_code != 200:
        print("Error:", r.status_code)
        
    response = r.json()
    #print("Printing Response: ")
    #print(response)
    originalBalance = float(response['balance'])
    balanceAdjusted = originalBalance / 1000000
    #print(balanceAdjusted)
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
    global feedCost
    
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
    
    
    

def feedOnce():
    print("Sending Singal to Feed")

def main():
    global lastNANOBalance

    #Initialize these Globals for Comparison Later
    lastNANOBalance = getNanoBalance()
    print("NANO Balance ", lastNANOBalance)
    

    #Admin Controls
    #sendNano()    
    #generateWallet()
    #generateAddress()
    
    # Enter Loop check user input and generate wallets or something
    while (1):

        #getNanoBalance()
        checkNANO()
        time.sleep(3)

        


if __name__ == '__main__':
    main()

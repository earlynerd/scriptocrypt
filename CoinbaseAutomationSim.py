import requests
import time

funding = 1000.0
initialFunding = 1000.0


uri = 'https://api.coinbase.com/v2/assets/prices?base=USD&filter=holdable&resolution=latest'

class crypto:
    def __init__(self, _name, currency_base_id):
        self.name = _name
        self.base_id = currency_base_id
        self.latest = 0.0
        self.balance = 0.0
        self.value = 0.0
        self.cost = 0.0

cryptoList = list()
    
def updateFromCoinbase(cryptos, doBuy):
    global funding
    try:
        response = requests.get(uri).json()
    except:
        return
    for key in response['data']:
      #print(key['base'], key['base_id'], key['prices']['latest'])
      found = False
      for i in range(len(cryptos)):
          if cryptos[i].base_id == key['base_id']:
              found = True
              cryptos[i].latest = float(key['prices']['latest'])
              cryptos[i].value = cryptos[i].latest * cryptos[i].balance
              if(cryptos[i].value >= cryptos[i].cost * 1.25):
                 funding += cryptos[i].value
                 cryptos[i].value = 0.0
                 cryptos[i].cost = 0.0
                 cryptos[i].balance = 0.0
      if(found == False):
          newCrypto = crypto(key['base'], key['base_id'])
          newCrypto.latest = float(key['prices']['latest'])
          if(doBuy):
              if(funding > 0.0):  
                  newCrypto.balance += funding / newCrypto.latest
                  funding = 0.0
                  newCrypto.value = newCrypto.balance * newCrypto.latest
                  newCrypto.cost = newCrypto.value
          if(doBuy):
              print("new crypto found", newCrypto.name, newCrypto.base_id, newCrypto.latest)
              print("purchase made.",newCrypto.name, "$", funding, "balance:", newCrypto.balance)
          cryptos.append(newCrypto)

def calculateProfit(crypt):
    global funding
    global initialFunding
    sum = 0
    for i in range(len(crypt)):
        if(crypt[i].balance > 0):
            print(crypt[i].name, "bal", crypt[i].balance, "value:", crypt[i].value)
            sum += crypt[i].value - crypt[i].cost
    if(funding > 0):
        sum += funding - initialFunding
    return sum
        
updateFromCoinbase(cryptoList, False)
#del cryptoList[-1]          #test to find a "new" crypto and buy it
while(True):
    updateFromCoinbase(cryptoList, True)
    print("funds:", funding, " overall profit:", calculateProfit(cryptoList))
    time.sleep(0.5)
    
      

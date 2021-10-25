import requests
import time
import pickle

funding = 1000.0
initialFunding = 1000.0

logFileName = 'logfile.txt'
databaseFilename = 'cryptoPickle'
balanceFile = 'balancePickle'


uri = 'https://api.coinbase.com/v2/assets/prices?base=USD&filter=holdable&resolution=latest'

class crypto:
    def __init__(self, _name, currency_base_id):
        self.name = _name
        self.base_id = currency_base_id
        self.latest = 0.0
        self.balance = 0.0
        self.value = 0.0
        self.cost = 0.0
        self.timestamp = time.time()

cryptoList = list()

def writeLogFile(file_name, text_to_append):
    """Append given text as a new line at the end of file"""
    # Open the file in append & read mode ('a+')
    with open(file_name, "a+") as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        # write formatted timestamp
        
        # Append text at the end of file
        file_object.write(time.strftime('{%Y-%m-%d %H:%M:%S}') + text_to_append)

    
def updateFromCoinbase(cryptos, doBuy):
    global funding
    global logFileName
    try:
        response = requests.get(uri).json()
    except:
        writeLogFile(logFileName, "JSON response parse error")
        return
    for key in response['data']:
      #print(key['base'], key['base_id'], key['prices']['latest'])
      found = False
      for i in range(len(cryptos)):
          if cryptos[i].base_id == key['base_id']:
              found = True
              cryptos[i].latest = float(key['prices']['latest'])
              cryptos[i].value = cryptos[i].latest * cryptos[i].balance
              cryptos[i].timestamp = time.time()
              if((cryptos[i].value >= cryptos[i].cost * 1.25) and (cryptos[i].balance >0)):
                 funding += cryptos[i].value
                 cryptos[i].value = 0.0
                 cryptos[i].cost = 0.0
                 cryptos[i].balance = 0.0
                 writeLogFile(logFileName, str(cryptos[i].name) + "sold! new funding balance:" + str(funding))
      if(found == False):
          newCrypto = crypto(key['base'], key['base_id'])
          newCrypto.latest = float(key['prices']['latest'])
          newCrypto.timestamp = time.time()
          if(doBuy):
              if(time.time() - cryptos[0].timestamp < 600):
                  if(funding > 0.0):  
                      newCrypto.balance += funding / newCrypto.latest
                      funding = 0.0
                      newCrypto.value = newCrypto.balance * newCrypto.latest
                      newCrypto.cost = newCrypto.value
                      print("new crypto found", newCrypto.name, newCrypto.base_id, newCrypto.latest)
                      writeLogFile(logFileName, "new crypto found" + str(newCrypto.name) + str(newCrypto.base_id) + str(newCrypto.latest))
                      print("purchase made.",newCrypto.name, "$", funding, "balance:", newCrypto.balance)
                      writeLogFile(logFileName, "purchase made." + str(newCrypto.name) + "$" + str(funding) + "balance:" + str(newCrypto.balance))
          cryptos.append(newCrypto)
          
def pickleLog(crypt):
    global databaseFilename
    global funding
    global balanceFile
    outfile = open(databaseFilename,'wb')
    pickle.dump(crypt, outfile)
    outfile.close()
    
    bal = open(balanceFile,'wb')
    pickle.dump(funding, bal)
    bal.close()

def restorePickle():
    global cryptoList
    global databaseFilename
    global funding
    global logFileName
    try:
        bal = open(balanceFile,'rb')
        outfile = open(databaseFilename,'rb')
        cryptoList = pickle.load(outfile)
        funding = pickle.load(bal)
        outfile.close()
        bal.close()
        writeLogFile(logFileName, "Script started. Restored data from pickle.")
    except:
        updateFromCoinbase(cryptoList, False)
        writeLogFile(logFileName, "Script started. pickle backup not found. pulling data from coinbase.")
        #cryptoList = {}
        #funding = 0
        #bal.close()
        #outfile.close()
    
        
        

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
        
#updateFromCoinbase(cryptoList, False)
restorePickle()

writeLogFile(logFileName, "funding: " + str(funding))
for i in range(len(cryptoList)):
        if(cryptoList[i].balance > 0):
            writeLogFile(logFileName, str(cryptoList[i].name) + "bal" + str(cryptoList[i].balance) + "value:" + str(cryptoList[i].value))
            
#del cryptoList[-1]          #test to find a "new" crypto and buy it
while(True):
    updateFromCoinbase(cryptoList, True)
    print("funds:", funding, " overall profit:", calculateProfit(cryptoList))
    pickleLog(cryptoList)
    time.sleep(0.5)
    
      

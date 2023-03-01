bloglink="http://aminoapps.com/p/kjhuex"

import os
#os.system("pip install Dick.py==1.2.4")
import amino
from threading import Thread
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from os import path
import json
THIS_FOLDER = path.dirname(path.abspath(__file__))
emailfile=path.join(THIS_FOLDER,"acc.json")
dictlist=[]
with open(emailfile) as f:
    dictlist = json.load(f)

#dicklis=dictlist.reverse()
def log(cli : amino.Client,email : str, password : str):
    try:
        cli.login(email=email,password=password)
    except Exception as e:
    	print(e)
    	pass

def threadit(acc : dict):
    email=acc["email"]
    password=acc["password"]
    device=acc["device"]
    client=amino.Client(deviceId=device)
    log(cli=client,email=email,password=password);print("\n°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°")
    print(f"Logged In {email}")
    xd=client.get_from_code(bloglink)
    id=xd.objectId
    cid=xd.path[1:xd.path.index("/")]
    client.join_community(cid)
    subclient=amino.SubClient(comId=cid,profile=client.profile)
    coin=int(client.get_wallet_info().totalCoins)
    print("Total Coins in wallet : "+str(coin))
    while coin>500:
    	try:
    		subclient.send_coins(coins=500,blogId=id)
    		print(f"Transferred 500 COINS")
    	except Exception as e:
    		print(e)
    		pass
    coin=int(client.get_wallet_info().totalCoins)
    if coin>1 and coin<500:
    	try:
    		subclient.send_coins(coins=coin,blogId=id)
    		print(f"Transferred {coin} COINS")
    	except Exception as e:
    		print(e)
    		pass
    #except Exception:pass
  
def main():
    print(f"\n\33[48;5;5m\33[38;5;234m ❮ {len(dictlist)} ACCOUNTS LOADED ❯ \33[0m\33[48;5;235m\33[38;5;5m \33[0m")
    for amp in dictlist:
        threadit(amp)
    print(f"\n\n\33[48;5;5m\33[38;5;234m ❮ Transferred all coins from {len(dictlist)} ACCOUNTS ❯ \33[0m\33[48;5;235m\33[38;5;5m \33[0m")
    	         
if __name__ == '__main__':
	main()

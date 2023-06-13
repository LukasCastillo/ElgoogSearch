import socket
from colorama import just_fix_windows_console, Fore
from collections import deque
import json
import pickle
import aiohttp
import asyncio
import traceback
import urllib.parse
from bs4 import BeautifulSoup
import keyboard
import sys
import re

test = [
    ("Bogy", "https://bogu.org", "bo"),
    ("Failed", "https://fail.org", "f")
]

#Sends data to server
def sendData(data):
    try:
        dbg("Sending data")
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = "localhost"
        port = 6969
        clientSocket.connect((host, port))
        dbg("Connected!")
        clientSocket.sendall(json.dumps(data, ensure_ascii=False).encode())
        dbg("Waiting for thing")
        clientSocket.close()
        dbg("Finished sending data!")
    except Exception as e:
        print("Error!", e)
        traceback.print_exc()

#colored print functions
inp = lambda *x:input(f"{Fore.YELLOW}{''.join(map(str,x))}{Fore.WHITE}")
dbg = lambda *x:print(f"{Fore.BLUE}{''.join(map(str,x))}{Fore.WHITE}")
err = lambda *x:print(f"{Fore.RED}{''.join(map(str,x))}{Fore.WHITE}")
cor = lambda *x:print(f"{Fore.GREEN}{''.join(map(str,x))}{Fore.WHITE}")

def check_url(url):
    banned = ["pdf", "png", "jpg", "doc", "avi", "mpg", "mp3"]
    filtered = ["en"]

    if "#" in url: return False

    for b in banned:
        if url.endswith("."+b):
            #err(url)
            return False

    if filtered:
      for f in filtered:
        if f not in url: return False
    return True

count = 0
tdata = []
async def main():
    global count
    count = 0
    MAX_COUNT = 10000

    just_fix_windows_console()
    session_timeout = aiohttp.ClientTimeout(total=None,sock_connect=10,sock_read=20)

    q = deque()
    q.append(inp("Input url: "))
    visited = []
    
    async with aiohttp.ClientSession(timeout=session_timeout) as session:

        async def proccess_url(url):
            global count
            if keyboard.is_pressed('x') and keyboard.is_pressed("shift"):
                err("Maunaly Exiting!")
                count = MAX_COUNT
                return
            print(url)
            try:
                if not check_url(url=url):
                    err("Bad url!")
                    return
                if url in visited:
                    cor("Url Visited!")
                    return
                visited.append(url)
                res = await session.get(url=url, ssl=False, timeout=1)

                #check if ok status code
                if res.status != 200: return

                res = await res.text()
                soup = BeautifulSoup(res, "html.parser")
                #dbg(res)

                #if no title return
                if not soup.title: return

                #check language
                if soup.html["lang"] != "" and soup.html["lang"] != "en": return

                #get the data from the site
                desc = ""
                descs = soup.find_all("meta", attrs={"name" : "description"})
                if descs: desc = descs[0]["content"]
                elif len(soup.get_text().split("\n")) > 1: desc = soup.get_text().split("\n")[1]  
                else: desc = soup.title.string
                data = (soup.title.string, url, desc)
                tdata.append(data)

                if len(tdata) > 100:
                    print("100 Send")
                    sendData(tdata)
                    tdata.clear()

                #get the links from the site
                res = res.split("<body",1)[1]
                links = re.findall(r'href="[^"]*"', res)
                
                dbg("Count: ", count)
                if len(links) < 10: cor(links)
                else: cor("Links: ", len(links))

                for link in links:
                    nlink = urllib.parse.urljoin(url, link[6:-1])
                    
                    if nlink not in visited and check_url(url=url): q.append(nlink)
                count += 1
            except asyncio.exceptions.TimeoutError:
                err("Error!: timeout!!")
            except Exception as error:
                err("Error!: ", error)
                traceback.print_exc()
                pass
            
        while q and count < MAX_COUNT:
            await proccess_url(q.popleft())
    dbg(visited)
    print(tdata)
    sendData(tdata)
    print("Finished!")

#fix recursion limit
sys.setrecursionlimit(100000)

asyncio.run(main())
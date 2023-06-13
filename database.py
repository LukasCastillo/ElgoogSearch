import socket
import keyboard
import threading
import sqlite3
import json
import colorama
import pickle

#colors
colorama.just_fix_windows_console()
print(colorama.Fore.GREEN, end="")

dataToPut = []
dataLock = threading.Lock()

dbCon = sqlite3.connect("sqlite/search.db")
dbCur = dbCon.cursor()

def database():
    test = [
        ("Snake", "https://snake.org", "snake"),
        ("Fast", "https://f.org", "o")
    ]

    dbCur.execute("CREATE TABLE IF NOT EXISTS search(title, url, description)")
    dbCur.executemany("INSERT INTO search VALUES(?, ?, ?)", test)
    dbCon.commit()

    for row in dbCur.execute("SELECT title, description, url FROM search ORDER BY title"):
        print(row)

    dbCon.close()


def saveToDatabase():
    dbCur.execute("CREATE TABLE IF NOT EXISTS search(title, url, description)")
    for data in dataToPut:
        dbCur.executemany("INSERT INTO search VALUES(?, ?, ?)", data)
        print(f"Urls: {len(data)}")
    print("Saved to databse!")
    dbCon.commit()

#Function that handles the socket connections
def handleClient(client : socket.socket):
    tdata = bytes()
    #accept all the data from client
    while True:
        data = client.recv(1024)
        if not data: break
        #print(data)
        tdata += data

    tdata = tdata.decode("utf-8")
    #send data to database
    with dataLock:
        dataToPut.append(json.loads(tdata))
    
    print("Connection closed!")
    client.close()

#main function
def main():
    try:
        socketServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = "localhost"
        port = 6969
        socketServer.bind((host, port))
        socketServer.listen(5)
        print(f"Server listening on {host}:{port}")
        while True:
            try:
                if (keyboard.is_pressed('z') and keyboard.is_pressed("shift")):
                    command = input('Command: ')
                    if command == "stop": break
                    elif command == "data":
                        for row in dbCur.execute("SELECT title, description, url FROM search ORDER BY title"):
                            print(row)
                    elif command == "clear":
                        dbCur.execute("DELETE FROM search")
                        print("Cleared database!")
                    else: print("Invalid Command")

                #check if there is data to save
                with dataLock:
                    if len(dataToPut) > 0:
                        saveToDatabase()
                        dataToPut.clear()
                #accept incoming socket conenctions
                socketServer.settimeout(1)
                client, clientAddress = socketServer.accept()
                print(f"New connnection {clientAddress[0]}:{clientAddress[1]}")
                clientThread = threading.Thread(target=handleClient, args=(client,))
                clientThread.start()
            except socket.timeout: pass
            except Exception as e:
                print("Error!", e)
        
        print("Stopping server!")
        socketServer.close()
        rowCount = 0
        for row in dbCur.execute("SELECT title, description, url FROM search ORDER BY title"): rowCount += 1
        print(f"Total rows: {rowCount}")
        dbCon.close()

    except Exception as e:
        print("Error!", e)

command = input("Command: ")
if command == "clear":
    dbCur.execute("DELETE FROM search")
    print("Cleared database!")
elif command == "data":
    for row in dbCur.execute("SELECT title, description, url FROM search ORDER BY title"):
        print(row)
main()
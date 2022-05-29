import threading
import time
from socket import *

lock = threading.Lock()

# Use this class for shared variables
class SharedData:
    def __init__(self):
        self.order = []
        self.messages = {"X": "", "Y": ""}
        self.bufferFull = {"X": False, "Y": False}
        self.connected = {"X": False, "Y": False}

    def hasMessage(self, client):
        return self.bufferFull[client]

    def areConnected(self):
        if self.connected["X"] or self.connected["Y"]:
            return True
        else:
            return False


# Sender thread to send messages to client
def Sender(name, socket, data):
    while data.areConnected():
        sender = "Y" if name == "X" else "X"

        message = ""
        # check buffer if sender has placed message lock and grab message
        if data.bufferFull[sender]:
            lock.acquire()
            message = data.messages[sender]
            data.bufferFull[sender] = False
            lock.release()
            # send message
            socket.send(message.encode())
            print("{} sending {} ".format(name, message))
        if message.strip().lower() == "bye" or not data.connected[name]:
            lock.acquire()
            data.connected[name] = False
            lock.release()

    socket.close()


# This function used to create the thread connections
def connect(name, socket, data):

    # Just output to tell what client you are and show in server instance
    if name == "X":
        print("Accepted first connection, calling it client X")
        socket.send("Client X connected".encode())
    elif name == "Y":
        print("Accepted second connection, calling it client Y")
        socket.send("Client Y Connected".encode())
    else:
        print("unknown client error")

    # Set ourselves as connected
    data.connected[name] = True

    # Wait for both clients to connect
    while True:
        if data.connected["X"] and data.connected["Y"]:
            break

    # both connected now send ok
    time.sleep(0.25)
    socket.send("yes".encode())

    # we need to create a sender thread to not block on waiting
    sender = threading.Thread(target=Sender, args=(name, socket, data))
    sender.start()

    # While loop to recieve messages from client
    while data.areConnected():
        socket.settimeout(1)
        try:
            message = socket.recv(1024).decode()
        except:
            message = "bye"
            continue

        # wait for buffer
        while data.bufferFull[name]:
            time.sleep(0.25)
            # Lock data and set message also append your name to the order
        lock.acquire()
        data.bufferFull[name] = True
        data.messages[name] = message
        data.order.append(name)
        lock.release()
        if message.strip().lower() == "bye":
            lock.acquire()
            data.connected[name] = False
            lock.release()

    sender.join()
    socket.close()


def Main():
    serverPort = 12000
    serverSocket = socket(AF_INET, SOCK_STREAM)
    # this line I guess sets the timeout to instant after socket closed
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serverSocket.bind(("", serverPort))
    serverSocket.listen(1)

    clients = 1
    threads = ["", ""]
    names = ["X", "Y"]

    # instantiate the messages shared data object
    messages = SharedData()

    print("The server is waiting to receive 2 connections...\n")

    # Create 2 threads
    while clients <= 2:
        connectionSocket, addr = serverSocket.accept()

        # create a connection (thread) put it in the list then start it
        threads[clients - 1] = threading.Thread(
            target=connect, args=(names[clients - 1], connectionSocket, messages)
        )
        threads[clients - 1].start()
        clients += 1

    serverSocket.close()
    # we need a message so wait until both clients connected then print
    while not messages.connected["X"] and not messages.connected["Y"]:
        thread.sleep(0.25)
    print("\nSession active\n")

    # wait here for the threads to complete
    for thread in threads:
        thread.join()
    print("Waiting for clients to close their connections...")
    time.sleep(2)

    print("\nMain Done")


if __name__ == "__main__":
    Main()

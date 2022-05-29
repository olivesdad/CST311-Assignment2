import threading
from socket import *
import time

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

    def clear(self):
        for name in self.messages:
            self.messages[name] = ""
            self.bufferFull[name] = False


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
        time.sleep(0.25)
        if data.connected["X"] and data.connected["Y"]:
            break

    # both connected now send ok
    socket.send("yes".encode())

    # wait for data from client
    message = socket.recv(1024).decode()

    # Lock data and set message also append your name to the order
    lock.acquire()
    data.bufferFull[name] = True
    data.messages[name] = message
    data.order.append(name)
    lock.release()

    # Now we need server to print the message and order
    place = 1 if name == data.order[0] else 2
    print("Client {} sent message {}: {}".format(name, str(place), data.messages[name]))

    # wait for both clients to send
    while True:
        time.sleep(0.25)
        if data.hasMessage("Y") and data.hasMessage("X"):
            break

    # This is kind of hacky... use the order of the 'order' list to determine who sent first
    first = data.order[0]
    second = data.order[1]
    results = "{}: {} recieved before {}: {}".format(
        first, data.messages[first], second, data.messages[second]
    )
    socket.send(results.encode())
    socket.close()


def Main():
    serverPort = 12000
    serverSocket = socket(AF_INET, SOCK_STREAM)
    # this line I guess sets the timeout to instant after socket closed
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serverSocket.bind(("", serverPort))
    serverSocket.listen(1)

    threads = []
    names = ["X", "Y"]

    # instantiate the messages shared data object
    messages = SharedData()

    print("The server is waiting to receive 2 connections...\n")

    # Create 2 threads
    for name in names:

        connectionSocket, addr = serverSocket.accept()
        # create a connection (thread) put it in the list then start it
        t = threading.Thread(target=connect, args=(name, connectionSocket, messages))
        t.start()
        threads.append(t)
    serverSocket.close()
    # we need a message so wait until both clients connected then print
    while not messages.connected["X"] and not messages.connected["Y"]:
        time.sleep(0.25)

    print("\nWaiting to receive messages from client X and client Y...\n")

    # wait here for the threads to complete
    for thread in threads:
        thread.join()
    # clear messages. Not needed for this version but test for persistant chat
    messages.clear()

    print("\nDone")


if __name__ == "__main__":
    Main()

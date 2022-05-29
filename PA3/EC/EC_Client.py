from concurrent.futures import thread
from socket import *
import signal
import threading

tLock = threading.Lock()
serverName = "127.0.0.1"
serverPort = 12000


def threadListener(sock, connected, name):
    # loop for reading and printing messages
    sock.settimeout(4)

    # flip name
    name = "Y" if name == "X" else "X"
    while connected[0]:
        try:
            message = sock.recv(1024).decode()
        except timeout:
            continue
        if message.strip().lower() == "bye":
            tLock.acquire()
            connected[0] = False
            tLock.release()
            print("{} said Bye!".format(name))
            break
        if message.strip().lower() != "":
            print("{}: {}".format(name, message))
    sock.close()


def main():

    connected = [True]

    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))

    # This bit is for the "client has connected"
    serverResponse = clientSocket.recv(1024)
    # get my name
    name = serverResponse.decode().split(" ")[1]

    print("From Server: " + serverResponse.decode())

    # Wait for ok
    ok = "no"
    while ok != "yes":
        ok = clientSocket.recv(1024).decode()

    # create listener thread
    chatListener = threading.Thread(
        target=threadListener, args=(clientSocket, connected, name)
    )
    chatListener.start()

    print("You're now connected! start chatting!")
    # loop for message sending
    while connected[0]:
        # Here to send the message
        message = ""

        signal.alarm(5)
        try:
            message = input()
        except:
            print("slowby")
        # if we send bye then set connected to false
        if message.strip().lower() == "bye":
            tLock.acquire()
            connected[0] = False
            tLock.release()
        try:
            clientSocket.send(message.encode())
        except:
            continue

    # wait for listener to end then close socket
    print("Shutting Down....")
    chatListener.join()
    print("Goodbye!")
    clientSocket.close()


if __name__ == "__main__":
    main()

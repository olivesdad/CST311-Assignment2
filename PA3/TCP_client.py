from socket import *

serverName = "127.0.0.1"
serverPort = 12000


def main():

    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))

    # This bit is for the "client has connected"
    serverResponse = clientSocket.recv(1024)
    print("From Server: " + serverResponse.decode())

    # Wait for ok
    ok = "no"
    while ok != "yes":

        ok = clientSocket.recv(1024).decode()

    # Here to send the message
    message = input("Enter message to send to server: ")
    clientSocket.send(message.encode())

    # here prints the messages
    serverResponse = clientSocket.recv(1024)
    print("From Server: " + serverResponse.decode())

    clientSocket.close()


if __name__ == "__main__":
    main()

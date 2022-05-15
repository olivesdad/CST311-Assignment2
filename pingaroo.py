from socket import *
import time
import sys

timeouts = 1
numPings = 10

# Use this to calculate rtt and maintain ertt and devrtt
def timeDiff(start, end, rtts, ertt, devrtt):
    a = 0.125
    b = 0.25

    diff = round(end * 1000 - start * 1000, 4)
    rtts.append(diff)

    # update ertt
    ertt[0] = diff if (ertt[0] == 0) else (1 - a) * ertt[0] + (a * diff)
    # update devrtt
    devrtt[0] = (
        diff / 2 if devrtt[0] == 0 else (1 - b) * devrtt[0] + b * abs(diff - ertt[0])
    )

    return diff


# call at the end to print results of ping test
def printSummary(pings, rtts, ertt, devrtt):
    try:
        loss = (int(pings) - len(rtts)) / int(pings) * 100

        min = timeouts * 1000
        max = 0
        sum = 0
        hit = len(rtts)

        for num in rtts:
            if num < min:
                min = num
            elif num > max:
                max = num
            sum += num

        rttAvg = sum / hit
        print(
            "\nRESULTS: \n"
            "Attempts:    " + str(pings) + "\n"
            "Responsees:  " + str(hit) + "\n"
            "Loss rate:   " + str(round(loss, 4)) + "%\n"
            "Min rtt:     " + str(min) + "ms\n"
            "Max rtt:     " + str(max) + "ms\n"
            "Average RTT: " + str(round(rttAvg, 4)) + "ms\n"
            "Timeout:     " + str(round(ertt + (4 * devrtt), 4)) + "ms"
        )
    except ZeroDivisionError:
        print("NO RESPONSE!")


# ping loop
def pingaroo(ip, port, pings):
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.settimeout(timeouts)
    rtts = []
    ertt = [0]
    devrtt = [0]
    mess = "Ping"

    print("Ping to: " + str(ip) + ":" + str(port) + " Count: " + str(pings) + "\n")

    for i in range(0, numPings):
        # try block, get a time stamp, send message wait for response, print response increment hit counter
        try:
            print('sending "' + mess + '" to ' + str(ip) + ":" + str(port))
            start = time.perf_counter()
            clientSocket.sendto(mess.encode(), (ip, port))
            modMess, serverAddress = clientSocket.recvfrom(2048)
            diff = str(timeDiff(start, time.perf_counter(), rtts, ertt, devrtt))

            print(
                "Response: " + modMess.decode() + "\n"
                "rtt:      " + diff + "ms\n"
                "est rtt:  " + str(round(ertt[0], 4)) + "ms\n"
                "dev rtt:  " + str(round(devrtt[0], 4)) + "ms\n"
            )

        # socket throws timeout exception so if we exceet timeout go here and just print timeout
        except timeout:
            print("Request Timeout\n")

    # do the summary thing
    printSummary(numPings, rtts, ertt[0], devrtt[0])
    clientSocket.close()


# MAIN
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: \n python pingaroo <ip> <port>")
        quit()
    pingaroo(sys.argv[1], int(sys.argv[2]), numPings)

from socket import *
import time
import sys

timeouts = 1
numPings = 10

# no arrays :(
class PingStats:
    a = 0.125
    b = 0.25
    pings = 0
    miss = 0
    msTotal = 0

    def __init__(self, minv, maxv, devrtt, ertt):
        self.minv = minv
        self.maxv = maxv
        self.devrtt = devrtt
        self.ertt = ertt

    def newPing(self, rtt):
        # update minmax
        if self.maxv < rtt:
            self.maxv = rtt
        elif self.minv > rtt:
            self.minv = rtt

        # update ertt
        self.ertt = (
            rtt if (self.ertt == 0) else (1 - self.a) * self.ertt + (self.a * rtt)
        )

        # update devrtt
        self.devrtt = (
            rtt / 2
            if self.devrtt == 0
            else (1 - self.b) * self.devrtt + self.b * abs(rtt - self.ertt)
        )

        # add ping
        self.pings = self.pings + 1

        # update avg
        self.msTotal += rtt

    def timeOut(self):
        self.miss += 1

    def print(self):

        try:
            loss = (self.miss / (self.pings + self.miss)) * 100
            avg = self.msTotal / self.pings
        except ZeroDivisionError:
            loss = 100
            avg = 0
        print(
            "\nPING RESULTS: \n"
            "Attempts:    " + str(self.pings + self.miss) + "\n"
            "Responsees:  " + str(self.pings) + "\n"
            "Loss rate:   " + str(round(loss, 4)) + "%\n"
            "Min rtt:     " + str(self.minv) + "ms\n"
            "Max rtt:     " + str(self.maxv) + "ms\n"
            "Average RTT: " + str(round(avg, 4)) + "ms\n"
            "Timeout:     " + str(round(self.ertt + (self.devrtt), 4)) + "ms"
        )


# Use this to calculate rtt and maintain ertt and devrtt
def timeDiff(start, end, stats):

    diff = round(end * 1000 - start * 1000, 4)
    stats.newPing(diff)

    return diff


# ping loop
def pingaroo(ip, port, pings):
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.settimeout(timeouts)

    mess = "Ping"

    stats = PingStats(timeouts * 1000, 0, 0, 0)

    stats.print()
    print("Ping to: " + str(ip) + ":" + str(port) + " Count: " + str(pings) + "\n")

    for i in range(0, numPings):
        # try block, get a time stamp, send message wait for response, print response increment hit counter
        try:
            print('sending "' + mess + '" to ' + str(ip) + ":" + str(port))
            start = time.perf_counter()
            clientSocket.sendto(mess.encode(), (ip, port))
            modMess, serverAddress = clientSocket.recvfrom(2048)
            diff = str(timeDiff(start, time.perf_counter(), stats))

            print(
                "Response: " + modMess.decode() + "\n"
                "rtt:      " + diff + "ms\n"
                "est rtt:  " + str(round(stats.ertt, 4)) + "ms\n"
                "dev rtt:  " + str(round(stats.devrtt, 4)) + "ms\n"
            )

        # socket throws timeout exception so if we exceet timeout go here and just print timeout
        except timeout:
            stats.timeOut()
            print("Request Timeout\n")

    # do the summary thing
    stats.print()
    clientSocket.close()


# MAIN
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: \n python pingaroo <ip> <port>")
        quit()
    pingaroo(sys.argv[1], int(sys.argv[2]), numPings)

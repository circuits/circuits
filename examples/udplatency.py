#!/usr/bin/env python

from time import time

from circuits.net.sockets import UDPClient, UDPServer, Write

class LatencyServer(UDPServer):

    channel = "server"

    def read(self, address, data):
        self.push(Write(address, data))

class LatencyClient(UDPClient):

    channel = "client"

    count = 0
    data = []

    def ready(self, cmp):
        self.push(Write(("127.0.0.1", 8000), str(time())))

    def read(self, address, data):
        latency = time() - float(data)
        self.data.append(latency)
        print "Round Trip: %0.2fs" % latency
        self.count += 1
        if self.count < 10:
            self.push(Write(("127.0.0.1", 8000), str(time())))
        else:
            average = sum(self.data) / len(self.data)
            print "Average Latency: %0.2fs" % average
            raise SystemExit, 0

(LatencyServer(8000) + LatencyClient(8001)).run()

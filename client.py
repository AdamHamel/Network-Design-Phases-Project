from socket import *
import math
import time
import numpy as np
import cv2 as cv
import tkinter as tk
from PIL import Image, ImageTk
import binascii
import socket
import struct
import sys
import hashlib
import base64
import random
from struct import *
import datetime
from makePackets import makePackets

def clientSide(inputData, cRate, pLossRate):
    corruptRate = float(cRate)
    packetLoss = float(pLossRate)

    def ackCorruption(rate, ackValue):
        newACK = ackValue
        if random.random() <= rate:
            newACK = random.randint(2, 9)

        return newACK

    serverName = '10.0.0.102'  # Server Address, IP4 Address
    serverPort = 12345
    clientSocket = socket.socket(AF_INET, SOCK_DGRAM)

    SEQ = 0

    size, data = makePackets(inputData, 1024)

    clientSocket.sendto(str(size).encode(), (serverName, serverPort))

    for packets in range(len(data)):
        clientSocket.settimeout(0.03)
        sending = True
        while sending:
            ##################  CHECKSUM  ####################
            packed_data = pack(f'i {len(data[packets])}s', SEQ, data[packets])
            checksum = hashlib.md5(packed_data).hexdigest().encode('utf-8')
            ##################  CHECKSUM  ####################

            if random.random() > packetLoss:
                message = pack(f'i {len(checksum)}s {len(data[packets])}s', SEQ, checksum, data[packets])
                clientSocket.sendto(message, (serverName, serverPort))

            try:
                ackPacket, serverAddress = clientSocket.recvfrom(2048)
                serverSEQ, sACK = unpack('ii', ackPacket)
                sending = False

                sACK = ackCorruption(corruptRate, sACK)
                if sACK == SEQ and serverSEQ == SEQ:
                    print("Client: Positive")
                else:
                    while True:
                        if sACK > 1:
                            print("Client: Corrupted ACK")
                        elif SEQ != serverSEQ and sACK < 2:
                            print("Client: Duplicate Packet. Sending Next Packet")
                            break
                        else:
                            print("Client: Negative, Sending New packet")

                        message = pack(f'i {len(checksum)}s {len(data[packets])}s', SEQ, checksum, data[packets])
                        clientSocket.sendto(message, (serverName, serverPort))

                        ackPacket, serverAddress = clientSocket.recvfrom(2048)
                        serverSEQ, sACK = unpack('ii', ackPacket)
                        sACK = ackCorruption(corruptRate, sACK)

                        if SEQ != serverSEQ and sACK < 2:
                            print("Client: Duplicate Packet. Sending Next Packet")
                            break
                        if sACK == SEQ:
                            print("Client: Corrupt Packet Corrected")
                            break

            except TimeoutError:
                print("Client: Packet/ACK Loss")

        SEQ = int(not SEQ)
    clientSocket.close()


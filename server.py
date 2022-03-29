from difflib import SequenceMatcher
from socket import *
import math
import time
import numpy as np
import cv2 as cv
import tkinter as tk
from PIL import Image, ImageTk
import binascii
import sys
import hashlib
import base64
import random
from struct import *
import datetime

def serverSide(cRate, ackRate):
    ackLoss = float(ackRate)
    corruptRate = float(cRate)

    serverPort = 12345
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', serverPort))
    numPacket = 0
    # print("Server Opened At: %s" % datetime.datetime.now())
    numPackets, clientAddress = serverSocket.recvfrom(2048)
    receivedFile = []
    receiving = 0
    previousSEQ = 1
    size = int(numPackets.decode())

    ######## Corruption Creation for Data Bits ########
    def corruption(rate, inputData):
        newData = inputData
        if random.random() <= rate:
            index = random.randint(0, len(inputData))
            newData = inputData[:index] + random.randint(0, 255).to_bytes(1, 'big') + inputData[index + 1:]
        return newData

    ######## Corruption Creation for Data Bits ########
    while True:

        ######## RECEIVE AND UNPACK DATA #########
        message, clientAddress = serverSocket.recvfrom(2048)
        SEQ, checksum, data = unpack(f'i 32s {len(message[36:])}s', message)
        ######## RECEIVE AND UNPACK DATA #########

        ######## Corruption Creation for Data Bits ########
        data = corruption(corruptRate, data)
        ######## Server Side Checksum Created for Comparison ########
        packed_data = pack(f'i {len(data)}s', SEQ, data)
        serverChkSum = hashlib.md5(packed_data).hexdigest().encode('utf-8')

        ######## Acknowledgement System ########

        while True:

            # All conditions met, sends next packet.
            if serverChkSum == checksum and previousSEQ != SEQ:
                print("Server: Packet Passes.")
                ACK = SEQ
                previousSEQ = SEQ
                receivedFile.append(data)
                receiving = receiving + 1
                ackPacket = pack('ii', SEQ, ACK)
                if random.random() > ackLoss:
                    serverSocket.sendto(ackPacket, clientAddress)
                break
            # Duplicate packets determined by SEQ value, sending next packet.
            elif previousSEQ == SEQ:
                print("Server: Duplicate Packet")
                ACK = int(not SEQ)
                ackPacket = pack('ii', int(not SEQ), ACK)
                if random.random() > ackLoss:
                    serverSocket.sendto(ackPacket, clientAddress)
                break
            # Packet was corrupted, determined by ACK, resending packet.
            else:
                print("Server: Packet Corrupted.")
                ACK = int(not SEQ)
                ackPacket = pack('ii', SEQ, ACK)
                serverSocket.sendto(ackPacket, clientAddress)
                message, clientAddress = serverSocket.recvfrom(2048)
                SEQ, checksum, data = unpack(f'i 32s {len(message[36:])}s', message)
                data = corruption(corruptRate, data)
                packed_data = pack(f'i {len(data)}s', SEQ, data)
                serverChkSum = hashlib.md5(packed_data).hexdigest().encode('utf-8')

        ######## Acknowledgement System ########
        if receiving == size:
            ACK = SEQ
            ackPacket = pack('ii', SEQ, ACK)
            serverSocket.sendto(ackPacket, clientAddress)
            break

    ######## Display ########
    image = receivedFile[0]
    for i in range(1, size):
        image = image + receivedFile[i]

    return image


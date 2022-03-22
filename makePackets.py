import math
import numpy as np
import cv2 as cv
import numpy
import tkinter as tk

def makePackets(userFile, pSize):
    inputFile = open(userFile, 'rb')
    inputFile = inputFile.read()
    dataFile = []

    numPackets = math.floor(len(inputFile) / pSize)
    if len(inputFile) % pSize != 0:
        numPackets = numPackets + 1

    for i in range(numPackets):  # Creates list of
        bytes_s = inputFile[i * pSize:(i + 1) * pSize]
        dataFile.append(bytes_s)

    return numPackets, dataFile

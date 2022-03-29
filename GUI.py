from client import clientSide
from server import serverSide
import threading
import concurrent.futures
from _thread import *
from socket import *
import math
import time
import numpy as np
import cv2 as cv
from tkinter import *
from PIL import Image, ImageTk
import binascii
import socket
import struct
import sys
import hashlib
import base64
from struct import *
import datetime
import time


window = Tk()
window.title("Image Transfer GUI")

myLabel = Label(
    text='Enter Image Name From Directory Folder',
    height=3,
    width=50,
    background="white",
    foreground="black"
)
myLabel.pack()

dataEntry = Entry(
    bg="white",
    fg="black",
    borderwidth=5,
    width=20,
)
dataEntry.pack()

myLabel2 = Label(
    text='Corruption Rate, (0.0 - 1.0)',
    height=3,
    width=50,
    background="white",
    foreground="black"
)
myLabel2.pack()
corruptEntry = Entry(
    bg="white",
    fg="black",
    borderwidth=5,
    width=20,
)
corruptEntry.pack()

r = IntVar()
Radiobutton(window, text="Option 1, No corruption", variable=r, value=0).pack()
Radiobutton(window, text="Option 2, ACK corruption", variable=r, value=1).pack()
Radiobutton(window, text="Option 3, Data Corruption", variable=r, value=2).pack()
Radiobutton(window, text="Option 4, Data Loss", variable=r, value=3).pack()
Radiobutton(window, text="Option 5, ACK Loss", variable=r, value=4).pack()

def openImage(value):
    global my_img, packetCorrupt, ackCorrupt, pLossCorrupt, ackLoss
    start = time.perf_counter()

    data = dataEntry.get()
    match value:
        case 0:
            packetCorrupt = 0
            pLossCorrupt = 0
            ackCorrupt = 0
            ackLoss = 0
        case 1:
            packetCorrupt = 0
            pLossCorrupt = 0
            ackLoss = 0
            ackCorrupt = corruptEntry.get()
        case 2:
            packetCorrupt = corruptEntry.get()
            pLossCorrupt = 0
            ackCorrupt = 0
            ackLoss = 0
        case 3:
            packetCorrupt = 0
            pLossCorrupt = corruptEntry.get()
            ackCorrupt = 0
            ackLoss = 0
        case 4:
            packetCorrupt = 0
            pLossCorrupt = 0
            ackCorrupt = 0
            ackLoss = corruptEntry.get()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        client = executor.submit(clientSide, data, ackCorrupt, pLossCorrupt)
        server = executor.submit(serverSide, packetCorrupt, ackLoss)

    finish = time.perf_counter()
    total_time = round(finish - start, 5)

    my_label = Label(window, text=f'Execution Time: {total_time}').pack()
    window.update()

    image = server.result()
    image = np.asarray(bytearray(image), dtype="uint8")
    image = cv.imdecode(image, cv.IMREAD_COLOR)

    cv.imshow('img', image)

    ######## Display ########
    cv.waitKey()

button = Button(
    text="Import",
    width=10,
    height=1,
    bg="white",
    fg="black",
    command=lambda: openImage(r.get())
).pack()

window.mainloop()

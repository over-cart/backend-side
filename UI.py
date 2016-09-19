#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending."
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# definition of functions
def init_reader():
    global MIFAREReader

    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    (status,uid) = MIFAREReader.MFRC522_Anticoll()
    if status == MIFAREReader.MI_OK:
        MIFAREReader.MFRC522_SelectTag(uid)
    return (status,uid)

# sectors: list
# return: read list
def read_sectors(uid, sectors):
    global MIFAREReader
    key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
    data = []

    for i in sectors:
        if i in range(0,64):
            status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, i, key, uid)
            if status == MIFAREReader.MI_OK:
                data += MIFAREReader.MFRC522_Read(i)
    return data

# start: int, data: list
# return: number of failure
def write_sectors(uid, start, data):
    global MIFAREReader
    key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
    count = 0

    for i in range(0,len(data)/16):
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, start+i, key, uid)
        if status == MIFAREReader.MI_OK:
            count += MIFAREReader.MFRC522_Write(start+i, data[16*i:16*i+16])
    return len(data)/16 - count

# save number per byte from left to right
def listToNum(numList):
    if numList is None:
        return -1
    num = 0
    for i in range(0,len(numList)):
        if numList[i] > 255:
            numList[i] = 255
        elif numList[i] < 0:
            numList[i] = 0
        num += numList[i] << 8*i
    return num

def numToList(num,size=16):
    l = []
    mask = 0xFF
    for i in range(0,size):
        l.append(int((num & (mask << 8*i)) >> 8*i))
    return l

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:

    (status,uid) = init_reader()
    if status == MIFAREReader.MI_OK:
        print "========================="
        print "select."
        print "1.read NodeID"
        print "2.read Type"
        print "3.read Location"
        print "4.read all"
        print "5.write Type"
        print "6.write Location"
        print "7.exit"
        print "========================="

        sel = input()
        if sel == 1:
             print uid
        elif sel == 2:
             tmp = read_sectors(uid,[1])
             print listToNum(tmp)
        elif sel == 3:
             tmp = read_sectors(uid,[2])
             print listToNum(tmp)
        elif sel == 4:
             print uid
             tmp = read_sectors(uid,[1,2])
             print listToNum(tmp[0:16])
             print listToNum(tmp[16:32])
        elif sel == 5:
             print "0: nothing / 1: ingate point / 2: outgate point"
             print "3: | point / 4: T point / 5: cross point"
             print "type. ",
             num = input()
             if num in range(0,6):
                 print(write_sectors(uid,1,numToList(num))),
                 print " failed."
             else:
                 print "not in range"
        elif sel == 6:
             print "input must be over 0"
             print "type. ",
             num = input()
             if num > 0:
                 print(write_sectors(uid,2,numToList(num))),
                 print " failed."
             else:
                 print "not over 0"
        MIFAREReader.MFRC522_StopCrypto1()

    if sel == 7:
        GPIO.cleanup()
        break

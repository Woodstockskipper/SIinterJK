# Programm zur Übersetzung der von JK BMS über RS485 gesendeten Zustandsinformationen an die 
# CAN-Bus Schnittstelle des SMA Sunny Island 6.0 und 8.0 (getestet).
# Funktioniert mit RaspberryPi 2B aufwärts, WaveShare CAN/RS485 Hat und 
# JiKong Batteriemanagementsytemen mit JiKong RS485 Adapter.
# Achtung! Dieser Code funktioniert mit 16-Zelligen LiFePo4 Akkus. Bei abweichender Zellenzahl müssen ab Z.43 die auszulesedenden Werte (mit * versehen)nach Anleitung der Schittstellenbeschreibung des BMS angepasst werden. (am Besten die Antwort vom BMS ausdrucken und auszählen)
# 
# Version 1.1 erstellt und zur feien Verfügung gestellt von Stephan Brabeck am 31.3.2023
# 
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import serial
import os
import can
import struct
import binascii
import time
from datetime import datetime

EN_485 =  4 # EN 485 ist Pin 4
GPIO.setmode(GPIO.BCM) 
GPIO.setup(EN_485,GPIO.OUT) 
GPIO.output(EN_485,GPIO.HIGH)
t = serial.Serial("/dev/ttyS0",115200)    #RS485 Schnittstelle definieren

os.system('sudo ip link set can0 type can bitrate 500000') # Siehe Schnittstellenbeschreibung des SMA Sunny Island
os.system('sudo ifconfig can0 up')
can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan')# socketcan_native CAN Schnittstelle definieren
can0.flush_tx_buffer() # CAN socket buffer leeren

# Fixe Parameter definieren: (bitte auf Eure Batterien anpassen)
bcv = 550 # set Battery charge voltage to 55V /0,1
dccl = 1150 # set DC charge current limitation to 115A /0,1
ddcl = 1150 # set DC discharge current limitation to 115A /0,1
bdv = 450 # set min. Battery discharge voltage to 45,0V /0,1
n = 1 # Anzahl der parallel geschalteten Batterien / BMS wenn nur ein BMS ausgelesen wird.
# SOH wird weiter unten immer auf 100% gesetzt.
# Damit der SI möglichst wenig Fehler detektiert, setze ich den erlaubten Bereich für Spannungen und Ströme größer (gerade noch im erlaubten Bereich)an als im BMS.
# So sichert das BMS die Batterieblocks ab und der SI schaltet sich nur bei Abschaltung der Batterie durch das BMS ab.

while True:
# Holen der Informationen vom BMS:
	#Alles lesen:
	command = [0x4E,0x57,0x00,0x13,0x00,0x00,0x00,0x00,0x06,0x03,0x00,0x00,0x00,0x00,0x00,0x00,0x68,0x00,0x00,0x01,0x29]   
	len = t.write(command)    
	#print ("length:",len) 
	stri = t.read(291) # Dieser Wert muss ggf. angepasst werden wenn mehr oder weniger als 16 Batteriezellen verwendet werden
	#print (stri.hex()) # Unkommentieren um die Antwort des BMS zu sehen, z.B. zum Auszählen der Werte bei abweichender Anzahl von Zellen
	
	# Zeit anzeigen
	now = datetime.now() 
	current_time = now.strftime("%H:%M:%S")
	print(current_time)
	
	#T Batterie auslesen
	tbatt = stri[65:67] # *
	tbattd = struct.unpack('>H', tbatt)
	print ("T Batterie = ", tbattd[0],"°C")

	#U Batterie auslesen
	ubatt = stri[71:73] # *
	ubattd = struct.unpack('>H', ubatt)
	print ("U Batterie = ", ubattd[0]/100,"V")

	#I Batterie auslesen
	ibatt = stri[74:76] # *
	#print (ibatt)
	if ibatt[0] & 0x80:
		sign = -1
		chmode = "Ladung"
	else:
		sign = 1
		chmode = "Entladen"
	ibattr = ''.join(format(x, '02x') for x in ibatt)	
	ibatth = ibattr[-3:]
	#print (ibatth)
	ibattd = sign * int(ibatth,16)
	print ("I Batterie = ", "{:.2f}".format(ibattd*n/100),"A", chmode)

	print ("P Batterie = ", "{:.2f}".format(ibattd*n/100*ubattd[0]/100/1000) ,"kW")

	# SOC auslesen
	soc = stri[77:78] # *
	socd = struct.unpack('<B', soc)
	print ("       SOC = ", socd[0],"%")

	#Warnungen auslesen
	wbatt = stri[92:94] # *
	#print (wbatt)
	wbatti = [int(byte) for byte in wbatt]
	#print (wbatti)
	wbattb = ''.join([bin(byte)[2:].zfill(8) for byte in wbatti])
	print (" Warnungen = ", wbattb)	

	#Cmax Batterie auslesen
	cbatt = stri[182:184] # *
	cbattd = struct.unpack('>H', cbatt)
	print ("C Batterie = ", cbattd[0]*n,"Ah")
	print ()

#CAN Ausgabe
	print ("Ausgabe CAN:")
	can0.flush_tx_buffer() # CAN socket buffer leeren, wichtig, da bei nicht emfangsbereitem SI der Puffer vollgeschrieben wird.

#si0x351 Adresse aus Schnittstellenbeschreibung des SMA Sunny Island

	bcvh = format(bcv, '04X') # Format value as 4-digit hexadecimal with leading zeros

	if dccl < 0:
		dccl = 65536 + dccl# Convert negative values to signed equivalent
		
	dcclh = format(dccl, '04X') 

	ddclh = format(ddcl, '04X')

	bdvh = format(bdv, '04X')
     
	msg = [int(x, 16) for x in ["0x"+bcvh[2:], "0x"+bcvh[:2], "0x"+dcclh[2:], "0x"+dcclh[:2], "0x"+ddclh[2:], "0x"+ddclh[:2], "0x"+bdvh[2:], "0x"+bdvh[:2]]]
	#print(msg)
           
	si351 = can.Message(arbitration_id=0x351, data=msg, is_extended_id=False)
	print (si351)
	can0.send(si351)
	time.sleep(0.1)
	
#si0x353 Adresse aus Schnittstellenbeschreibung des SMA Sunny Island

	soch = format(socd[0], '04X') # Format value as 4-digit hexadecimal with leading zeros
	#print (soch)
	
	sohh = format(100, '04X') #SOH ist immer 100%
	#print (sohh)
     
	msg = [int(x, 16) for x in ["0x"+soch[2:], "0x"+soch[:2], "0x"+sohh[2:], "0x"+sohh[:2], "0xFF", "0xFF"]]
	#print(msg)
           
	si355 = can.Message(arbitration_id=0x355, data=msg, is_extended_id=False)
	print (si355)
	can0.send(si355)
	time.sleep(0.1)	

#si0x356 Adresse aus Schnittstellenbeschreibung des SMA Sunny Island

	abvh = format(ubatt[0], '04X') #Aktuelle Batteriespannung 
	#print ("abv=", abvh)	

	abc = int(ibattd*n/10) 
	if abc < 0:
		abc = 65536 + abc # Convert negative values to signed equivalent
	abch = format(abc, '04X') # Aktueller Batteriestrom
	#print ("abc=", abch)	

	abth = format(tbattd[0]*10, '04X')
	#print ("abt=", abth)
     
	msg = [int(x, 16) for x in ["0x"+abvh[2:], "0x"+abvh[:2], "0x"+abch[2:], "0x"+abch[:2], "0x"+abth[2:], "0x"+abth[:2]]]
	#print(msg)
           
	si356 = can.Message(arbitration_id=0x356, data=msg, is_extended_id=False)
	print (si356)
	can0.send(si356)
	time.sleep(0.1)	

#si0x35A Adresse aus Schnittstellenbeschreibung des SMA Sunny Island
	#Warnungen:
	#wbatt = b'\x65\ff'  #Achtung nur Testwert! vor IBN entfernen!
	wbattd = int.from_bytes(wbatt, byteorder='big')
	
	#print (wbattd)

	w12 = (wbattd & 0b10) >> 1 # liest das zweite Bit (1) aus: bit 1: MOS tube over-temperature alarm
	w2 = (wbattd & 0b100) >> 2 # liest das dritte bit aus (2): bit 2 : Charging over-voltage alarm
	w3 = (wbattd & 0b1000) >> 3 # 3 bits: Discharge undervoltage alarm
	w4 = (wbattd & 0b10000) >> 4 # 4 bits: Battery over temperature alarm
	w9 = (wbattd & 0b100000) >> 5 # 5 bits: Charging overcurrent alarm
	w8 = (wbattd & 0b1000000) >> 6 # 6 bits: Discharge overcurrent alarm
	w13 = (wbattd & 0b10000000) >> 7 # 7-bit: Cell pressure difference alarm
	w5 = (wbattd & 0b1000000000) >> 9 # 9 bits: Battery low temperature alarm
	
	#print(w2, w3, w4, w5, w8, w9, w12, w13)

	wb4 = (0 << 7) | (0 << 6) | (w2 << 5) | (0 << 4) | (w3 << 3) | (0 << 2) | (w4 << 1) | (0 << 0)
	wb5 = (w5 << 7) | (0 << 6) | (0 << 5) | (0 << 4) | (0 << 3) | (0 << 2) | (w8 << 1) | (0 << 0)
	wb6 = (w9 << 7) | (0 << 6) | (0 << 5) | (0 << 4) | (0 << 3) | (0 << 2) | (w12 << 1) | (0 << 0)
	wb7 = (w13 << 7) | (0 << 6) | (0 << 5) | (0 << 4) | (0 << 3) | (0 << 2) | (0 << 1) | (0 << 0)

	#print('{:08b}'.format(wb4))
	#print('{:08b}'.format(wb5))
	#print('{:08b}'.format(wb6))
	#print('{:08b}'.format(wb7))
     
	msg = [int(x, 16) for x in ["0x00", "0x00", "0x00", "0x00", hex(wb4), hex(wb5), hex(wb6), hex(wb7)]] # Kein Alarm, nur Warnungen, da Batterien mit BMS eigensicher
	#print(msg)

	si35a = can.Message(arbitration_id=0x35a, data=msg, is_extended_id=False)
	print (si35a)
	can0.send(si35a)
	time.sleep(0.1)	

#si0x35e: Adresse aus Schnittstellenbeschreibung des SMA Sunny Island
	#Herstellerbezeichung
	msg = [int(x, 16) for x in ["0x72", "0x42", "0x62", "0x61", "0x63", "0x65", "0x00", "0x6b"]]
	si35e = can.Message(arbitration_id=0x35e, data=msg, is_extended_id=False)
	print (si35e)
	can0.send(si35e)
	time.sleep(0.1)

#si0x35f: Adresse aus Schnittstellenbeschreibung des SMA Sunny Island
	#Bat-Type, BMS Version, Bat-Capacity, Manufacturer ID = "01"
	cbatth = format(cbattd[0]*n, '04X') #Batteriekapazität
	msg = [int(x, 16) for x in ["0x69", "0x4c", "0x4b", "0x4a", "0x"+cbatth[2:], "0x"+cbatth[:2], "0x31", "0x30"]]
	si35f = can.Message(arbitration_id=0x35f, data=msg, is_extended_id=False)
	print (si35f)
	can0.send(si35f)
	time.sleep(10)
	
	GPIO.cleanup() # Puffer leeren
	print ("\033c") #Bildschirm leeren

# os.system('sudo ifconfig can0 down')
# Ende


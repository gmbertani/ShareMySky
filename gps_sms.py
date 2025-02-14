"""
This program acquires GPS data from a serial port and saves it to a CSV file.

Copyright (C) 2024 Thomas Mazzi

This program is distributed under the GNU General Public License version 3.0.
For more information, see the LICENSE file or visit https://www.gnu.org/licenses/gpl-3.0.html
"""


import serial, requests, time
import matplotlib.pyplot as plt


ser = serial.Serial('/dev/ttyACM0',baudrate=9600,timeout=1)
ser.flushInput()

x=[]
y=[]
k=0
while (True):
	k=k+1
	idsatmax=0
	decsatmax=0
	arsatmax=0
	snrsatmax=0
	timesat=0
	lat=0
	lon=0
	alt=0
	satlist=[]
	a=True
	while (a==True):
		s=str(ser.readline().decode("utf-8")[:-5]).split(',')
		if (s[0]=='$GPRMC'):
			data=s[9][4:6]+s[9][2:4]+s[9][0:2]
			timesat=data+(s[1][:-3])
			lat= int((int(float(s[3])/100) + ( float(s[3])/100 - int(float(s[3])/100))*100/60) *1000000)/1000000
			if (s[4]=='S'):
				lat=-lat
			lon=int((int(float(s[5])/100) + ( float(s[5])/100 - int(float(s[5])/100))*100/60) *1000000)/1000000
			if (s[6]=='W'):
				lon=-lon
			
		if (s[0]=='$GPGSV'):
			numsat=int(s[3])
			tmsg=int(s[1]) 
			nmsg=int(s[2])
			s=s[4:]
			for t in range (len(s)):
				if (s[t]==''):
					s[t]='0'		
			for t in range (0,int(len(s)/4)):
				idsat=int(s[t*4])
				decsat=int(s[t*4+1])
				arsat=int(s[t*4+2])
				snrsat=int(s[t*4+3])
				
				#inserire i dati corretti per la finestra di cutoff
				cutoffarea=((arsat>315) or (arsat<135)) and (decsat>54)
				
				if (cutoffarea==True):
					satlist=satlist+[idsat,arsat,decsat,snrsat]	
				
			if (tmsg==nmsg):
				a=False
	satlist=[timesat,lat,lon]+satlist
	print (satlist)
	
	
	f=open("./gps.csv","a")
	f.write (timesat+","+str(idsatmax)+","+str(arsatmax)+","+str(decsatmax)+","+str(snrsatmax)+"\n")
	f.close()
	
ser.close()


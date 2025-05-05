import serial

# costanti
DEVICE='/dev/ttyACM0'
DIR_FILE="/mnt/ramdisk/"
STATION_NAME="tom"
args.max_sats=33

# finestra cutoff
AZ_da=0
AZ_a=360
ALT_min=45
ALT_max=90



# calcolo media di un vettore
def med (a):
	x=0
	if (len (a)>0):
		x=sum(a)/len(a)
	return x

# calcolo s4c partendo da vettore cn0 in db
def s4c (a):
	x=0
	k=[]
	j=[]
	for t in a:
		i=10**(t/10)
		k=k+[i**2]
		j=j+[i]
	k=med(k)
	j=med(j)**2
	if (j>0) and (k>=j):
		x=((k-j)/j)**0.5
		x=int(x*100+0.5)/100
	return x
	
	
# crea array di array vuoti di n elementi
def array (n):
	x=[]
	for t in range (0,n):
			x=x+[[]]
	return (x)
	
	
# legge i dati dall'antenna	
def readgps ():
	s=str(ser.readline().decode("utf-8"))
	
	# calcola il checksum
	payload_start = s.find('$') + 1  # trova il primo carattere dopo $
	payload_end   = s.find('*')      # trova il carattere *
	payload = s [ payload_start : payload_end ]   # dati di cui fare XOR
	ck = 0
	for ch in payload:      # ciclo di calcolo del checksum
		ck = ck ^ ord(ch)   # XOR
	str_ck = '%02X' % ck    # trasforma il valore calcolato in una stringa di 2 caratteri
	
	# controlla checksum
	if (s[-4:-2]!=str_ck):
		s="$ERR"

	# decodifica stringa GPS
	s=s[:-5].split(',')
	for t in range (len(s)):
		if (s[t]==''):
			s[t]='0'
	return (s)


# imposta la seriale e vuota il buffer
ser = serial.Serial(DEVICE,baudrate=9600,timeout=1)
ser.flushInput()


# sicronizza la partenza al secondo 00
timesat_old=""
second=""
print ("--- SHARE MY SKY ---\n")
print ("Dati ricevitore:")

while (second!="00"):
	s=readgps()
	
	if (s[0]=='$GPTXT'):
		print (s[4])
		
	# decodifica il codice nmea0183 GPRMC per avere latitudine longitudine e l'orario gps
	if (s[0]=='$GPRMC'):
		timesat_old=s[9][4:6]+s[9][2:4]+s[9][0:2]+s[1][:-5]
		second=s[1][-5:-3]
		lat=str(int(float(s[3]))/100)+" "+s[4]
		lon=str(int(float(s[5]))/100)+" "+s[6]

print ()

print("Start ",timesat_old," coordinate: ",lat,"-",lon,"\n")


# crea gli array vuoti
azsatvet=array (args.max_sats)
altsatvet=array (args.max_sats)
cn0satvet=array (args.max_sats)

while (True):
		
		# legge nmea0183 da seriale
		s=readgps()
		
		# decodifica il codice nmea0182 GPRMC
		if (s[0]=='$GPRMC'):
			date=s[9][4:6]+s[9][2:4]+s[9][0:2]
			timesat=s[9][4:6]+s[9][2:4]+s[9][0:2]+s[1][:-5]
			second=s[1][-5:-3]
			
			# al secondo 00 esegue la statistica e logga i risultati
			if (second=="00"):
				# calcolo delle coordinate medie e dell sqm del segnale per ogni satellite valido		
				for t in range (0,args.max_sats):
					if (len(cn0satvet[t])>0):
						azmed=int(med(azsatvet[t])*10+0.5)/10
						altmed=int(med(altsatvet[t])*10+0.5)/10
						cn0med=int(med(cn0satvet[t])*10+0.5)/10
						cn0s4c=s4c(cn0satvet[t])
						cn0s=""
						for x in range(int(cn0s4c/0.333)):
							cn0s=cn0s+"*"
						
						print (f'{timesat_old:6}  sat: {t:2}   az: {azmed:5}   alt: {altmed:4}   cn0: {cn0med:4}   s4c:{cn0s4c:5} {cn0s}')
						LOG_FILE=DIR_FILE+"gps_"+STATION_NAME+"_"+date+".csv"
						f=open(LOG_FILE,"a")
						s1=str(timesat_old)+","+str(t)+","+str(azmed)+","+str(altmed)+","+str(cn0med)+","+str(cn0s4c)+"\n"
						f.write (s1)
						f.close()
				print ()
				# vuota gli array
				azsatvet=array (args.max_sats)
				altsatvet=array (args.max_sats)
				cn0satvet=array (args.max_sats)
				timesat_old=timesat
		
	
		# decodifica il codeice nmea0183 GPGSV
		if (s[0]=='$GPGSV'):
			s=s[4:]
				
			for t in range (0,int(len(s)/4)):
				idsat=int(s[t*4])
				altsat=int(s[t*4+1])
				azsat=int(s[t*4+2])
				cn0sat=int(s[t*4+3])
			
				# calcola la finestra di cutoff
				if AZ_da<=AZ_a:
					cutoffarea=(azsat>=AZ_da and azsat<=AZ_a) and (altsat>=ALT_min and altsat<=ALT_max)
				else:
					cutoffarea=(azsat>=AZ_da or azsat<=AZ_a) and (altsat>=ALT_min and altsat<=ALT_max)
				
				# memorizza i valori dei satelliti validi
				if ((cutoffarea==True) and (idsat<args.max_sats)):
					azsatvet[idsat]=azsatvet[idsat]+[azsat]
					altsatvet[idsat]=altsatvet[idsat]+[altsat]
					cn0satvet[idsat]=cn0satvet[idsat]+[cn0sat]	
			
ser.close()


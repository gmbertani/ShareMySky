import serial, config_gps_s4c

# costanti
DEVICE=config_gps_s4c.DEVICE
DIR_FILE=config_gps_s4c.DIR_FILE
STATION_NAME=config_gps_s4c.STATION_NAME
MAX_SAT=config_gps_s4c.MAX_SAT

# finestra cutoff
AZ_da=config_gps_s4c.AZ_da
AZ_a=config_gps_s4c.AZ_a
ALT_min=config_gps_s4c.ALT_min
ALT_max=config_gps_s4c.ALT_max



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
		

STATION_POS=str(int(float(s[3])))+s[4]+str(int(float(s[5])))+s[6]	
print ()
print("Start ",timesat_old," coordinate: ",lat,"-",lon,"\n")


# crea gli array vuoti
azsatvet=array (MAX_SAT)
altsatvet=array (MAX_SAT)
cn0satvet=array (MAX_SAT)

# crea gli array vuoti per le coordinate
lat=0
lon=0
alt=0
latv=[]
lonv=[]
altv=[]


while (True):
		
		# legge nmea0183 da seriale
		s=readgps()
		
		#legge il frame GGA per le coordinate
		if (s[0]=='$GPGGA'):
			lat= int((int(float(s[2])/100) + ( float(s[2])/100 - int(float(s[2])/100))*100/60) *1000000)/1000000
			if (s[3]=='S'):
				lat=-lat	
			lon=int((int(float(s[4])/100) + ( float(s[4])/100 - int(float(s[4])/100))*100/60) *1000000)/1000000
			if (s[5]=='W'):
				lon=-lon
			alt=float(s[9])
			latv=latv+[lat]
			lonv=lonv+[lon]
			altv=altv+[alt]
		
		
		
		# decodifica il codice nmea0182 GPRMC
		if (s[0]=='$GPRMC'):
			date=s[9][4:6]+s[9][2:4]+s[9][0:2]
			timesat=s[9][4:6]+s[9][2:4]+s[9][0:2]+s[1][:-5]
			hour=s[1][-9:-7]
			minute=s[1][-7:-5]
			second=s[1][-5:-3]
			
			
			# al secondo 00 esegue la statistica e logga i risultati
			if (second=="00"):
				
				# calcola e scrive il file della posizione
				latm=int(sum(latv)/len(latv)*1000000)/1000000
				lonm=int(sum(lonv)/len(lonv)*1000000)/1000000
				altm=int(sum(altv)/len(altv)*10)/10
				latv=[]
				lonv=[]
				altv=[]
				POSFILE=DIR_FILE+"sms_pos_"+STATION_NAME+".csv"
				f=open(POSFILE,"a")
				s=str(timesat_old)+","+str(latm)+","+str(lonm)+","+str(altm)+"\n"
				print (s)
				f.write (s)
				f.close()
				
				# calcolo delle coordinate medie e dell s4c del segnale per ogni satellite valido		
				for t in range (0,MAX_SAT):
					if (len(cn0satvet[t])>0):
						azmed=int(med(azsatvet[t])*10+0.5)/10
						altmed=int(med(altsatvet[t])*10+0.5)/10
						cn0med=int(med(cn0satvet[t])*10+0.5)/10
						cn0s4c=s4c(cn0satvet[t])
						
						cn0s=""
						if (cn0s4c>0.25):
							for x in range(int(cn0s4c/0.25)-1):
								cn0s=cn0s+"*"
						
						print (f'{timesat_old:6}  sat: {t:2}   az: {azmed:5}   alt: {altmed:4}   cn0: {cn0med:4}   s4c:{cn0s4c:5} {cn0s}')
						
						# esegue il log sul file giornaliero
						LOG_FILE=DIR_FILE+"sms_"+STATION_NAME+"_"+STATION_POS+"_"+timesat_old[:6]+".csv"
						f=open(LOG_FILE,"a")
						s1=str(timesat_old)+","+str(t)+","+str(azmed)+","+str(altmed)+","+str(cn0med)+","+str(cn0s4c)+"\n"
						f.write (s1)
						f.close()
						
						# esegue il log sul file dei topevent
						if (cn0s4c>0.5):
							LOG_FILE=DIR_FILE+"sms_"+STATION_NAME+"_"+STATION_POS+"_topevent.csv"
							f=open(LOG_FILE,"a")
							f.write (s1)
							f.close()
							
				print ()
				# vuota gli array
				azsatvet=array (MAX_SAT)
				altsatvet=array (MAX_SAT)
				cn0satvet=array (MAX_SAT)
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
				if ((cutoffarea==True) and (idsat<MAX_SAT)):
					azsatvet[idsat]=azsatvet[idsat]+[azsat]
					altsatvet[idsat]=altsatvet[idsat]+[altsat]
					cn0satvet[idsat]=cn0satvet[idsat]+[cn0sat]	
			
ser.close()


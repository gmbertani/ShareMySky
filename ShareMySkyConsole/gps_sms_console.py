"""
This program acquires GPS data from a serial port and saves it to a CSV file.

Copyright (C) 2024 Thomas Mazzi, Giuseppe Massimo Bertani

This program is distributed under the GNU General Public License version 3.0.
For more information, see the LICENSE file or visit https://www.gnu.org/licenses/gpl-3.0.html
"""

import serial
import argparse
import sys
from pathlib import Path


def parse_arguments():
    """
    Gestisce i parametri da linea di comando.
    """
    parser = argparse.ArgumentParser(description="Acquisisce dati GPS da porta seriale e li salva in un file CSV per "
                                                 "le finalità del progetto Share My Sky")

    # Parametri obbligatori
    parser.add_argument("station", type=str,
                        help="Nome da assegnare a questa stazione")
    parser.add_argument("serial_port", type=str, help="Nome della porta seriale a cui è collegato il GPS (es: COM1, "
                                                      "/dev/ttyACM0)")
    parser.add_argument("azimuth_cutoff", type=str,
                        help="Intervallo di azimut per il cutoff (es: 315-45, 45-280)")
    parser.add_argument("elevation_cutoff", type=str,
                        help="Intervallo di elevazione per il cutoff (es: 20-80)")

    # Parametri opzionali
    parser.add_argument("--csv_path", type=str, default=Path.home(),
                        help=f"Percorso del file CSV dove verranno registrati i dati raccolti da GPS (default: {Path.home()})")

    parser.add_argument("--max_sats", type=str, default=33,
                        help=f"Massimo numero di satelliti da considerare, default 33")
    parser.add_argument("--silent", action="store_true", default=False,
                        help="Se specificato, disabilita la stampa dei dati sulla console")
    # parser.add_argument("--window", type=int, default=60,
    # help="Lunghezza della finestra dati per il calcolo di s4c (default: 60)")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()


def parse_cutoff_interval(interval_str, max_value):
    if interval_str is None:
        return 0, max_value

    try:
        start, end = map(int, interval_str.split('-'))
        if start < 0 or end < 0 or start > max_value or end > max_value:
            raise ValueError("Angoli non validi")

        return start, end
    except ValueError as e:
        print(f"Errore nell'intervallo di cutoff: {e}")
        sys.exit(1)


def is_within_cutoff(azimuth, elevation, azimuth_start, azimuth_end, elevation_start, elevation_end):
    if not (azimuth_start == 0 and azimuth_end == 360):
        if azimuth_start < azimuth_end:
            if not (azimuth_start <= azimuth <= azimuth_end):
                return False
        else:
            if not (azimuth_start <= azimuth or azimuth <= azimuth_end):
                return False

    if not (elevation_start == 0 and elevation_end == 90):
        if not (elevation_start <= elevation <= elevation_end):
            return False

    return True


# calcolo media di un vettore
def med(a):
    x = 0
    if len(a) > 0:
        x = sum(a) / len(a)
    return x


# calcolo s4c partendo da vettore cn0 in db
def s4c(a):
    x = 0
    k = []
    j = []
    for t in a:
        i = 10 ** (t / 10)
        k = k + [i ** 2]
        j = j + [i]
    k = med(k)
    j = med(j) ** 2
    if (j > 0) and (k >= j):
        x = ((k - j) / j) ** 0.5
        x = int(x * 100 + 0.5) / 100
    return x


# crea array di array vuoti di n elementi
def array(n):
    x = []
    for t in range(0, n):
        x = x + [[]]
    return x


# legge i dati dall'antenna
def readgps(ser):
    s = str(ser.readline().decode("utf-8"))

    # calcola il checksum
    payload_start = s.find('$') + 1  # trova il primo carattere dopo $
    payload_end = s.find('*')  # trova il carattere *
    payload = s[payload_start: payload_end]  # dati di cui fare XOR
    ck = 0
    for ch in payload:  # ciclo di calcolo del checksum
        ck = ck ^ ord(ch)  # XOR
    str_ck = '%02X' % ck  # trasforma il valore calcolato in una stringa di 2 caratteri

    # controlla checksum
    if s[-4:-2] != str_ck:
        s = "$ERR"

    # decodifica stringa GPS
    s = s[:-5].split(',')
    for t in range(len(s)):
        if s[t] == '':
            s[t] = '0'
    return s


def main():
    args = parse_arguments()

    azimuth_start, azimuth_end = parse_cutoff_interval(args.azimuth_cutoff, 360)
    elevation_start, elevation_end = parse_cutoff_interval(args.elevation_cutoff, 90)

    try:
        ser = serial.Serial(args.serial_port, baudrate=9600, timeout=1)
        ser.reset_input_buffer()  # era flushInput()

    except serial.SerialException as e:
        print(f"Errore apertura porta seriale: {e}")
        sys.exit(1)

    # sincronizza la partenza al secondo 00
    lat = ""
    lon = ""
    timesat_old = ""
    second = ""
    print("--- SHARE MY SKY ---\n")
    print("Attesa sincronizzazione...")

    while second != "00":
        try:
            s = readgps(ser)
            if s[0] == '$GPTXT':
                print(s[4])

            # decodifica il codice nmea0183 GPRMC per avere latitudine longitudine e l'orario gps
            if s[0] == '$GPRMC':
                timesat_old = s[9][4:6] + s[9][2:4] + s[9][0:2] + s[1][:-5]
                if len(s[1]) == 6:
                    # orario senza millisecondi, per dispositivi vecchi
                    second = s[1][4:6]
                else:
                    second = s[1][-5:-3]

                lat = str(int(float(s[3])) / 100) + " " + s[4]
                lon = str(int(float(s[5])) / 100) + " " + s[6]

            print('.', end='')

        except KeyboardInterrupt:
            print("Interruzione da tastiera.")
            ser.close()
            print("Programma terminato.")
            return

    print("\n\nDati ricevitore:")
    print("\nStart ", timesat_old, " coordinate: ", lat, "-", lon, "\n")

    azsatvet = array(args.max_sats)
    altsatvet = array(args.max_sats)
    cn0satvet = array(args.max_sats)

    while True:
        try:
            s = readgps(ser)

            # decodifica il codice nmea0183 GPRMC
            if s[0] == '$GPRMC':
                date = s[9][4:6] + s[9][2:4] + s[9][0:2]
                timesat = s[9][4:6] + s[9][2:4] + s[9][0:2] + s[1][:-5]
                if len(s[1]) == 6:
                    # orario senza millisecondi, per dispositivi vecchi
                    second = s[1][4:6]
                else:
                    second = s[1][-5:-3]

                # al secondo 00 esegue la statistica e logga i risultati
                if second == "00":
                    # calcolo delle coordinate medie e dell sqm del segnale per ogni satellite valido
                    for t in range(0, args.max_sats):
                        if len(cn0satvet[t]) > 0:
                            azmed = int(med(azsatvet[t]) * 10 + 0.5) / 10
                            altmed = int(med(altsatvet[t]) * 10 + 0.5) / 10
                            cn0med = int(med(cn0satvet[t]) * 10 + 0.5) / 10
                            cn0s4c = s4c(cn0satvet[t])
                            cn0s = ""
                            for x in range(int(cn0s4c / 0.333)):
                                cn0s = cn0s + "*"

                            if not args.silent:
                                print(
                                    f'{timesat_old:6}  sat: {t:2}   az: {azmed:5}   alt: {altmed:4}   cn0: {cn0med:4}   s4c:{cn0s4c:5} {cn0s}')

                            logname = "gps_" + args.station + "_" + date + ".csv"
                            logfile = args.csv_path / Path(logname)
                            f = open(logfile, "a")
                            s1 = str(timesat_old) + "," + str(t) + "," + str(azmed) + "," + str(
                                altmed) + "," + str(cn0med) + "," + str(cn0s4c) + "\n"
                            f.write(s1)
                            f.close()

                    # vuota gli array
                    azsatvet = array(args.max_sats)
                    altsatvet = array(args.max_sats)
                    cn0satvet = array(args.max_sats)
                    timesat_old = timesat

            # decodifica il codice nmea0183 GPGSV
            elif s[0] == '$GPGSV':
                sat_data = s[4:]
                for i in range(0, len(sat_data), 4):
                    try:
                        idsat = int(sat_data[i])
                        altsat = int(sat_data[i + 1])
                        azsat = int(sat_data[i + 2])
                        cn0sat = int(sat_data[i + 3])

                        # calcola la finestra di cutoff
                        if is_within_cutoff(azsat, altsat, azimuth_start, azimuth_end, elevation_start,
                                            elevation_end):
                            if idsat < args.max_sats:
                                azsatvet[idsat] = azsatvet[idsat] + [azsat]
                                altsatvet[idsat] = altsatvet[idsat] + [altsat]
                                cn0satvet[idsat] = cn0satvet[idsat] + [cn0sat]
                    except (ValueError, IndexError):
                        pass
        except KeyboardInterrupt:
            print("Interruzione da tastiera.")
            break

    ser.close()
    print("Programma terminato.")


if __name__ == "__main__":
    main()

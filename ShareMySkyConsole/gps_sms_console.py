"""
This program acquires GPS data from a serial port and saves it to a CSV file.

Copyright (C) 2024 Thomas Mazzi, Giuseppe Massimo Bertani

This program is distributed under the GNU General Public License version 3.0.
For more information, see the LICENSE file or visit https://www.gnu.org/licenses/gpl-3.0.html
"""


import serial
import argparse
import os
import sys


def parse_arguments():
    """
    Gestisce i parametri da linea di comando.
    """
    parser = argparse.ArgumentParser(description="Acquisisce dati GPS da porta seriale e li salva in un file CSV per "
                                                 "le finalità del progetto Share My Sky")

    # Parametri obbligatori
    parser.add_argument("serial_port", type=str, help="Nome della porta seriale a cui è collegato il GPS (es: COM1, "
                                                      "/dev/ttyACM0)")

    # Parametri opzionali
    default_csv_file = os.path.join(os.path.expanduser("~"), "gps.csv")
    parser.add_argument("--csv_file", type=str, default=default_csv_file,
                        help="Percorso del file CSV dove verranno registrati i dati raccolti da GPS (default: {})".format(default_csv_file))
    parser.add_argument("--azimuth_cutoff", type=str,
                        help="Intervallo di azimut per il cutoff (es: 315-45, 45-280)")
    parser.add_argument("--elevation_cutoff", type=str,
                        help="Intervallo di elevazione per il cutoff (es: 20-80)")
    parser.add_argument("--silent", action="store_true", help="Disabilita la stampa dei dati sulla console")

    # Se vengono forniti zero parametri, viene stampata la schermata di aiuto
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()


def parse_cutoff_interval(interval_str, max_value):
    """
    Converte una stringa di intervallo in due valori numerici.
    """
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
    """
    Verifica se un punto è all'interno degli intervalli di cutoff.
    """
    if not (azimuth_start == 0 and azimuth_end == 360):  # se non è stato specificato nessun azimut
        if azimuth_start < azimuth_end:
            if not (azimuth_start <= azimuth <= azimuth_end):
                return False
        else:  # se l'intervallo di azimut include lo zero (es. 315-45)
            if not (azimuth_start <= azimuth or azimuth <= azimuth_end):
                return False

    if not (elevation_start == 0 and elevation_end == 90):  # se non è stato specificato nessun azimut
        if not (elevation_start <= elevation <= elevation_end):
            return False

    return True


def main():
    """
    Funzione principale del programma.
    """
    args = parse_arguments()

    azimuth_start, azimuth_end = parse_cutoff_interval(args.azimuth_cutoff, 360)
    elevation_start, elevation_end = parse_cutoff_interval(args.elevation_cutoff, 90)

    try:
        ser = serial.Serial(args.serial_port, baudrate=9600, timeout=1)
    except serial.SerialException as e:
        print(f"Errore apertura porta seriale: {e}")
        sys.exit(1)

    print(f"File CSV: {args.csv_file}")
    print(f"Porta seriale: {args.serial_port}")
    print(f"Silent mode: {args.silent}")

    try:
        with open(args.csv_file, "a") as f:
            while True:
                try:
                    line = ser.readline().decode("utf-8").strip()
                    parts = line.split(',')

                    # Elaborazione frase $GPRMC (dati di posizione)
                    if parts[0] == '$GPRMC':
                        time_str = parts[9][4:6] + parts[9][2:4] + parts[9][0:2] + parts[1][:-3]
                        lat = int((int(float(parts[3]) / 100) + (
                                    float(parts[3]) / 100 - int(float(parts[3]) / 100)) * 100 / 60) * 1000000) / 1000000
                        if parts[4] == 'S':
                            lat = -lat
                        lon = int((int(float(parts[5]) / 100) + (
                                    float(parts[5]) / 100 - int(float(parts[5]) / 100)) * 100 / 60) * 1000000) / 1000000
                        if parts[6] == 'W':
                            lon = -lon

                    # Elaborazione frase $GPGSV (dati satelliti)
                    elif parts[0] == '$GPGSV':
                        num_satellites = int(parts[3])
                        msg_num = int(parts[1])
                        total_msgs = int(parts[2])
                        sat_data = parts[4:]

                        # Itera sui dati dei satelliti
                        for i in range(0, len(sat_data), 4):
                            try:
                                sat_id = int(sat_data[i])
                                elevation = int(sat_data[i + 1])
                                azimuth = int(sat_data[i + 2])
                                snr = int(sat_data[i + 3])

                                # Verifica se il satellite è all'interno degli intervalli di cutoff
                                if is_within_cutoff(azimuth, elevation, azimuth_start, azimuth_end, elevation_start,
                                                    elevation_end):
                                    if not args.silent:
                                        print(
                                            f"Satellite: {sat_id}, Azimuth: {azimuth}, Elevation: {elevation}, SNR: {snr}")
                                    f.write(f"{time_str},{sat_id},{azimuth},{elevation},{snr}\n")

                            except (ValueError, IndexError):
                                pass  # Ignora dati non validi

                except KeyboardInterrupt:
                    print("Interruzione da tastiera.")
                    break

    except Exception as e:
        print(f"Errore durante l'elaborazione dei dati: {e}")

    finally:
        ser.close()
        print("Programma terminato.")


if __name__ == "__main__":
    main()

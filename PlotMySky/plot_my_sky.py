import pandas as pd
import matplotlib.pyplot as plt
import argparse
from tqdm.auto import tqdm
import matplotlib.dates as mdates
import os
from matplotlib.widgets import Cursor


def plot_snr_vs_time(file_path, azimut_range=None, elevation_range=None, idsat_list=None, max_sats=None):
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Errore: File '{file_path}' non trovato.")
        return

    # Rileva il formato del file (GABB o AAC)
    if 'timestamp' in df.columns:
        print("Formato file: GABB")
        # Formatta i timestamp come stringhe nel formato desiderato
        df['timestamp'] = df['timestamp'].astype(str).str.replace('T', ' ').str.replace('Z', '')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    elif 'date' in df.columns:
        print("Formato file: AAC")
        df = df.rename(columns={'date': 'timestamp', 'lat': 'latitude', 'lon': 'longitude',
                                'arsat': 'azimuth', 'decsat': 'elevation', 'cn0': 'snr'})
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%y%m%d%H%M%S')
    else:
        print("Errore: Formato file CSV non riconosciuto.")
        return

    print("Inizio filtraggio dati:")

    # 1. Filtra per azimut ed elevazione
    if azimut_range is not None:
        df = df[(df['azimuth'] >= azimut_range[0]) & (df['azimuth'] <= azimut_range[1])]
    if elevation_range is not None:
        df = df[(df['elevation'] >= elevation_range[0]) & (df['elevation'] <= elevation_range[1])]

    # 2. Filtra per max_sats (se specificato)
    if max_sats:
        sat_counts = df['idsat'].value_counts()
        top_sats = sat_counts.nlargest(max_sats).index.tolist()
        df = df[df['idsat'].isin(top_sats)]
        print(f"IDSAT considerati (max_sats = {max_sats}): {top_sats}")

    # 3. Filtra per idsat_list (se specificato)
    if idsat_list:
        df = df[df['idsat'].isin(idsat_list)]
        print(f"IDSAT considerati (da linea di comando): {idsat_list}")

    # 4. Prepara i dati per il plot e salva il file CSV filtrato
    if 'timestamp' in df.columns:
        # Rimuovi l'informazione del fuso orario, conversione in datetime
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
        df = df.sort_values('timestamp')
        df = df.reset_index(drop=True)
        # Converti i timestamp in numeri di date di Matplotlib
        df['time_num'] = mdates.date2num(df['timestamp'])

        # Salva il file CSV filtrato
        base_filename = os.path.splitext(os.path.basename(file_path))[0]
        output_filename = f"{base_filename}_filtered.csv"
        df.to_csv(output_filename, index=False)
        print(f"File filtrato salvato come: {output_filename}")

        # 5. Plotta i risultati
        if df['idsat'].nunique() > 0:
            fig, ax = plt.subplots(figsize=(12, 6))
            colors = plt.cm.get_cmap('tab10', df['idsat'].nunique())
            lines = []
            for i, idsat in enumerate(df['idsat'].unique()):
                df_idsat = df[df['idsat'] == idsat]
                line, = ax.plot(df_idsat['time_num'], df_idsat['snr'], marker='', linestyle='-', color=colors(i),
                                label=f'IDSAT {idsat}')
                lines.append(line)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

            # Aggiungi il cursore
            cursor = Cursor(ax, useblit=True, color='red', linewidth=1)

            # Aggiungi l'annotazione per il tooltip
            annot = ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                                bbox=dict(boxstyle="round", fc="w"),
                                arrowprops=dict(arrowstyle="->"))
            annot.set_visible(False)

            def hover(event):
                if event.inaxes == ax:
                    for line in lines:
                        cont, ind = line.contains(event)
                        if cont:
                            x, y = line.get_data()
                            idsat = line.get_label().split(' ')[1]
                            annot.xy = (x[ind['ind'][0]], y[ind['ind'][0]])
                            annot.set_text(f"IDSAT: {idsat}")
                            annot.set_visible(True)
                            fig.canvas.draw_idle()
                            return
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

            fig.canvas.mpl_connect("motion_notify_event", hover)

        else:
            print("Nessun dato da plottare dopo i filtri.")
    else:
        print('Nessun dato con la colonna timestamp trovato dopo i filtri')
    ax.set_xlabel('Orario')
    ax.set_ylabel('SNR')

    # Aggiungi i filtri al titolo
    title = 'SNR nel tempo'
    if azimut_range:
        title += f', Azimut: {azimut_range[0]}-{azimut_range[1]}'
    if elevation_range:
        title += f', Elevazione: {elevation_range[0]}-{elevation_range[1]}'
    if max_sats:
        title += f', Max Sats: {max_sats}'
    if idsat_list:
        title += f', IDSAT: {idsat_list}'

    ax.set_title(title)

    # Usa AutoDateLocator con un formato più specifico
    locator = mdates.AutoDateLocator()
    formatter = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser(description='Genera un grafico dell\'SNR nel tempo da un file CSV.')
    parser.add_argument('file_path', type=str, help='Il percorso del file CSV.')
    parser.add_argument('--azimut_min', type=float, help='Il valore minimo di azimut.')
    parser.add_argument('--azimut_max', type=float, help='Il valore massimo di azimut.')
    parser.add_argument('--elevation_min', type=float, help='Il valore minimo di elevazione.')
    parser.add_argument('--elevation_max', type=float, help='Il valore massimo di elevazione.')
    parser.add_argument('--idsat', type=int, nargs='+', help='Lista di IDSAT da considerare.')
    parser.add_argument('--max_sats', type=int,
                        help='Numero massimo di satelliti da plottare (in base al numero di dati).')

    args = parser.parse_args()

    azimut_range = (
    args.azimut_min, args.azimut_max) if args.azimut_min is not None and args.azimut_max is not None else None
    elevation_range = (args.elevation_min,
                       args.elevation_max) if args.elevation_min is not None and args.elevation_max is not None else None
    idsat_list = args.idsat
    max_sats = args.max_sats

    plot_snr_vs_time(args.file_path, azimut_range, elevation_range, idsat_list, max_sats)


if __name__ == '__main__':
    main()

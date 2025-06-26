import pandas as pd
import matplotlib.pyplot as plt
import argparse
from tqdm.auto import tqdm
import matplotlib.dates as mdates
import os
from matplotlib.widgets import Cursor

try:
    import matplotlib.colormaps as cm
except ImportError:
    import matplotlib.cm as cm


def plot_snr_vs_time(file_path, azimut_range=None, elevation_range=None, idsat_list=None, max_sats=None,
                     hours_per_plot=24):
    try:
        df = pd.read_csv(file_path)
        if df.columns[0] != 'timestamp':
            # missing header, add a new one:
            print("This CSV has no header, applying a new one")
            dtypes = {'timestamp': str, 'idsat': int, 'azimuth': float, 'elevation': float, 'cn0': float,
                      's4c': float, 'time_num': float}
            cols = list(dtypes.keys())
            df = pd.read_csv(file_path, header=None, names=cols, dtype=dtypes)

    except FileNotFoundError:
        print(f"Errore: File '{file_path}' non trovato.")
        return

    if df['time_num'].isna().any() is not None:
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%y%m%d%H%M')


    print("Inizio filtraggio dati:")

    # 1. Filtra per azimut ed elevazione
    if azimut_range is not None:
        df = df[(df['azimuth'] >= azimut_range[0]) & (df['azimuth'] <= azimut_range[1])]
    if elevation_range is not None:
        df = df[(df['elevation'] >= elevation_range[0]) & (df['elevation'] <= elevation_range[1])]

    # 2. Filtra per args.max_sats (se specificato)
    if max_sats:
        sat_counts = df['idsat'].value_counts()
        top_sats = sat_counts.nlargest(max_sats).index.tolist()
        df = df[df['idsat'].isin(top_sats)]
        print(f"IDSAT considerati (args.max_sats = {max_sats}): {top_sats}")

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

        # Logica per suddividere i dati in blocchi di 'hours_per_plot' ore
        start_time = df['timestamp'].min()
        end_time = df['timestamp'].max()

        # Calcola il numero totale di ore coperte dai dati
        total_hours = (end_time - start_time).total_seconds() / 3600

        num_plots = int(total_hours / hours_per_plot)
        if total_hours % hours_per_plot != 0:
            num_plots += 1  # Se c'è un resto, aggiungi un altro plot per coprire i dati rimanenti

        print(
            f"I dati coprono {total_hours:.2f} ore. Verranno generati {num_plots} grafici da {hours_per_plot} ore ciascuno.")

        for i in range(num_plots):
            plot_start_time = start_time + pd.Timedelta(hours=i * hours_per_plot)
            plot_end_time = plot_start_time + pd.Timedelta(hours=hours_per_plot)

            df_plot = df[(df['timestamp'] >= plot_start_time) & (df['timestamp'] < plot_end_time)].copy()

            if df_plot['idsat'].nunique() > 0:
                fig, ax = plt.subplots(figsize=(12, 6))

                unique_idsats = df_plot['idsat'].unique()
                num_unique_idsats = len(unique_idsats)

                cmap = plt.colormaps.get_cmap('hsv')
                colors = [cmap(j / num_unique_idsats) for j in range(num_unique_idsats)]

                lines = []
                for j, idsat in enumerate(unique_idsats):
                    df_idsat = df_plot[df_plot['idsat'] == idsat]
                    line, = ax.plot(df_idsat['time_num'], df_idsat['cn0'], marker='', linestyle='-', color=colors[j],
                                    label=f'IDSAT {idsat}')
                    lines.append(line)

                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

                cursor = Cursor(ax, useblit=True, color='red', linewidth=1)

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
                print(f"Nessun dato da plottare per l'intervallo {plot_start_time} - {plot_end_time} dopo i filtri.")
                plt.close(fig)  # Chiudi la figura vuota
                continue  # Passa al prossimo intervallo

            ax.set_xlabel('Orario')
            ax.set_ylabel('cn0')

            title = f'cn0 nel tempo ({plot_start_time.strftime("%Y-%m-%d %H:%M")} a {plot_end_time.strftime("%Y-%m-%d %H:%M")})'
            if azimut_range:
                title += f', Azimut: {azimut_range[0]}-{azimut_range[1]}'
            if elevation_range:
                title += f', Elevazione: {elevation_range[0]}-{elevation_range[1]}'
            if max_sats:
                title += f', Max Sats: {max_sats}'
            if idsat_list:
                title += f', IDSAT: {idsat_list}'

            ax.set_title(title)

            locator = mdates.AutoDateLocator()
            formatter = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(formatter)

            plt.xticks(rotation=45)
            plt.grid(True)
            plt.tight_layout()

            # Salva il grafico con un nome che include l'indice del blocco
            png_filename = f"{base_filename}_part{i + 1}.png"
            plt.savefig(png_filename)
            print(f"Grafico salvato come: {png_filename}")

            plt.close(fig)  # Chiudi il grafico dopo averlo salvato

    else:
        print('Nessun dato con la colonna timestamp trovato dopo i filtri')


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
    parser.add_argument('--hours', type=int, default=24,
                        help='Numero di ore da plottare in ciascun grafico (default: 24).')

    args = parser.parse_args()

    azimut_range = (
        args.azimut_min, args.azimut_max) if args.azimut_min is not None and args.azimut_max is not None else None
    elevation_range = (args.elevation_min,
                       args.elevation_max) if args.elevation_min is not None and args.elevation_max is not None else None
    idsat_list = args.idsat
    max_sats = args.max_sats
    hours_per_plot = args.hours

    plot_snr_vs_time(args.file_path, azimut_range, elevation_range, idsat_list, max_sats, hours_per_plot)


if __name__ == '__main__':
    main()

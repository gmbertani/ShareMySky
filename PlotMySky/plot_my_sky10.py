import pandas as pd
import matplotlib.pyplot as plt
import argparse
from tqdm.auto import tqdm
import matplotlib.dates as mdates
import os
from matplotlib.widgets import Cursor
import numpy as np  # Importa numpy per gestire NaN

try:
    import matplotlib.colormaps as cm
except ImportError:
    import matplotlib.cm as cm


def plot_snr_vs_time(file_path, azimut_range=None, elevation_range=None, idsat_list=None, max_sats=None,
                     hours_per_plot=24, cn0_mask=None):  # Aggiunto cn0_mask
    # Definisci i tipi di dato e i nomi delle colonne desiderati
    desired_dtypes = {
        'timestamp_col': str,
        'idsat_col': int,
        'azimuth_col': float,
        'elevation_col': float,
        'cn0_col': float,
        's4c_col': float
    }
    temp_col_names = ['timestamp_col', 'idsat_col', 'azimuth_col', 'elevation_col', 'cn0_col', 's4c_col']

    df = None
    try:
        # Tenta di leggere il file assumendo che ci sia un'intestazione
        print("Tento di leggere il file con intestazione...")
        temp_df = pd.read_csv(file_path)

        # Check if the first column name matches 'timestamp' after initial read
        if temp_df.columns[0] == 'timestamp':
            # It seems to have a header with expected names
            # Directly use the read df, but then rename for consistency with desired_dtypes
            print("File letto con intestazione 'timestamp'. Applico i tipi.")
            # Map column names if they are different from temp_col_names but order is same
            current_col_map = {old_name: new_name for old_name, new_name in zip(temp_df.columns, temp_col_names)}
            temp_df.rename(columns=current_col_map, inplace=True)
            df = temp_df
        else:
            # If the first column is not 'timestamp', it might be missing header or different header
            print("La prima colonna non è 'timestamp'. Ritento senza intestazione.")
            raise ValueError("First column mismatch, retrying without header.")

    except Exception as e:
        print(f"Errore nella lettura con intestazione o mismatch colonne ({e}). Ritento senza intestazione...")
        # Se fallisce, tenta di leggere il file assumendo che non ci sia intestazione
        try:
            df = pd.read_csv(file_path, header=None, names=temp_col_names)
            print("File letto senza intestazione. Colonne assegnate.")
        except Exception as e_no_header:
            print(f"Errore anche nella lettura senza intestazione: {e_no_header}")
            print(f"Errore: Impossibile leggere il file '{file_path}' correttamente.")
            return

    if df is None:
        print(f"Errore: Impossibile leggere il file '{file_path}'.")
        return

    # Applica i tipi di dato definiti, gestendo gli errori per 'idsat' in caso di valori non numerici
    for col, dtype in desired_dtypes.items():
        if col in df.columns:
            if col == 'idsat_col':
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
            else:
                df[col] = df[col].astype(dtype, errors='ignore')

    # Rimuovi eventuali righe dove 'idsat_col' è diventato NaN a causa di errori di conversione
    df.dropna(subset=['idsat_col'], inplace=True)

    # Rinomina le colonne ai nomi finali più brevi e puliti
    df.rename(columns={
        'timestamp_col': 'timestamp',
        'idsat_col': 'idsat',
        'azimuth_col': 'azimuth',
        'elevation_col': 'elevation',
        'cn0_col': 'cn0',
        's4c_col': 's4c'
    }, inplace=True)

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

    # NUOVA FUNZIONALITÀ: Filtro per cn0_mask
    if cn0_mask is not None:
        initial_rows = len(df)
        df = df[df['cn0'] > cn0_mask]
        print(f"Filtrato CN0: rimosse {initial_rows - len(df)} righe con CN0 <= {cn0_mask}.")

    # 4. Prepara i dati per il plot e salva il file CSV filtrato
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
        df = df.sort_values('timestamp')
        df = df.reset_index(drop=True)
        df['time_num'] = mdates.date2num(df['timestamp'])

        base_filename = os.path.splitext(os.path.basename(file_path))[0]
        output_filename = f"{base_filename}_filtered.csv"
        df.to_csv(output_filename, index=False)
        print(f"File filtrato salvato come: {output_filename}")

        start_time = df['timestamp'].min()
        end_time = df['timestamp'].max()

        total_hours = (end_time - start_time).total_seconds() / 3600
        num_plots = int(total_hours / hours_per_plot)
        if total_hours % hours_per_plot != 0:
            num_plots += 1

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

                # NUOVA FUNZIONALITÀ: Linea nera tratteggiata per i massimi CN0
                # Raggruppa per time_num e trova il CN0 massimo per ogni punto temporale
                max_cn0_per_time = df_plot.groupby('time_num')['cn0'].max().reset_index()
                ax.plot(max_cn0_per_time['time_num'], max_cn0_per_time['cn0'],
                        color='black', linestyle='--', label='Max CN0')
                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')  # Aggiorna la legenda

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
                plt.close(fig)
                continue

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
            if cn0_mask is not None:
                title += f', CN0 > {cn0_mask}'  # Aggiunto al titolo

            ax.set_title(title)

            locator = mdates.AutoDateLocator()
            formatter = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(formatter)

            plt.xticks(rotation=45)
            plt.grid(True)
            plt.tight_layout()

            png_filename = f"{base_filename}_part{i + 1}.png"
            plt.savefig(png_filename)
            print(f"Grafico salvato come: {png_filename}")

            plt.close(fig)

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
    parser.add_argument('--mask', type=float,
                        help='Valore CN0 minimo. Ignora i valori di CN0 inferiori o uguali a N.')  # NUOVO ARGOMENTO

    args = parser.parse_args()

    azimut_range = (
        args.azimut_min, args.azimut_max) if args.azimut_min is not None and args.azimut_max is not None else None
    elevation_range = (args.elevation_min,
                       args.elevation_max) if args.elevation_min is not None and args.elevation_max is not None else None
    idsat_list = args.idsat
    max_sats = args.max_sats
    hours_per_plot = args.hours
    cn0_mask = args.mask  # Recupera il valore della maschera

    plot_snr_vs_time(args.file_path, azimut_range, elevation_range, idsat_list, max_sats, hours_per_plot, cn0_mask)


if __name__ == '__main__':
    main()
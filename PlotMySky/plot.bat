call .venv\Scripts\activate.bat
del *.png
rem i satelliti da considerare vanno da 1 a 32 eccetto il 21 che è guasto (Tom)
python plot_my_sky10.py --idsat 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 22 23 24 25 26 27 28 29 30 31 32  --azimut_min 100 --azimut_max 260 --elevation_min 30 --elevation_max 90  --hours 2  share_my_sky-BENDER.csv
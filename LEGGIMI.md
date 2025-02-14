
# ShareMySky
## Introduzione 
Immaginate di essere in una città sconosciuta senza una mappa o di aver 
bisogno di soccorso. Sarebbe difficile orientarsi o dare indicazioni sul luogo, 
giusto? Il GPS (Global Positioning System) è un po' come una bussola super 
potente che ci indica sempre la strada giusta, in qualsiasi parte del mondo ci 
troviamo. Grazie ad una rete di satelliti che orbitano attorno alla Terra, il GPS 
ci  permette  di  conoscere  la  nostra  posizione  esatta in  ogni  momento… o 
quasi. Questo sistema ha rivoluzionato il nostro modo di vivere. Pensiamo 
agli smartphone: grazie al GPS possiamo usare le mappe per raggiungere una 
destinazione,  condividere  la  nostra  posizione  con  gli  amici  o  trovare  il 
ristorante  più  vicino  ma  le  applicazioni  del  GPS  vanno  ben  oltre:  dalla 
navigazione  marittima  e  aerea  alla  logistica,  dall'agricoltura  alla  ricerca 
scientifica fino alle richieste di soccorso come capita ogni tanto di vedere in 
montagna. Insomma, il GPS è diventato uno strumento indispensabile nella 
nostra  vita  quotidiana!  Uno  strumento  importante  anche  nell’ambito  del 
soccorso tempestivo. 
Il  GPS  è  un  po'  come  un  sistema  di  triangolazione  spaziale  che  funziona 
misurando  la  distanza  in  tempo  dai  satelliti  sopra  le  nostre  teste.  Lo 
smartphone o navigatore riceve questi segnali e, calcolando il tempo che 
hanno  impiegato  per  arrivare,  determina  la  posizione  con  estrema 
precisione. 
Tra i satelliti e il ricevitore non c’è il vuoto, anzi il percorso del segnale è 
alquanto  accidentato!  Uno  degli  ostacoli  maggiori  che  il  segnale  deve 
superare è la ionosfera terrestre, uno strato di gas rarefatto e ionizzato che 
appartiene alla nostra atmosfera (dai 60 km di altezza fino ai 700km). Questo 
strato è in continua evoluzione e viene tenuto eccitato dai raggi del Sole, dai 
brillamenti e dagli eventi di space weather. I segnali trasmessi dai satelliti 
vengono deviati dagli elettroni liberi aumentando il tempo di volo e falsando 
i calcoli del GPS. In oltre gli eventi di space weather agiscono come super 
eccitanti  della  ionosfera  modificandola  in  maniera  imprevedibile  e 
aumentandone  l’assorbimento  oltre  che  gli  effetti  di  scattering.  A  questi 
vanno aggiunti altri effetti della fisica dei gas che perturbano la forma e lo 
spessore della ionosfera. 
Tutto  questo  significa  errori  di  posizionamento  del  gps  e  mancanza  di 
sicurezza. 
 
## L’obbiettivo 
Del segnale GPS si conosce tutto in ogni momento, è tutto ben descritto nelle 
specifiche.  È  quindi  possibile  ricevere  un  segnale  GPS  da  un  satellite  e 
comparare questo con quanto ci si aspetta. La differenza tra il segnale atteso 
e  il  ricevuto,  se  il  satellite  è  a  portata  ottica  (in  vista),  è  attribuibile 
principalmente  allo  stato eccitato  della ionosfera.  Gli  errori  introdotti  nel 
calcolo  della  posizione  e  i  rapporti  Carry/Noise  (SNR  normalizzato  per 
l’ampiezza  di  banda)  ricevuti  dai  satelliti,  possono  essere  utilizzati  per 
studiare la ionosfera e i suoi effetti, cercando di capire di più su come questi 
agiscono,  sulle  correlazioni  che  hanno  con  lo  space  weather,  insomma 
comprendere meglio questo magico mondo, con il doppio obiettivo di poter 
capire di piu sullo space weather e contribuire al miglioramento del sistema 
GPS. 
 
## L’esperimento 
Per  poter  raggiungere  l’obiettivo  sopra  descritto,  l’idea  sarebbe  di 
coinvolgere in primis le associazioni e le persone, ma per fare questo si deve 
poter eseguire delle misure a costi contenuti, con spazi ridotti, accessibili a 
tutti, ben supportate in termini di strumenti sw e soprattutto robusti e privi 
di manutenzione. 
Lo strumento individuato è una piccola antenna GPS (dotata di chip UBLOX 
7020) nata per applicazioni automotive e nautiche, resistente all’acqua e alle 
intemperie  (una  piccola  scatola  protezione  non  guasta  comunque)  delle 
dimensioni  di  5x4x2  cm  da  posizionare  all’esterno  secondo  le  proprie 
possibilità di cielo visibile (non tutti hanno il cielo perfettamente aperto). 
Il costo dell’antenna è inferiore ai 20 euro alla quale bisogna aggiungere un 
eventuale cavo di prolunga usb del costo di pochi euro e un computer (anche 
datato)  collegato  ad  internet  con  sistema  LINUX  (potrebbe  andare  bene 
anche un raspberry). 
Ogni stazione ricevente, dipendentemente dalle proprie disponibilità di cielo 
e di tempo secondo la propria finestra di cutoff, raccoglie dati sui segnali 
ricevuti dai satelliti e gli invia ad un server dove vengono tutti convogliati. 
In questa maniera, gli utenti possono scaricare i dati anche di altre stazioni 
riceventi e vedere: 
1.  cosa è successo ai segnali di diverse stazioni in correlazione ad eventi 
2.  fare statistiche 
3.  modellare  la  ionosfera  avendo  disponibile  più  punti  di  vista  in 
contemporanea 
4.  generare sw da condividere che permetta di fare studi su questi dati 
Il sistema GPS è coordinato da orologi atomici e la correlazione dei dati è 
particolarmente precisa. 
Il programma di acquisizione è già stato sviluppato in python e in questo 
momento  sta  girando  su  un  pc  datato.  Ovviamente  in  questa  fase 
sperimentale,  gira  in  locale  (essendoci  solo  una  stazione)  ma  i  dati 
interessanti non sono tardati ad arrivare. Nel grafico sotto si vede il momento 
in cui la ionosfera ha disturbato il segnale. Purtroppo, non è ancora chiaro il 
motivo  di  questi  picchi  inattesi,  in  quel  momento  non  erano  presenti 
particolari eventi di space weather. C’è un mondo da scoprire e noi come 
associazioni a target scientifico astronomico potremmo fare la nostra parte. 
Il sw genera dei file di testo di circa 20MB giornalieri da poter utilizzare anche 
con un semplice excel o con un più evoluto matlab o python. La scelta del 
sistema dipende dall’utente che una volta sviluppato il sw può condividerlo 
con altri. 
 
## In Conclusione 
Se si vuole partecipare a questo esperimento è necessario avere: 
1.  un  posto  con  un  minimo  di  cielo  disponibile,  va  bene  anche  una 
finestra in città 
2.  un accesso a internet 
3.  essere capaci di usare un computer 
4.  avere  un  minimo  di  disponibilità  economica  per  l’acquisto  del 
sistema 
5.  voglia, voglia e voglia di indagare su questi argomenti 
 
   
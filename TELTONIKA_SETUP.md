# Configurazione dispositivi Teltonika

## Protocolli supportati
- CODEC 8 (FMB series, TFT series)
- CODEC 8 Extended (FMB125, FMB640, TAT100, ecc.)

## Configurazione dispositivo via Teltonika Configurator

### Parametri di connessione
1. Aprire **Teltonika Configurator**
2. Navigare su `GPRS > Main`
3. Impostare:
   - **APN**: APN del tuo operatore
   - **Domain**: IP/hostname del server fleet (es. `fleet.tuodominio.it`)
   - **Port**: `5027`
   - **Protocol**: TCP

### Invio dati (Data Acquisition)
Configurare in `Data Acquisition > On Stop`:
- **Min Saved Records**: 1
- **Send Period**: 30 (secondi)

Configurare in `Data Acquisition > On Move`:
- **Min Saved Records**: 1
- **Send Period**: 10 (secondi)

## Registrazione IMEI
Ogni dispositivo deve essere registrato nel sistema prima di poter inviare dati.

1. Aprire **Fleet Manager** → **Gestione Flotta**
2. Cliccare **Aggiungi veicolo**
3. Inserire il campo **IMEI Teltonika** (15 cifre, visibile nell'etichetta del dispositivo)

Il server TCP accetta connessioni solo da IMEI registrati.

## Porte da aprire nel firewall
| Porta | Protocollo | Descrizione |
|-------|-----------|-------------|
| 5027  | TCP       | Dati Teltonika (CODEC 8/8E) |
| 8000  | TCP       | API REST / WebSocket |
| 3000  | TCP       | Frontend web |

## IO Element ID notevoli (FMB series)
| ID  | Nome           | Descrizione |
|-----|----------------|-------------|
| 21  | GSM Signal     | Segnale GSM (0-5) |
| 66  | External Voltage | Tensione batteria esterna (mV) |
| 199 | Trip Odometer  | Odometro viaggio (m) |
| 239 | Ignition       | Stato accensione (0/1) |
| 240 | Movement       | Rilevamento movimento (0/1) |
| 241 | Active GSM Operator | Operatore attivo |

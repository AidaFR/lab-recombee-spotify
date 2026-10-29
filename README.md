# Laborator 2 – Sistem de recomandare cu Recombee: înregistrarea proprietăților

## Domeniul ales

**Muzică** – cele mai ascultate piese pe Spotify din 2023

Sistemul de recomandare va sugera piese muzicale
pe baza artistului, a perioadei de lansare, a popularității și a caracteristicilor audio
(ritm, energie, cât de dansabilă și cât de veselă este piesa). De exemplu, unui utilizator
care ascultă piese energice i se pot recomanda alte piese cu valori apropiate
la `energy` și `danceability`.

## Dataset

- **Sursă:** [Most Streamed Spotify Songs 2023 – Kaggle](https://www.kaggle.com/datasets/nelgiriyewithana/top-spotify-songs-2023)
- **Fișier original:** `spotify-2023.csv` – 953 de piese, 24 de coloane
- **Fișier folosit în Recombee:** `spotify_songs_clean.csv` – **948 de piese**, 9 coloane
  (identificatorul `item_id` + 8 proprietăți)

## Proprietățile înregistrate în Recombee

| Proprietate | Tip Recombee | Coloana din fișierul original | Descriere |
|---|---|---|---|
| `track_name` | `string` | `track_name` | numele piesei |
| `artist_name` | `string` | `artist(s)_name` | artistul sau artiștii |
| `release_date` | `timestamp` | `released_year` + `released_month` + `released_day` | data lansării piesei |
| `streams` | `int` | `streams` | numărul total de ascultări pe Spotify |
| `bpm` | `int` | `bpm` | ritmul piesei |
| `danceability` | `int` | `danceability_%` | cât de potrivită este pentru dans (0–100) |
| `energy` | `int` | `energy_%` | intensitatea și energia piesei (0–100) |
| `valence` | `int` | `valence_%` | starea transmisă: 0 = tristă, 100 = veselă |

Coloana `item_id` este identificatorul unic al fiecărei piese.
Ea **nu** este înregistrată ca proprietate.

## Pregătirea datelor (`prepare_dataset.py`)

1. Fișierul original este citit cu codarea **Latin-1** (nu este salvat în UTF-8).
2. Este eliminat **1 rând invalid** („Love Grows (Where My Rosemary Goes)”), care avea text
   în loc de număr în coloana `streams`.
3. Sunt eliminate **4 piese duplicate** (același titlu și același artist): SNAP,
   About Damn Time, Take My Breath, SPIT IN MY FACE!.
4. Coloanele `released_year`, `released_month`, `released_day` sunt unite în `release_date`
   (format `an-luna-zi`).
5. Coloanele care conțin `(s)` sau `%` sunt redenumite, deoarece Recombee nu le acceptă în numele
   proprietăților
6. Sunt păstrate doar cele 8 proprietăți alese și este adăugată coloana `item_id`.
7. Rezultatul este salvat în `spotify_songs_clean.csv`.

## Structura repository-ului

| Fișier | Rol |
|---|---|
| `spotify-2023.csv` | dataset-ul original descărcat de pe Kaggle |
| `spotify_songs_clean.csv` | dataset-ul curățat |
| `prepare_dataset.py` | scriptul care curăță dataset-ul |
| `recombee_properties.py` | scriptul care înregistrează proprietățile în Recombee |
| `requirements.txt` | bibliotecile Python necesare |

## Cum se rulează

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

python prepare_dataset.py

set "RECOMBEE_PRIVATE_TOKEN=<tokenul privat al bazei de date>"
python recombee_properties.py

## Laborator 3 – Încărcarea item-urilor în Recombee (`recombee_items.py`)

Toate cele **948 de piese** din `spotify_songs_clean.csv` au fost încărcate cu succes în Recombee
(rezultatul rulării: `Item-uri trimise cu succes: 948 din 948`).

### Maparea CSV → Recombee

| Coloana din CSV | În Recombee | Conversie |
|---|---|---|
| `item_id` | `itemId` (identificator nativ) | `str` |
| `track_name`, `artist_name` | proprietăți `string` | `str` |
| `release_date` | proprietate `timestamp` | `AAAA-LL-ZZ` → text ISO 8601 `AAAA-LL-ZZT00:00:00Z` |
| `streams`, `bpm`, `danceability`, `energy`, `valence` | proprietăți `int` | `int` |

Conversia explicită este necesară deoarece pandas citește numerele ca `numpy.int64`, pe care
biblioteca Recombee nu le poate serializa în JSON.

**Data lansării ca text ISO 8601.** Prima variantă trimitea data ca număr de secunde de la
1.01.1970. Pentru cele 16 piese lansate înainte de 1970 (în mare parte colinde clasice, ex.
*White Christmas* – 1942, *Jingle Bell Rock* – 1957) numărul era negativ, iar Recombee le-a respins
cu eroarea `Invalid timestamp value`. Trimise ca text ISO 8601, aceleași date sunt acceptate.

### Trimiterea în loturi (Batch)

Item-urile sunt trimise cu `SetItemValues(..., cascade_create=True)` grupate în cereri `Batch`
de câte 100 (10 cereri HTTP în loc de 948). Fiecare lot este verificat pe două niveluri:

1. **Lotul întreg** – `client.send` este pus într-un bloc `try/except APIException`; dacă lotul
   este respins (token greșit, rețea), eroarea este afișată și scriptul continuă cu loturile următoare.
2. **Fiecare item din lot** – Recombee răspunde cu codul 200 pentru lot chiar dacă unele item-uri
   din el au eșuat, așa că scriptul citește codul fiecărui item din răspuns și afișează ID-urile
   item-urilor respinse. Așa au fost descoperite cele 16 piese dinainte de 1970.

La final, scriptul verifică direct în Recombee numărul de item-uri (`ListItems`) și valorile
item-ului 1 (`GetItemValues`).

### Rulare

```cmd
set "RECOMBEE_PRIVATE_TOKEN=<tokenul privat al bazei de date>"
python recombee_items.py


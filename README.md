# Laborator 2 – Sistem de recomandare cu Recombee: înregistrarea proprietăților

## Domeniul ales

**Muzică** – cele mai ascultate piese pe Spotify în anul 2023

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

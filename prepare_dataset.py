"""
Pregatire dataset "Most Streamed Spotify Songs 2023" (Kaggle) pentru Recombee

Intrare:  spotify-2023.csv         - fisierul original descarcat de pe Kaggle
Iesire:   spotify_songs_clean.csv  - fisier modificat
"""
import pandas as pd

FISIER_ORIGINAL = "spotify-2023.csv"
FISIER_CURAT = "spotify_songs_clean.csv"

#  Citirea fisierului
df = pd.read_csv(FISIER_ORIGINAL, encoding="latin-1")
print(f"Randuri in fisierul original: {len(df)}")

#  Coloana 'streams' trebuie sa contina doar numere.
#    Un rand ("Love Grows (Where My Rosemary Goes)") are text in loc de numar
df["streams"] = pd.to_numeric(df["streams"], errors="coerce")
randuri_invalide = df[df["streams"].isna()]
for nume in randuri_invalide["track_name"]:
    print(f"Rand eliminat (streams invalid): {nume}")
df = df.dropna(subset=["streams"])
df["streams"] = df["streams"].astype("int64")

#  Unele piese apar de doua ori (acelasi titlu si acelasi artist).
#     Pastram doar prima aparitie, ca o piesa sa nu fie recomandata de doua ori
duplicate = df[df.duplicated(subset=["track_name", "artist(s)_name"])]
for nume in duplicate["track_name"]:
    print(f"Rand eliminat (piesa duplicata): {nume}")
df = df.drop_duplicates(subset=["track_name", "artist(s)_name"])

#  Unirea coloanelor released_year, released_month, released_day intr-o singura data
data_lansare = pd.to_datetime(
    df[["released_year", "released_month", "released_day"]].rename(
        columns={"released_year": "year", "released_month": "month", "released_day": "day"}
    )
)
df["release_date"] = data_lansare.dt.strftime("%Y-%m-%d")

# 4. Redenumirea coloanelor care contin "(s)" sau "%" pt ca Recombee nu le accepta in numele proprietatilor
df = df.rename(columns={
    "artist(s)_name": "artist_name",
    "danceability_%": "danceability",
    "energy_%": "energy",
    "valence_%": "valence",
})

# Pastram doar 8 proprietati alese
PROPRIETATI = [
    "track_name",
    "artist_name",
    "release_date",
    "streams",
    "bpm",
    "danceability",
    "energy",
    "valence",
]
df = df[PROPRIETATI]

# 6. Adaugam id unic
#    In Recombee acesta va deveni itemId (NU se declara ca proprietate).
df.insert(0, "item_id", range(1, len(df) + 1))

# 7. Salvarea fisierului curatat
df.to_csv(FISIER_CURAT, index=False, encoding="utf-8")

print(f"Randuri in fisierul curat: {len(df)}")
print(f"Fisier salvat: {FISIER_CURAT}")
print()
print("Primele 5 randuri:")
print(df.head().to_string(index=False))
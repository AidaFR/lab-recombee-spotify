import os
import sys

import pandas as pd
from recombee_api_client.api_client import RecombeeClient, Region
from recombee_api_client.api_requests import AddItemProperty, ListItemProperties
from recombee_api_client.exceptions import APIException, ResponseException

# TODO 1: Configurare credentiale Recombee
# Datele se iau din Recombee Admin UI -> baza de date -> Settings.
# Tokenul privat NU este scris in cod (repository-ul este pe GitHub), ci este citit
# din variabila de mediu RECOMBEE_PRIVATE_TOKEN. Inainte de rulare, in cmd:
#     set RECOMBEE_PRIVATE_TOKEN=tokenul_tau_privat
DB_NAME = 'spotify-songs-dev'
PRIVATE_TOKEN = os.environ.get('RECOMBEE_PRIVATE_TOKEN')
# Biblioteca recombee-api-client (versiunea 6.x) asteapta regiunea ca Region.EU_WEST,
# nu ca text ('eu-west'); cu text, crearea clientului da eroarea "Unknown region given".
REGION = Region.EU_WEST  # alte valori: Region.US_WEST, Region.CA_EAST, Region.AP_SE

if not PRIVATE_TOKEN:
    print("Eroare: variabila de mediu RECOMBEE_PRIVATE_TOKEN nu este setata.")
    print("Rulati mai intai in cmd:  set RECOMBEE_PRIVATE_TOKEN=tokenul_tau_privat")
    sys.exit(1)

# Initializarea clientului Recombee
client = RecombeeClient(DB_NAME, PRIVATE_TOKEN, region=REGION)

# TODO 2: Configurare dataset propriu
# Fisierul curat produs de prepare_dataset.py din "Most Streamed Spotify Songs 2023" (Kaggle)
PATH_DATASET = 'spotify_songs_clean.csv'

# TODO 3: Definirea schemei de date
# Coloana item_id NU apare aici: Recombee o gestioneaza nativ ca itemId.
PROPRIETATI_CATALOG = [
    {"name": "track_name", "type": "string"},        # numele piesei
    {"name": "artist_name", "type": "string"},       # artistul / artistii
    {"name": "release_date", "type": "timestamp"},   # data lansarii
    {"name": "streams", "type": "int"},              # numarul de ascultari pe Spotify
    {"name": "bpm", "type": "int"},                  # ritmul (batai pe minut)
    {"name": "danceability", "type": "int"},         # cat de dansabila este (0-100)
    {"name": "energy", "type": "int"},               # cat de energica este (0-100)
    {"name": "valence", "type": "int"},              # cat de pozitiva/vesela este (0-100)
]

def load_dataset():
    """Functie helper care citeste si verifica dataset-ul"""
    try:
        df = pd.read_csv(PATH_DATASET)
        total_randuri = len(df)
        print(f"Dataset incarcat cu succes! Total randuri: {total_randuri}")
        
        # Verificare numar de randuri (100 - 10K)
        if total_randuri < 100:
            print("ATENTIE: Dataset-ul are sub 100 de produse!")
        elif total_randuri > 10 * 1000:
            print("ATENTIE: Dataset-ul este prea mare! Limitati-l la primele 10K randuri.")

        # Verificare: fiecare proprietate definita trebuie sa existe ca si coloana in CSV
        lipsa = [prop["name"] for prop in PROPRIETATI_CATALOG if prop["name"] not in df.columns]
        if lipsa:
            print(f"Eroare: coloanele {lipsa} nu exista in '{PATH_DATASET}'!")
            return None
            
        print("\nPreview primele 3 randuri:")
        print(df.head(3))
        print("-" * 50)
        return df
    except FileNotFoundError:
        print(f"Eroare: Fisierul '{PATH_DATASET}' nu a fost gasit!")
        return None

def set_properties():
    """Functie care trimite structura coloanelor catre Recombee"""
    print(f"\nIncepe definirea proprietatilor pentru baza de date: '{DB_NAME}'...")
    
    for prop in PROPRIETATI_CATALOG:
        try:
            # Request API Recombee pentru adaugarea proprietatii (echivalentul adaugarii unei coloane intr-un tabel)
            client.send(AddItemProperty(prop["name"], prop["type"]))
            print(f"Proprietatea '{prop['name']}' ({prop['type']}) a fost adaugata cu succes.")
        except ResponseException as e:
            # Recombee raspunde cu 409 (Conflict) daca proprietatea a fost deja definita la o rulare anterioara
            if e.status_code == 409 or "already exists" in str(e).lower():
                print(f"Proprietatea '{prop['name']}' exista deja in Recombee.")
            else:
                print(f"Eroare API la proprietatea '{prop['name']}': {e}")
        except APIException as e:
            print(f"Eroare API la proprietatea '{prop['name']}': {e}")

def verify():
    """Interogheaza API-ul pentru a lista toate proprietatile active din cont"""
    print("\nSe verifica structura finala din Recombee...")
    try:
        atribute_active = client.send(ListItemProperties())
        print("Proprietatile configurate in acest moment in baza ta de date:")
        for atribute in atribute_active:
            print(f"- {atribute['name']} => tip de date: {atribute['type']}")
    except APIException as e:
        print(f"Nu s-a putut efectua verificarea. Detalii eroare: {e}")

if __name__ == "__main__":
    # Verificam daca fisierul CSV local se citeste corect
    dataset_ok = load_dataset()
    
    if dataset_ok is not None:
        # Trimitem proprietatile catre Recombee prin API
        set_properties()
        
        # Listam ce s-a salvat in baza de date pentru confirmare
        verify()
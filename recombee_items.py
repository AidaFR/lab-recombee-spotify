import os
import sys

import pandas as pd
from recombee_api_client.api_client import RecombeeClient, Region
from recombee_api_client.api_requests import SetItemValues, Batch, ListItems, GetItemValues
from recombee_api_client.exceptions import APIException

# TODO 1: Configurare credentiale Recombee (la fel ca la Lab 02)
DB_NAME = 'spotify-songs-dev'
PRIVATE_TOKEN = os.environ.get('RECOMBEE_PRIVATE_TOKEN')
REGION = Region.EU_WEST

client = RecombeeClient(DB_NAME, PRIVATE_TOKEN, region=REGION)

# TODO 2: Incarcarea aceluiasi dataset folosit la Lab 02
PATH_DATASET = 'spotify_songs_clean.csv'

MARIME_LOT = 100


def build_properties(row):
        # TODO 4: Mapati proprietatile definite anterior cu valorile din randul curent

    return {
        "track_name": str(row['track_name']),
        "artist_name": str(row['artist_name']),
	    "release_date": f"{row['release_date']}T00:00:00Z",
        "streams": int(row['streams']),
        "bpm": int(row['bpm']),
        "danceability": int(row['danceability']),
        "energy": int(row['energy']),
        "valence": int(row['valence']),
    }


def send_batch(requests, nr_lot):
    """Trimite un lot de request-uri si verifica rezultatul fiecarui item din lot.

    Intoarce lista cu ID-urile item-urilor care NU au ajuns in Recombee.
    """
    # Caz 1: tot lotul este respins, deci client.send arunca exceptie si niciun item nu ajunge in Recombee.
    try:
        raspunsuri = client.send(Batch(requests))
    except APIException as e:
        print(f"Lotul {nr_lot}: Eroare: lotul nu a fost acceptat, niciun item nu a ajuns. Detalii: {e}")
        return [req.item_id for req in requests]

    # Caz 2: lotul a fost acceptat (cod 200), dar rezultatul fiecarui item trebuie verificat separat.
    # Raspunsurile vin in ordinea in care au fost trimise request-urile.
    esuate = []
    for req, raspuns in zip(requests, raspunsuri):
        if raspuns['code'] not in (200, 201):
            esuate.append(req.item_id)
            print(f"  Item {req.item_id}: EROARE cod {raspuns['code']} - {raspuns['json']}")

    print(f"Lotul {nr_lot}: {len(requests) - len(esuate)}/{len(requests)} item-uri trimise cu succes.")
    return esuate


def send_items():
    """Functie care citeste dataset-ul si trimite item-urile in Recombee"""
    df = pd.read_csv(PATH_DATASET)
    print(f"Se trimit {len(df)} item-uri in Recombee...")

    requests = []
    esuate = []
    nr_lot = 0

    for index, row in df.iterrows():
        # TODO 3: Extrageti ID-ul unic al produsului din coloana corespunzatoare din CSV
        item_id = str(row['item_id'])

        properties = build_properties(row)

        # Adaugam request-ul de setare a valorilor pentru item
        # (SetItemValues creează automat item-ul dacă acesta nu există)
        requests.append(SetItemValues(item_id, properties, cascade_create=True))

        # Trimitem in loturi (batch) de cate 100 pentru eficienta
        if len(requests) == MARIME_LOT:
            nr_lot += 1
            esuate += send_batch(requests, nr_lot)
            requests = []

    # Trimitem si restul ramase (daca numarul total nu e multiplu de 100)
    if requests:
        nr_lot += 1
        esuate += send_batch(requests, nr_lot)

    print("-" * 50)
    print(f"Item-uri trimise cu succes: {len(df) - len(esuate)} din {len(df)}")
    if esuate:
        print(f"Item-uri care NU au ajuns in Recombee ({len(esuate)}): {', '.join(esuate)}")
    return len(df), esuate


def verify(total_asteptat):
    """Intreaba Recombee cate item-uri are acum si afiseaza valorile primului item"""
    print("-" * 50)
    print("Verificare in Recombee...")
    try:
        item_ids = client.send(ListItems(count=total_asteptat + 100))
        print(f"Item-uri existente in baza de date: {len(item_ids)} (asteptate: {total_asteptat})")

        valori = client.send(GetItemValues('1'))
        print("Valorile item-ului cu itemId = 1:")
        for nume, valoare in valori.items():
            print(f"  {nume}: {valoare}")
    except APIException as e:
        print(f"Nu s-a putut efectua verificarea. Eroare: {e}")


if __name__ == "__main__":
    total, esuate = send_items()
    verify(total)

    if esuate:
        sys.exit(1)
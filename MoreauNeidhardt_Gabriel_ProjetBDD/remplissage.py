import sqlite3
import random
from datetime import datetime, timedelta


conn = sqlite3.connect('base.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()


def ajouter_mesures():
    c.execute("SELECT id_Capteur, TYPE FROM Capteur")
    capteurs = c.fetchall()
    
    for capteur in capteurs:
        capteur_id = capteur['id_Capteur']
        capteur_type = capteur['TYPE']
        
        if capteur_type == "Température":
            valeur = lambda: round(random.uniform(15, 30), 2)
        elif capteur_type == "Humidité":
            valeur = lambda: random.randint(30, 70)
        elif capteur_type == "Lumière":
            valeur = lambda: random.randint(100, 300)
        elif capteur_type == "Mouvement":
            valeur = lambda: random.choice([0, 1]) 
        else:
            continue 
        
        date_actuelle = datetime.now()
        for _ in range(5):  
            date_insertion = date_actuelle - timedelta(minutes=random.randint(1, 100))
            c.execute("""
                INSERT INTO Mesure (DATEINSERTION, VALEUR, id_Capteur)
                VALUES (?, ?, ?)
            """, (date_insertion.strftime('%Y-%m-%d %H:%M:%S'), valeur(), capteur_id))


def ajouter_factures():
    date_actuelle = datetime.now()
    for _ in range(5):  
        date_facture = date_actuelle - timedelta(days=random.randint(30, 365))
        montant = round(random.uniform(50, 500), 2) 
        c.execute("""
            INSERT INTO Facture (DATE, MONTANT, VALCONSO, TYPE, id_Logement)
            VALUES (?, ?, ?, ?, ?)
        """, (
            date_facture.strftime('%Y-%m-%d'), 
            montant, 
            round(random.uniform(100, 500), 2),  
            random.choice(['Electricité', 'Eau', 'Gaz']), 
            1  
        ))

ajouter_mesures()
ajouter_factures()

conn.commit()
conn.close()


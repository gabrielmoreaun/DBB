import sqlite3

conn = sqlite3.connect('base.db')
c = conn.cursor()


tables = ['Logement', 'Piece', 'Capteur', 'Facture', 'Mesure']

for table in tables:
    c.execute(f"DELETE FROM {table}")


conn.commit()

conn.close()

print("Toutes les tables ont été vidées avec succès.")
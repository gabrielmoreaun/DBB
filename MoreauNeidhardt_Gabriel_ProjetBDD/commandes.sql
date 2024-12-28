CREATE TABLE IF NOT EXISTS Logement (
    id_Logement INTEGER PRIMARY KEY AUTOINCREMENT,
    ADRESSE TEXT NOT NULL, 
    NUMTEL TEXT,
    ADDRIP TEXT,
    DATEINSERTION DATE
);

CREATE TABLE IF NOT EXISTS Piece (
    id_Piece INTEGER PRIMARY KEY AUTOINCREMENT,
    NOM TEXT NOT NULL,
    LOCALISATION TEXT,
    id_Logement INTEGER,  
    FOREIGN KEY (id_Logement) REFERENCES Logement(id_Logement) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Capteur ( 
    id_Capteur INTEGER PRIMARY KEY AUTOINCREMENT,
    REFCOMMER TEXT,
    TYPE TEXT NOT NULL,
    DATEINSERTION DATE,
    id_Piece INTEGER, 
    PORTCOMMU TEXT NOT NULL,
    FOREIGN KEY (id_Piece) REFERENCES Piece(id_Piece) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS Facture (
    id_Facture INTEGER PRIMARY KEY AUTOINCREMENT, 
    MONTANT REAL NOT NULL, 
    VALCONSO REAL NOT NULL,
    TYPE TEXT NOT NULL,
    DATE DATE,
    id_Logement INTEGER, 
    FOREIGN KEY (id_Logement) REFERENCES Logement(id_Logement) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Type ( 
    id_Type INTEGER PRIMARY KEY AUTOINCREMENT,
    UNITE TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Mesure ( 
    id_Mesure INTEGER PRIMARY KEY AUTOINCREMENT,
    DATEINSERTION DATE,
    VALEUR REAL NOT NULL,
    id_Capteur INTEGER,
    FOREIGN KEY (id_Capteur) REFERENCES Capteur(id_Capteur) ON DELETE CASCADE
);

ALTER TABLE Capteur ADD COLUMN current_value TEXT;
ALTER TABLE Capteur ADD COLUMN last_updated DATETIME;


-- Ajout de 4 types de capteurs 
-- INSERT INTO Type (UNITE)
-- VALUES 
-- ('Celsius'),       
-- ('Pourcentage'),   
-- ('Lumen'),         
-- ('Détecté/Non détecté');
-- -- Supprimer la table Mesure 
-- DROP TABLE IF EXISTS Mesure;


-- -- Supprimer la table Facture 
-- DROP TABLE IF EXISTS Facture;

-- -- Supprimer la table Capteur 
-- DROP TABLE IF EXISTS Capteur;

-- -- Supprimer la table Piece 
-- DROP TABLE IF EXISTS Piece;

-- -- Supprimer la table Logement 
-- DROP TABLE IF EXISTS Logement;

-- -- Supprimer la table Type // ne pas toucher 
-- -- DROP TABLE IF EXISTS Type;  //ne pas toucher





-- Ajout d'un logement
-- INSERT INTO Logement (ADRESSE, NUMTEL, ADDRIP, DATEINSERTION)
-- VALUES ('123 Rue Exemple, Ville', '0123456789', '192.168.1.1', '2024-11-18');

-- -- Ajout de 4 pièces pour ce logement
-- INSERT INTO Piece (NOM, LOCALISATION, id_Logement)
-- VALUES 
-- ('Salon', 'Rez-de-chaussée', 1),
-- ('Cuisine', 'Rez-de-chaussée', 1),
-- ('Chambre', '1er étage', 1),
-- ('Salle de bain', '1er étage', 1);



-- -- Ajout de deux capteurs
-- INSERT INTO Capteur (REFCOMMER, TYPE, DATEINSERTION, id_Piece, PORTCOMMU)
-- VALUES 
-- ('TEMP-001', 'Température', '2024-11-18', 1, 'COM1'),
-- ('LUM-002', 'Lumière', '2024-11-18', 2, 'COM2');

-- -- Ajout de mesures 
-- INSERT INTO Mesure (DATEINSERTION, VALEUR, id_Capteur)
-- VALUES 
-- ('2024-11-18 12:00:00', 22.5, 1),  -- Mesure pour le capteur de température
-- ('2024-11-18 12:10:00', 23.0, 1),  -- Autre mesure pour le même capteur
-- ('2024-11-18 12:00:00', 150, 2),   -- Mesure pour le capteur de lumière
-- ('2024-11-18 12:10:00', 145, 2);   -- Autre mesure pour le même capteur

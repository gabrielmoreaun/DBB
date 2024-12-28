from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import re
import requests
from datetime import datetime, timedelta
import locale
from datetime import timezone

app = Flask(__name__)
API_KEY = "VOTRE_CLE_API"

def get_db_connection():
    conn = sqlite3.connect('base.db', timeout=10, isolation_level=None)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.row_factory = sqlite3.Row
    return conn
@app.route('/')
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

# Page d'accueil
@app.route('/index')
def index():
    conn = get_db_connection()
    try:
        logements = conn.execute('SELECT * FROM Logement').fetchall()
    except sqlite3.OperationalError as e:
        print(f"Erreur lors de l'accès aux logements : {e}")
        logements = []
    finally:
        conn.close()
    return render_template('index.html', logements=logements)


try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')  
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'fr_FR')  

@app.route('/meteo')
def meteo():
    city = request.args.get('city', 'Paris')  
    weather = []

    if city:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city},FR&appid={API_KEY}&units=metric&lang=fr"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            unique_dates = set()
            for entry in data['list']:
                date = entry['dt_txt'].split()[0]
                if date not in unique_dates:
                    unique_dates.add(date)
                    formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%a %d').capitalize()
                    weather.append({
                        'date': formatted_date,
                        'temp': round(entry['main']['temp']),
                        'icon': map_description_to_image(entry['weather'][0]['description'])
                    })
                if len(weather) == 5: 
                    break

    return render_template('meteo.html', weather=weather, city=city)


def map_description_to_image(description):
    """Mappe une description météo à une image."""
    mapping = {
        'ensoleillé': 'sunny.png',
        'ciel dégagé': 'sunny.png',
        'partiellement nuageux': 'partly_cloudy.png',
        'nuageux': 'cloudy.png',
        'couvert': 'overcast.png',
        'pluie légère': 'light_rain.png',
        'pluie': 'rain.png',
        'averses de pluie': 'shower_rain.png',
        'orageux': 'storm.png',
        'neige': 'snow.png',
        'brouillard': 'foggy.png',
        'bruine': 'drizzle.png',
        'vent': 'wind.png'
    }
    return mapping.get(description.lower(), 'default.png')  




@app.route('/create_logement', methods=['GET', 'POST'])
def create_logement():
    if request.method == 'POST':
        
        print(f"Données du formulaire : {request.form}")

      
        adresse = request.form['adresse']
        numtel = request.form['numtel']
        addrip = request.form['addrip']
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
           
            cursor.execute('''
                INSERT INTO Logement (ADRESSE, NUMTEL, ADDRIP, DATEINSERTION)
                VALUES (?, ?, ?, DATE('now'))
            ''', (adresse, numtel, addrip))
            logement_id = cursor.lastrowid
            print(f"Logement ajouté avec id : {logement_id}")

          
            pieces = request.form.getlist('pieces[]')
            pieces_locations = request.form.getlist('pieces_location[]')
            for i, (piece_name, piece_location) in enumerate(zip(pieces, pieces_locations)):
                print(f"Ajout de la pièce {piece_name} avec localisation {piece_location}")
                cursor.execute('''
                    INSERT INTO Piece (NOM, LOCALISATION, id_Logement)
                    VALUES (?, ?, ?)
                ''', (piece_name, piece_location, logement_id))
                piece_id = cursor.lastrowid
                print(f"Pièce ajoutée avec id : {piece_id}")

               
                capteur_refs = request.form.getlist(f'capteurs_ref_{i}[]')
                capteur_types = request.form.getlist(f'capteurs_type_{i}[]')
                capteur_ports = request.form.getlist(f'capteurs_port_{i}[]')
                for ref, typ, port in zip(capteur_refs, capteur_types, capteur_ports):
                    print(f"Ajout du capteur {ref}, type {typ}, port {port} pour la pièce {piece_id}")
                    cursor.execute('''
                        INSERT INTO Capteur (REFCOMMER, TYPE, DATEINSERTION, id_Piece, PORTCOMMU)
                        VALUES (?, ?, DATE('now'), ?, ?)
                    ''', (ref, typ, piece_id, port))

            conn.commit()
        except Exception as e:
            print(f"Erreur lors de l'insertion : {e}")
        finally:
            conn.close()
        return redirect(url_for('index'))
    return render_template('create_logement.html')


@app.route('/logement/<int:logement_id>')
def logement_details(logement_id):
    conn = get_db_connection()
    selected_location = request.args.get('location', 'all')  
    try:
        
        logement = conn.execute('SELECT * FROM Logement WHERE id_Logement = ?', (logement_id,)).fetchone()
        if not logement:
            return "Logement non trouvé", 404

        logement = dict(logement)

      
        if selected_location == 'all':
            pieces_query = 'SELECT * FROM Piece WHERE id_Logement = ?'
            pieces = conn.execute(pieces_query, (logement_id,)).fetchall()
        else:
            pieces_query = 'SELECT * FROM Piece WHERE id_Logement = ? AND LOCALISATION = ?'
            pieces = conn.execute(pieces_query, (logement_id, selected_location)).fetchall()

        pieces = [dict(piece) for piece in pieces]

        capteurs_by_piece = {}
        for piece in pieces:
            capteurs = conn.execute('SELECT * FROM Capteur WHERE id_Piece = ?', (piece['id_Piece'],)).fetchall()
            capteurs_by_piece[piece['id_Piece']] = [dict(capteur) for capteur in capteurs]

        selected_piece_id = None
    except sqlite3.OperationalError as e:
        print(f"Erreur lors de l'accès aux détails du logement : {e}")
        logement, pieces, capteurs_by_piece, selected_piece_id = None, [], {}, None
    finally:
        conn.close()

    return render_template(
        'logement_details.html',
        logement=logement,
        pieces=pieces,
        capteurs_by_piece=capteurs_by_piece,
        selected_piece_id=selected_piece_id,
        selected_location=selected_location  
    )



@app.route('/factures/<int:logement_id>')
def view_factures(logement_id):
    filter_type = request.args.get('type', 'all')  
    filter_month = request.args.get('month', 'all')  
    filter_year = request.args.get('year', 'all')  
    conn = get_db_connection()

    try:
        
        if filter_type == 'all':
            query_table = '''
                SELECT id_Facture, TYPE as type, MONTANT as montant, DATE as date
                FROM Facture
                WHERE id_Logement = ?
            '''
            factures = conn.execute(query_table, (logement_id,)).fetchall()
        else:
            query_table = '''
                SELECT id_Facture, TYPE as type, MONTANT as montant, DATE as date
                FROM Facture
                WHERE id_Logement = ? AND TYPE = ?
            '''
            factures = conn.execute(query_table, (logement_id, filter_type)).fetchall()

     
        factures = [
            {
                **dict(row),
                'date': datetime.strptime(row['date'], '%Y-%m-%d').strftime('%d/%m/%Y') if row['date'] else ''
            }
            for row in factures
        ]

        
        query_camembert = '''
            SELECT TYPE as type, SUM(MONTANT) as total
            FROM Facture
            WHERE id_Logement = ?
        '''
        params = [logement_id]

        if filter_month != 'all':
            query_camembert += ' AND strftime("%m", DATE) = ?'
            params.append(filter_month.zfill(2))  

        if filter_year != 'all':
            query_camembert += ' AND strftime("%Y", DATE) = ?'
            params.append(filter_year)

        query_camembert += ' GROUP BY TYPE'
        camembert_data = conn.execute(query_camembert, params).fetchall()
        camembert_data = [dict(row) for row in camembert_data]

       
        query_years = '''
            SELECT DISTINCT strftime("%Y", DATE) as year
            FROM Facture
            WHERE id_Logement = ?
            ORDER BY year ASC
        '''
        years = [row['year'] for row in conn.execute(query_years, (logement_id,))]

    except Exception as e:
        print(f"Erreur lors de la récupération des factures : {e}")
        factures = []
        camembert_data = []
        years = []
    finally:
        conn.close()

    return render_template(
        'factures.html',
        factures=factures,
        camembert_data=camembert_data,
        logement_id=logement_id,
        selected_type=filter_type,
        selected_month=filter_month,
        selected_year=filter_year,
        years=years
    )







@app.route('/add_facture/<int:logement_id>', methods=['GET', 'POST'])
def add_facture(logement_id):
    if request.method == 'POST':
        type_facture = request.form['type']
        montant = request.form['montant']
        valconso = request.form['valconso']
        date = request.form['date']

        if not type_facture or not montant or not valconso or not date:
            return "Tous les champs sont obligatoires.", 400

        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO Facture (TYPE, MONTANT, VALCONSO, DATE, id_Logement)
                VALUES (?, ?, ?, ?, ?)
            ''', (type_facture, float(montant), float(valconso), date, logement_id))
            conn.commit()
        except Exception as e:
            print(f"Erreur lors de l'ajout de la facture : {e}")
            return "Erreur interne.", 500
        finally:
            conn.close()

        return redirect(url_for('view_factures', logement_id=logement_id))
    
    return render_template('add_facture.html', logement_id=logement_id)

@app.route('/delete_facture/<int:logement_id>', methods=['GET', 'POST'])
def delete_facture(logement_id):
    conn = get_db_connection()
    if request.method == 'POST':
        facture_id = request.form['facture_id']

        if not facture_id:
            return "Aucune facture sélectionnée.", 400

        try:
            conn.execute('DELETE FROM Facture WHERE id_Facture = ?', (facture_id,))
            conn.commit()
        except Exception as e:
            print(f"Erreur lors de la suppression de la facture : {e}")
            return "Erreur interne.", 500
        finally:
            conn.close()

        return redirect(url_for('view_factures', logement_id=logement_id))

    try:
        factures = conn.execute('''
            SELECT id_Facture, TYPE as type, MONTANT as montant, DATE as date
            FROM Facture
            WHERE id_Logement = ?
        ''', (logement_id,)).fetchall()

        factures = [
            {
                **dict(row),
                'date': datetime.strptime(row['date'], '%Y-%m-%d').strftime('%d/%m/%Y') if row['date'] else ''
            }
            for row in factures
        ]
    except Exception as e:
        print(f"Erreur lors de la récupération des factures : {e}")
        factures = []
    finally:
        conn.close()

    return render_template('delete_facture.html', factures=factures, logement_id=logement_id)




@app.route('/capteurs/<int:logement_id>')
def view_capteurs(logement_id):
    conn = get_db_connection()

    try:
        capteurs_query = '''
            SELECT c.REFCOMMER as ref, c.TYPE as type, c.PORTCOMMU as port, 
                   c.DATEINSERTION as date_insertion, p.NOM as piece_nom, 
                   p.LOCALISATION as piece_localisation, c.current_value as current_value, 
                   c.last_updated as last_updated
            FROM Capteur c
            INNER JOIN Piece p ON c.id_Piece = p.id_Piece
            WHERE p.id_Logement = ?
        '''
        capteurs = conn.execute(capteurs_query, (logement_id,)).fetchall()
        capteurs = [dict(row) for row in capteurs]

       
        for capteur in capteurs:
            last_updated = capteur.get("last_updated")
            if last_updated:
                try:
                  
                    last_updated_time = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)  
                  
                    capteur["is_active"] = (now - last_updated_time) < timedelta(minutes=10)
                    print(f"Capteur {capteur['ref']} - Actif : {capteur['is_active']}")
                except ValueError as ve:
                    print(f"Erreur de conversion de date pour {capteur['ref']}: {ve}")
                    capteur["is_active"] = False
            else:
                print(f"Capteur {capteur['ref']} n'a pas de valeur last_updated.")
                capteur["is_active"] = False

    except Exception as e:
        print(f"Erreur lors de la récupération des données : {e}")
        capteurs = []
    finally:
        conn.close()

    print(f"Liste des capteurs envoyés au frontend : {capteurs}")
    return render_template('capteurs.html', capteurs=capteurs, logement_id=logement_id)


@app.route('/economies/<int:logement_id>')
def view_economies(logement_id):
    start_period1 = request.args.get('startPeriod1')
    end_period1 = request.args.get('endPeriod1')
    start_period2 = request.args.get('startPeriod2')
    end_period2 = request.args.get('endPeriod2')

    conn = get_db_connection()
    try:
        def calculate_total(start_period, end_period):
            query = '''
                SELECT SUM(MONTANT) as total
                FROM Facture
                WHERE id_Logement = ? AND DATE BETWEEN ? AND ?
            '''
            params = [logement_id, start_period + "-01", end_period + "-31"]
            result = conn.execute(query, params).fetchone()
            return result['total'] if result['total'] else 0

        period1_total = calculate_total(start_period1, end_period1) if start_period1 and end_period1 else 0
        period2_total = calculate_total(start_period2, end_period2) if start_period2 and end_period2 else 0

        economies = {
            "period1_total": period1_total,
            "period2_total": period2_total,
        }

    except Exception as e:
        print(f"Erreur lors de la récupération des données : {e}")
        economies = {"period1_total": 0, "period2_total": 0}
    finally:
        conn.close()

    return render_template('economies.html', economies=economies, logement_id=logement_id)




@app.route('/delete_piece/<int:logement_id>', methods=['GET', 'POST'])
def delete_piece(logement_id):
    conn = get_db_connection()
    if request.method == 'POST':
        piece_id = request.form['piece_id']
        try:

            conn.execute('DELETE FROM Capteur WHERE id_Piece = ?', (piece_id,))

            conn.execute('DELETE FROM Piece WHERE id_Piece = ?', (piece_id,))
            conn.commit()
        except Exception as e:
            print(f"Erreur lors de la suppression de la pièce : {e}")
        finally:
            conn.close()
        return redirect(url_for('logement_details', logement_id=logement_id))

    pieces = conn.execute('SELECT * FROM Piece WHERE id_Logement = ?', (logement_id,)).fetchall()
    conn.close()

    return render_template('delete_piece.html', logement_id=logement_id, pieces=pieces)

@app.route('/add_piece/<int:logement_id>', methods=['GET', 'POST'])
def add_piece(logement_id):
    conn = get_db_connection()
    if request.method == 'POST':
        piece_name = request.form['piece_name']
        piece_location = request.form['piece_location']
        try:
            conn.execute('''
                INSERT INTO Piece (NOM, LOCALISATION, id_Logement)
                VALUES (?, ?, ?)
            ''', (piece_name, piece_location, logement_id))
            conn.commit()
        except Exception as e:
            print(f"Erreur lors de l'ajout de la pièce : {e}")
        finally:
            conn.close()
        return redirect(url_for('logement_details', logement_id=logement_id))

    conn.close()
    return render_template('add_piece.html', logement_id=logement_id)



@app.route('/add_capteur', methods=['GET', 'POST'])
def add_capteur():
    piece_id = request.args.get('piece_id')
    logement_id = request.args.get('logement_id') 
    
    if not piece_id or not logement_id:
        return "Missing parameters", 400

    if request.method == 'POST':
        capteur_ref = request.form.get('capteur_ref')
        capteur_type = request.form.get('capteur_type')
        capteur_port = request.form.get('capteur_port')

        if not capteur_ref or not capteur_type or not capteur_port:
            return "Missing form data", 400

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO Capteur (REFCOMMER, TYPE, PORTCOMMU, id_Piece) VALUES (?, ?, ?, ?)',
            (capteur_ref, capteur_type, capteur_port, piece_id)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('logement_details', logement_id=logement_id))

    return render_template('add_capteur.html', piece_id=piece_id, logement_id=logement_id)



@app.route('/delete_capteur', methods=['GET', 'POST'])
def delete_capteur():
    piece_id = request.args.get('piece_id')
    logement_id = request.args.get('logement_id')  
    if request.method == 'POST':
        capteur_id = request.form['capteur_id']
        conn = get_db_connection()
        conn.execute('DELETE FROM Capteur WHERE id_Capteur = ?', (capteur_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('logement_details', logement_id=logement_id))
    conn = get_db_connection()
    capteurs = conn.execute('SELECT * FROM Capteur WHERE id_Piece = ?', (piece_id,)).fetchall()
    conn.close()
    return render_template('delete_capteur.html', capteurs=capteurs, piece_id=piece_id, logement_id=logement_id)

received_data = {}

@app.route('/update_data', methods=['POST'])
def update_data():
    global received_data

    if 'received_data' not in globals():
        received_data = {}

    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    ip_gateway = data.get('ip_gateway')
    sensor_ref = data.get('sensor_ref')
    temp = data.get('temperature')
    humidity = data.get('humidity')
    ip = data.get('ip')

    if not ip_gateway or not sensor_ref:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    print(f"Données reçues : {data}")

    received_data = data

    subnet = '.'.join(ip_gateway.split('.')[:3])
    conn = get_db_connection()
    try:
        logement = conn.execute(
            "SELECT * FROM Logement WHERE ADDRIP LIKE ? || '%'", (subnet,)
        ).fetchone()

        if logement:
            logement_id = logement['id_Logement']

           
            capteurs = conn.execute(
                """
                SELECT * FROM Capteur 
                WHERE REFCOMMER = ? 
                AND id_Piece IN (SELECT id_Piece FROM Piece WHERE id_Logement = ?)
                """,
                (sensor_ref, logement_id)
            ).fetchall()

            if capteurs:
                capteurs = [dict(row) for row in capteurs]

         
                capteur_temp = next((capteur for capteur in capteurs if capteur['TYPE'] == 'Celsius'), None)
                capteur_humidity = next((capteur for capteur in capteurs if capteur['TYPE'] == 'Pourcentage'), None)

                if capteur_temp and temp is not None:
                    print(f"Updating temperature sensor {capteur_temp['REFCOMMER']} with value {temp}")
                    conn.execute(
                        """
                        UPDATE Capteur
                        SET current_value = ?, last_updated = datetime('now')
                        WHERE id_Capteur = ?
                        """,
                        (temp, capteur_temp['id_Capteur'])
                    )

                if capteur_humidity and humidity is not None:
                    print(f"Updating humidity sensor {capteur_humidity['REFCOMMER']} with value {humidity}")
                    conn.execute(
                        """
                        UPDATE Capteur
                        SET current_value = ?, last_updated = datetime('now')
                        WHERE id_Capteur = ?
                        """,
                        (humidity, capteur_humidity['id_Capteur'])
                    )

                conn.commit()

                return jsonify({"status": "success", "message": "Capteurs mis à jour avec succès"})
            else:
                print(f"Aucun capteur trouvé pour la référence {sensor_ref} dans le logement {logement_id}")
                return jsonify({"status": "error", "message": "Aucun capteur trouvé"}), 404
        else:
            print(f"Logement avec IP gateway {ip_gateway} non trouvé")
            return jsonify({"status": "error", "message": "Logement non trouvé"}), 404
    except Exception as e:
        print(f"Erreur : {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500
    finally:
        conn.close()

@app.route('/show_data', methods=['GET'])
def show_data():
    global received_data

    if 'received_data' not in globals() or not received_data:
        received_data = {"status": "Aucune donnée reçue"} 

    return render_template('update_data.html', data=received_data)

@app.route('/info_logement/<int:logement_id>', methods=['GET', 'POST'])
def info_logement(logement_id):
    conn = get_db_connection()
    if request.method == 'POST':
        adresse = request.form.get('adresse')
        numtel = request.form.get('numtel')
        addrip = request.form.get('addrip')

        try:
            conn.execute('''
                UPDATE Logement
                SET ADRESSE = ?, NUMTEL = ?, ADDRIP = ?
                WHERE id_Logement = ?
            ''', (adresse, numtel, addrip, logement_id))
            conn.commit()
        except Exception as e:
            print(f"Erreur lors de la mise à jour : {e}")
        finally:
            conn.close()

        return redirect(url_for('logement_details', logement_id=logement_id))

    logement = conn.execute('SELECT * FROM Logement WHERE id_Logement = ?', (logement_id,)).fetchone()
    conn.close()

    if not logement:
        return "Logement non trouvé", 404

    return render_template('info_logement.html', logement=dict(logement))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)





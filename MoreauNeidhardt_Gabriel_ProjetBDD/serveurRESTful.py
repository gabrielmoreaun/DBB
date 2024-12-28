from flask import Flask, jsonify, request, render_template
import sqlite3
import requests
from datetime import datetime

app = Flask(__name__)


cache_meteo = {}
API_KEY = '8f253841ef57532b7a0d25ca479ead1f'
BASE_URL = 'https://api.openweathermap.org/data/2.5/forecast'
def charger_meteo(ville):
    global cache_meteo
    params = {
        'q': ville,
        'appid': API_KEY,
        'units': 'metric',
        'cnt': 5 * 8 
    }
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        previsions = []
        previsions_par_date = {}

        for entry in data['list']:
            date = entry['dt_txt'].split(" ")[0]  
            heure = entry['dt_txt'].split(" ")[1]  

            if date not in previsions_par_date and heure == "12:00:00":
                previsions_par_date[date] = {
                    'date': entry['dt_txt'],
                    'temperature': entry['main']['temp'],
                    'description': entry['weather'][0]['description']
                }
        
        for date in sorted(previsions_par_date.keys()):
            previsions.append(previsions_par_date[date])

        cache_meteo = {
            'ville': ville,
            'previsions': previsions
        }
    else:
        raise Exception(f"Erreur API météo : {response.status_code}, {response.text}")

@app.route('/meteo', methods=['GET'])
def get_meteo_cache():
    if cache_meteo:
        return jsonify(cache_meteo)
    else:
        return jsonify({'error': 'Données météo non disponibles'}), 500

@app.route('/admin/recharger_meteo', methods=['POST'])
def recharger_meteo():
    try:
        charger_meteo('Paris') 
        return jsonify({'message': 'Données météo rechargées avec succès'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_db_connection():
    conn = sqlite3.connect('base.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    return "Bienvenue sur mon super site !"

@app.route('/logements', methods=['GET'])
def get_logements():
    conn = get_db_connection()
    logements = conn.execute('SELECT * FROM Logement').fetchall()
    conn.close()
    return jsonify([dict(row) for row in logements])

@app.route('/logements', methods=['POST'])
def add_logement():
    data = request.get_json()
    adresse = data.get('ADRESSE')
    numtel = data.get('NUMTEL', None)
    addrip = data.get('ADDRIP', None)
    dateinsertion = datetime.now().strftime('%Y-%m-%d')

    if not adresse:
        return jsonify({'error': 'ADRESSE est requis'}), 400

    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO Logement (ADRESSE, NUMTEL, ADDRIP, DATEINSERTION)
        VALUES (?, ?, ?, ?)
        """,
        (adresse, numtel, addrip, dateinsertion)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Logement ajouté avec succès'}), 201

@app.route('/pieces/<int:piece_id>/capteurs', methods=['GET'])
def get_capteurs_by_piece(piece_id):
    conn = get_db_connection()
    capteurs = conn.execute(
        'SELECT * FROM Capteur WHERE id_Piece = ?', (piece_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in capteurs])

@app.route('/capteurs/<int:capteur_id>/mesures', methods=['POST'])
def add_mesure_to_capteur(capteur_id):
    data = request.get_json()
    valeur = data.get('VALEUR')
    dateinsertion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if valeur is None:
        return jsonify({'error': 'VALEUR est requis'}), 400

    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO Mesure (DATEINSERTION, VALEUR, id_Capteur)
        VALUES (?, ?, ?)
        """,
        (dateinsertion, valeur, capteur_id)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Mesure ajoutée avec succès'}), 201

@app.route('/logements/<int:logement_id>/factures', methods=['GET'])
def get_factures_by_logement(logement_id):
    conn = get_db_connection()
    factures = conn.execute(
        'SELECT * FROM Facture WHERE id_Logement = ?', (logement_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in factures])

@app.route('/logements/<int:logement_id>/factures', methods=['POST'])
def add_facture_to_logement(logement_id):
    data = request.get_json()
    montant = data.get('MONTANT')
    valconso = data.get('VALCONSO')
    type_facture = data.get('TYPE')
    date = datetime.now().strftime('%Y-%m-%d')

    if not montant or not valconso or not type_facture:
        return jsonify({'error': 'MONTANT, VALCONSO et TYPE sont requis'}), 400

    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO Facture (MONTANT, VALCONSO, TYPE, DATE, id_Logement)
        VALUES (?, ?, ?, ?, ?)
        """,
        (montant, valconso, type_facture, date, logement_id)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Facture ajoutée avec succès'}), 201

@app.route('/factures/chart', methods=['GET'])
def chart_factures():
    conn = get_db_connection()
    factures = conn.execute('SELECT TYPE, SUM(MONTANT) as total FROM Facture GROUP BY TYPE').fetchall()
    conn.close()

    chart_data = [["Type", "Montant"]]
    chart_data.extend([[facture["TYPE"], facture["total"]] for facture in factures])

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fromton des Factures</title>
        <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
        <script type="text/javascript">
            google.charts.load('current', {{packages: ['corechart']}});
            google.charts.setOnLoadCallback(drawChart);

            function drawChart() {{
                var data = google.visualization.arrayToDataTable({chart_data});

                var options = {{
                    title: 'Répartition des Factures par Type',
                    pieHole: 0.4,
                }};

                var chart = new google.visualization.PieChart(document.getElementById('piechart'));
                chart.draw(data, options);
            }}
        </script>
    </head>
    <body>
        <h1>Répartition des Factures</h1>
        <div id="piechart" style="width: 900px; height: 500px;"></div>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    try:
        print("Chargement des données météo...")
        charger_meteo('Paris') 
        print("Données météo chargées avec succès.")
        app.run(debug=True)
    except Exception as e:
        print(f"Erreur lors du chargement des données météo : {e}")


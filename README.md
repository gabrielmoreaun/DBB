LOGEMENT ECO-RESPONSABLE

ECO-Gestion

ECO-Gestion est une application web conçue pour aider les utilisateurs à gérer leurs logements de manière écoresponsable. Elle permet de suivre les factures, gérer les capteurs et pièces des logements, et comparer les économies réalisées



Glossaire

  I-Fonctionnalités
 II-Technologies
III-Structure
 IV-Prérequis et installation
  V-Utilisation



I-Fonctionnalités

L'application permet de gérer vos logements de manière complète et intuitive. Vous pouvez créer, modifier et personnaliser vos logements en ajoutant ou supprimant des pièces et des capteurs, tout en actualisant leurs informations. Elle offre la possibilité d'ajouter des factures (eau, gaz, électricité) afin de suivre vos dépenses énergétiques de manière détaillée. Grâce à ces factures, vous pouvez également visualiser vos économies à travers des graphiques comparant les dépenses sur des périodes définies. La gestion des capteurs et le suivi de leurs relevés sont intégrés pour une supervision précise. 
Enfin, l'application propose des prévisions météorologiques basées sur l'API OpenWeatherMap, vous permettant d'anticiper les conditions climatiques et d'ajuster votre consommation en conséquence.

  

II-Technologies

 - Backend : Le framework Flask est utilisé pour gérer la logique applicative et les interactions avec la base de données, offrant une structure légère et performante pour le développement web.
 - Base de données : SQLite est employée comme base de données relationnelle pour stocker et organiser les données des logements, factures, pièces et capteurs de manière efficace.
 - Frontend : L'interface utilisateur est développée en HTML5 et CSS3, avec Bootstrap pour un design moderne et responsive, et JavaScript (Chart.js) pour la visualisation interactive des données.
 - API : OpenWeatherMap API est intégrée pour fournir des prévisions météorologiques en temps réel, permettant d'adapter la gestion des logements en fonction des conditions climatiques.
 -ESP32 et Arduino : L'ESP32, programmé avec Arduino, est utilisé comme microcontrôleur pour collecter les données des capteurs DHT11 (température et humidité). Ce module assure une communication en temps réel entre les capteurs et l'application web.




III-Structure

/sketch_dec26b
    /sketch_dec26b.ino
/static
    /icons
        bruine.png
        cloudy.png
	default.png
	...
    /images
	background.png
	capteurs.gif
	capteurs_static.gif
	...  
/templates
    base.html
    index.html
    logement_details.html
    ...
app.py
base.db
commandes.sql
Diagramme.png
README.txt
suppression.txt ///
vidange.py
serveurRESTful.py




IV-Prérequis et installation

Pour exécuter l'application ECO-Gestion, assurez-vous de disposer des éléments suivants :

 - Python 3.x : L'application est développée en Python, veillez à installer une version récente pour garantir la compatibilité.
 - SQLite : Nécessaire pour gérer la base de données utilisée par l'application.
 - Connexion Internet : Requise pour accéder aux API externes, notamment OpenWeatherMap pour les prévisions météorologiques.
 - API : Un compte Openweathermap est obligatoire pour posséder une API key et afficher les données météo (https://openweathermap.org/).
 - Arduino IDE 2.3.4 : Nécessaire pour programmer l'ESP32 et configurer les capteurs comme le DHT11. Téléchargez et installez la version récente depuis le site officiel (https://www.arduino.cc/).


Les bibliothèques suivante sont nécessaire pour faire fonctionner le code python : 

 - Flask : Framework web léger utilisé pour construire l'application et gérer les routes, le rendu des templates HTML, et les interactions HTTP (requêtes, redirections, JSON).
 - sqlite3 : Module intégré à Python pour interagir avec la base de données SQLite utilisée dans l'application.
 - re : Fournit des fonctionnalités pour travailler avec des expressions régulières, utilisées notamment pour valider ou manipuler des données.
 - requests : Permet d'effectuer des requêtes HTTP, notamment pour récupérer les données météo depuis l'API OpenWeatherMap.
 - datetime : Fournit des classes pour manipuler les dates et les heures, essentielles pour le traitement des factures et des prévisions météorologiques.
 - locale : Module permettant de configurer la localisation pour formater les dates et textes selon les conventions françaises.

Pour installer les bibliothèques Python nécessaires au projet, vous pouvez utiliser pip, le gestionnaire de packages Python. Suivez les étapes ci-dessous :

 - Ouvrez un invité de commande.
 - Vérifiez que Python 3.x est installé avec la commande "python --version" ou "python3 --version".
 - Flask : "pip install flask".
 - SQLite (intégré dans Python, pas besoin d'installation supplémentaire).
 - re (module intégré, aucune installation requise).
 - Requests : pip install requests.
 - Locale et datetime (modules intégrés, aucune installation requise).


Les bibliothèques suivante sont nécessaire pour faire fonctionner le code arduino :
 
 - Arduino ESP32 Boards by Arduino : Fournit le support matériel et logiciel pour programmer l'ESP32 avec l'IDE Arduino.
 - esp32 by Espressif Systems : Offre un support officiel et complet pour l'ESP32 dans l'IDE Arduino.
 - DHT sensor library by Adafruit : Permet de lire les données des capteurs DHT.

Le code arduino utilise plusieurs bibliothèques Arduino pour exploiter les fonctionnalités de l'ESP32 et des capteurs. Voici un guide pour les installer :

 - Ouvrez l’IDE Arduino.
 - Allez dans Tools > Board:"..." > Boards Manager.
 - Recherchez ESP32 dans la barre de recherche.
 - Installer esp32 by Espressif Systems et Arduino ESP32 Boards by Arduino.

 - Allez dans Tools > Manage Libraries.
 - Recherchez DHT sensor library dans la barre de recherche.
 - Installer DHT sensor library by Adafruit.


Une clé API est nécessaire pour faire fonctionner la partie météo de l'application web. Voici un guide pour l'obtenir:
	
 - Rendez-vouz sur le site "https://openweathermap.org/".
 - Créez un compte un compte Openweathermap ou connectez-vous si vous en avez déjà un.
 - Souscrivez à l'abonnement "Pay as you call".
 - Cliquez sur votre profil.
 - Sélectionnez "My API keys".
 - Récupérez votre API key.



V-Utilisation

1/Initialisation

 - Dans le code python "app.py" collé l'API key de votre compte Openweathermap précédemment créé à la ligne 10 : API_KEY = "VOTRE_CLE_API"
 - Dans le code arcuino "sketch_dec26b.ino" remplissez les champs ssid et password aux ligne 8 et 9 : "const char* ssid = "";" et "const char* password = "";". Ceci définit le réseau auquel l'ESP32 se connecte. Assurez-vous d'utiliser le même réseau que celui de l'ordinateur qui héberge le serveur. 
 - Dans le code arcuino "sketch_dec26b.ino" remplissez le champ ligne 12 : "const char* serverURL = "";". Pour determiner cette valeur ouvrez un invité de commande. Rentrez la commande "ipconfig" et récupérez la valeur "Adresse IPv4". Remplissez le champs par "http://AdresseIPv4:5000" (exemple : const char* serverURL = "http://192.168.0.38:5000";).

Vous pouvez maintenant lancer le serveur et téléverser le code arduino sur l'ESP32.


2/Naviguation et interface

 - Accueil   : Vous y trouverez un message de bienvenue.  
 - Météo     : Vous y accéderer en cliquant sur le GIF représentant un soleil et des nuages, situé en haut à droite de la page. Sur cette page vous pouvez séléctionner une ville de France pour y voir une prédiciton météo sur cinq jours.  
 - Logement  : Vous y trouverez la liste des logement exitants dans la base de données. Vous pouvez soit créer un nouveau logement soit en séléctionner un pour le modifier ou voir ses informations en cliquant dessus.
 - Logement détail : Vous y trouverez tous les détails d'un logement (pièces, capteurs, informations et factures). L'ensemble des données du logement sont modifiables (ajout/suppression de capteurs et de pièces et modifications des informations du logement) en cliquant sur les blocs.
 - Capteurs  : Vous y trouverez la liste des capteurs du logement et vous serez lesquel sont actifs ou non.
 - Factures  : Vous y trouverez l'ensemble des factures du logement. Vous pourrez en ajouter ou en supprimer en cas d'erreur de saisi et vous pourrez connaître vos dépenses par mois et par année.
 - Economies : Vous pourrez comparez les dépenses sur différentes périodes pour évaluer vos économies.

3/Utilisation des capteurs

Pour connecter un capteur à votre logement suivez ces étapes : 
 - Une fois le serveur lancé et le code arduino téleversé récupérez l'ip_gateway. Vous pouvez la trouver dans le terminal arduino ou sur cette page spécialement créé pour voir si le serveur récupère bien le donnée du capteur : "http://127.0.0.1:5000/show_data". 
 - Lors de la création du logement utilisez cette ip_gateway comme IP pour le logement.
 - Ajouter un nouveau capteur dans un pièce en utilisant, comme référence du capteur le nom determiné par défaut dans le code arduino ligne 4 : "#define SENSOR_REF "DHT11-001"  // Référence unique du capteur". Il peut être modifié mais les noms doivent correspondre pour asssurer la synchronisation. Un fois cela fait le capteur affichera sa mesure dans les détails du logement et il sera noté comme actif dans le tableau des capteurs. Sachant que le DHT11 fais à la fois capteur de température et d'humidité, il pourra convrir deux capteurs, un de température et un d'humidité si deux capteurs de type différent (température et humidité) sont présent dans le même pièce et utilisent tous deux la référence du capteur utilisée dans le code arduino.


4/Base de données

Pour rénitialiser la base de donnée suivez ce guide :
 - Ouvrez un invité de commande.
 - Rendez-vous dans le répertoire où se situe la base de donnée.
 - Lancez SQLite avec lac commande : "sqlite3 base.db".
 - Executer le fichier suppression.sql avec la commande : ".read suppression.sql".
 - Executer le fichier commandes.sql avec la commande : ".read commandes.sql".

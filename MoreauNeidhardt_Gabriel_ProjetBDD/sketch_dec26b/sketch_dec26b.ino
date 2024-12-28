#include <WiFi.h>          
#include <HTTPClient.h>    
#include "DHT.h"           
#define SENSOR_REF "DHT11-001"  // Référence unique du capteur


// Configuration réseau
const char* ssid = "";// a remplacer
const char* password = "";//a remplacer

// Configuration du serveur
const char* serverURL = "http://192.168.0.38:5000";  // Remplacez "192.168.0.38" par IPV4 de la machine ou est hebergé le serveur

// Configuration du capteur DHT
#define DHTPIN 4           // Pin connectée DHT11 
#define DHTTYPE DHT11      // Type de capteur
DHT dht(DHTPIN, DHTTYPE);


WiFiClient wifiClient;

void setup() {
  Serial.begin(115200);

 
  dht.begin();

 
  Serial.println("Connexion au WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connecté !");
  Serial.print("Adresse IP : ");
  Serial.println(WiFi.localIP());
}

void loop() {
  
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

 
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Erreur de lecture du capteur !");
    delay(2000);
    return;
  }

  
  if (WiFi.status() == WL_CONNECTED) {  
    HTTPClient http;
    http.begin(String(serverURL) + "/update_data");  
    http.addHeader("Content-Type", "application/json");  

   
    String payload = "{\"temperature\":" + String(temperature) +
                 ",\"humidity\":" + String(humidity) +
                 ",\"ip\":\"" + WiFi.localIP().toString() +
                 "\",\"sensor_ref\":\"" + String(SENSOR_REF) +
                 "\",\"ip_gateway\":\"" + WiFi.gatewayIP().toString() + "\"}";
    Serial.print("Envoi des données : ");
    Serial.println(payload);

   
    int httpResponseCode = http.POST(payload);

   
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Réponse du serveur : " + response);
    } else {
      Serial.print("Erreur HTTP : ");
      Serial.println(httpResponseCode);
    }

    http.end();  
  } else {
    Serial.println("WiFi déconnecté !");
  }

  delay(10000);  
}




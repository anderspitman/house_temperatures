

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>

#define DHTPIN D4
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);
int id = -1;
int uploadIntervalSeconds = 10;

void setup() {

    Serial.begin(115200);
    //Serial.setDebugOutput(true);

    Serial.println();
    Serial.println();
    Serial.println();

    WiFi.begin("ssid", "wpa-password");

    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }

    Serial.println("");
    Serial.println("WiFi connected");  
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
    String mac = WiFi.macAddress();
    Serial.println("MAC address: ");
    Serial.println(mac);

    if (mac == "5C:CF:7F:3A:A2:AB") {
      id = 1;
    }
    else if (mac == "60:01:94:1E:F1:15") {
      id = 2;
    }
    else if (mac == "5C:CF:7F:3A:D5:1A") {
      id = 3;
    }
    else if (mac == "5C:CF:7F:3A:A3:DE") {
      id = 4;
    }
    else if (mac == "5C:CF:7F:3A:D5:34") {
      id = 5;
    }
    else if (mac == "5C:CF:7F:3A:94:5B") {
      id = 6;
    }
    else if (mac == "5C:CF:7F:3A:9F:97") {
      id = 7;
    }
    else if (mac == "5C:CF:7F:3A:D0:C4") {
      id = 8;
    }

    dht.begin();

}

void loop() {
    // wait for WiFi connection
    if((WiFi.status() == WL_CONNECTED)) {

        HTTPClient http;
        
        float temp = dht.readTemperature();
        float humidity = dht.readHumidity();

      
        http.begin("192.168.0.160", 5001, "/upload_interval/");
        int httpCode = http.GET();
    
        if(httpCode > 0) {
          if(httpCode == HTTP_CODE_OK) {
              String payload = http.getString();
              uploadIntervalSeconds = payload.toInt();
          }
          else {
            Serial.println("Failed to retrieve upload interval");
          }
        }
        else {
          Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
        }

        Serial.print("[HTTP] begin...\n");
        
        http.begin("192.168.0.160", 5001, "/readings/" + String(id));
        http.addHeader("Content-Type", "application/json");

        Serial.print("[HTTP] POST...\n");
        // start connection and send HTTP header
        httpCode = http.POST("{ \"temperature_celsius\": " + String(temp) + ",\n\"humidity\": " + String(humidity) + "}");

        http.writeToStream(&Serial);

        // httpCode will be negative on error
        if(httpCode > 0) {
            // HTTP header has been send and Server response header has been handled
            Serial.printf("[HTTP] POST... code: %d\n", httpCode);

            // file found at server
            if(httpCode == HTTP_CODE_OK) {
                String payload = http.getString();
                Serial.println(payload);
            }
        } else {
            Serial.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpCode).c_str());
        }

        http.end();
    }

    delay(uploadIntervalSeconds * 1000);
}


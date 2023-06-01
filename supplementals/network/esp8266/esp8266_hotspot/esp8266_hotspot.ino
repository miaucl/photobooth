#include <ESP8266WiFi.h>

const char* ssid     = "o3pxxkr5khPC";
const char* password = "87faNAMhrGrq";

void setup()
{
  Serial.begin(115200);
  Serial.println();

  Serial.print("Setting soft-AP ... ");
  boolean result = WiFi.softAP(ssid, password);
  if(result == true)
  {
    Serial.println("Ready");
  }
  else
  {
    Serial.println("Failed!");
  }
}

void loop()
{
  Serial.printf("Stations connected = %d\n", WiFi.softAPgetStationNum());
  delay(3000);
}

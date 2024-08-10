#include <ESP8266WiFi.h>

const char* ssid     = "Photomaton Hotspot";
const char* password = "321smile";

WiFiEventHandler stationConnectedHandler;
WiFiEventHandler stationDisconnectedHandler;

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

  stationConnectedHandler = WiFi.onSoftAPModeStationConnected(&onStationConnected);

  stationDisconnectedHandler = WiFi.onSoftAPModeStationDisconnected(&onStationDisconnected);
}

void onStationConnected(const WiFiEventSoftAPModeStationConnected& evt) 
{
  Serial.print("Station connected: ");
  Serial.println(evt.aid);
  Serial.println(macToString(evt.mac));
}

void onStationDisconnected(const WiFiEventSoftAPModeStationDisconnected& evt) 
{
  Serial.print("Station disconnected: ");
  Serial.println(evt.aid);
  Serial.println(macToString(evt.mac));
}

void loop()
{
  Serial.printf("Stations connected = %d\n", WiFi.softAPgetStationNum());
  delay(3000);
}

String macToString(const unsigned char* mac)
{
  char buf[20];
  snprintf(buf, sizeof(buf), "%02x:%02x:%02x:%02x:%02x:%02x", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  return String(buf);
}
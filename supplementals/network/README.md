# Network

Several possibilities are available to access the photobooth using one of the following network options.

## Router

Using a regular router, the photobooth has access to all printers on that network, the photobooth web page can be accessed and all features using internet are available. It is the responsibility of the router whether the photobooth is accessible from devices outside the routers subnet or limit to local devices.

## Printer Hotspot

Most network printers provide a mode to provide their own hotspot. This is useful, when one does not have access to a network or for a mobile setup. The photobooth can use the printer directly and other devices will be able to reach the photobooth web page by connecting to the printers hotspot. All features requiring internet cannot be used in this mode.

## ESP32/ESP8266 Hotspot (or similar such as a mobile phone)

When no printer is needed, or it does not provide a hotspot feature, a simple low-cost hotspot can be created by a ESP32/ESP8266 chip, which creates a local network over which other devices can access the photobooth web page, much alike the printer hotspot. Any wifi-able printer can then be connected to this hotspot as well to be available to the photobooth. No feature requiring internet can be used in this mode.

Alternatively, when a hotspot with internet access is used, such as a mobile phone, all mentioned features above are also available and the internet-dependent features on top, much alike the router option.

## Internet stick

Using an internet stick or a phones hotspot grants direct internet access to the photobooth and can be used **in addition to any other option**. This allow to use features such as `Mailer`, `WebDAV` or `UploadS3` when required.

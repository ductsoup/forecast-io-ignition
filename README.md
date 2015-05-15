# forecast-io-ignition
A forecast.io API script for Inductive Automation's Ignition SCADA product
## Overview
There's a good introduction to [forecast.io](http://forecast.io) over at [lifehacker](http://lifehacker.com/5992542/forecastio-delivers-a-useful-animated-weather-report-for-your-location-all-on-one-page). Briefly, it's a very useful and sophisticated short-term weather forecast site, smart phone app and JSON feed. Integrated with [Ignition](https://inductiveautomation.com/), the practical applications are almost unlimited.

This example recursively maps the entire API payload for a given location along with some convenient derived values into an Ignition tag database. Ignition already has a JSON parser so it only takes two lines of Jython to retrieve the payload and parse it into a dictionary.

```
json = system.net.httpGet("https://api.forecast.io/forecast/" + APIKey + "/" + LatLon)
res = system.util.jsonDecode(json)
```
From there it's a relatively simple matter to traverse the directory, recreate the payload's structure and bind the data to a collection of Ignition memory tags. The script is called from a gateway timer event to refresh the tags periodically.

## Installation
First you'll need an installed copy of Ignition. Either the demo or licensed version will work just fine. The other thing you need is an API key. You can obtain one from [https://developer.forecast.io](https://developer.forecast.io). 

In Ignition Designer create a new global script called forecast_io. Copy and paste the contents of forecast_io.py in the new script.

![ScreenShot1](/images/ScreenShot1.jpg)

Edit the script, configure your API key and location then commit and save. 

![ScreenShot2](/images/ScreenShot2.jpg)

With the script installed it's time to configure the gateway timer. Go to Project, Gateway Event Scripts and create a new timer event called forecast_io. Set the time to something reasonable, say 120,000ms.

![ScreenShot3](/images/ScreenShot3.jpg)

Finally, cut and paste or type the contents of gateway_timer.py and you're ready to go.

![ScreenShot4](/images/ScreenShot4.jpg)

If all went well you should see something like this in your tag browser.

![ScreenShot5](/images/ScreenShot5.jpg)

## Design Notes
All derived tag names begin with an underscore.


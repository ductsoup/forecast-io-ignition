# forecast-io-ignition
A forecast.io API script for Inductive Automation's Ignition SCADA product
## Overview
There's a good introduction to [forecast.io](http://forecast.io) over at [lifehacker](http://lifehacker.com/5992542/forecastio-delivers-a-useful-animated-weather-report-for-your-location-all-on-one-page). Briefly, it's a concise and very sophisticated short-term weather forecast site, smart phone app and JSON feed. Integrated with [Ignition](https://inductiveautomation.com/), the practical applications are almost unlimited.

This example recursively maps the entire API payload for a given location along with some convenient derived values into an Ignition tag database. Ignition already has a JSON parser so it only takes two lines of Jython to retrieve the payload and parse it into a dictionary.

```
json = system.net.httpGet("https://api.forecast.io/forecast/" + APIKey + "/" + LatLon)
res = system.util.jsonDecode(json)
```
From there it's a relatively simple matter to traverse the directory, recreate the payload's structure and bind the data to a collection of memory tags. The script is called from a gateway timer event to refresh the tags periodically.

## Installation
First you'll need an installed copy of Ignition. Either the demo or licensed version will work just fine. The other thing you need is an API key. You can obtain one from [https://developer.forecast.io](https://developer.forecast.io). 

In Ignition Designer create a new global script called forecast_io. Copy and paste the contents of forecast_io.py in the new script.

![ScreenShot1](/images/ScreenShot1.jpg)

Edit the script, configure your API key and location then commit and save. 

![ScreenShot2](/images/ScreenShot2.jpg)

With the script installed it's time to configure the gateway timer. Go to Project, Gateway Event Scripts and create a new timer event called forecast_io. Set the time to something reasonable, say about 120,000ms. That'll keep you in the free zone. 

![ScreenShot3](/images/ScreenShot3.jpg)

Finally, cut and paste or type the contents of gateway_timer.py and you're ready to go.

![ScreenShot4](/images/ScreenShot4.jpg)

If all went well you should see something like this in your tag browser.

![ScreenShot5](/images/ScreenShot5.jpg)

## Design Notes
It's been a while since I've worked with Python. It came back quickly but I'm sure some of the for loops could be streamlined. There's no major performance issue here, more just coding style.

This is a complicated payload. With Ignition running on a well provisioned Ubuntu virtual host it's taking 400 to 800ms to run. But, since we're only executing it every two minutes we're not going to sink a ship or anything. The first run is the worst since the gateway has to create all the tags. From there we update and only remove and recreate those tags that are potentially stale and misleading like NOAA alerts.

For reasons of sanity all derived tag names begin with an underscore so it's easy to distinguish what came from the API and what's been coalesed. One of the challenges is Ignition prefers a reliable, defined set of tags and nearly all of the forecast.io API is optional. For any given location the API seems to be pretty consistent in the information it provides. If you're going to be sweeping the location all across the globe you'll definitely need to work more robust exception handling into the derived tags.

I've been testing this code for a couple days and it seems reliable with the possible exception of the alert tags.  The weather here has been mild so for testing purposes I've been changing the lat/lon and chasing storms all over North America. There may be some refinements to that little piece later.

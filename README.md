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

##Time Series Usage Example
For convenience each time series is isolated then joined into a delimited string tag. To use the data retrieve the string and use the split method.

In this example I've got a chart object and the script below attached to a button event. 

![ScreenShot6](/images/ScreenShot6.jpg)

```
from java.util import Date
y = system.tag.read("forecast_io/hourly/data/_time").value.split(",")
x1 = system.tag.read("forecast_io/hourly/data/_ozone").value.split(",")
x2 = system.tag.read("forecast_io/hourly/data/_pressure").value.split(",")
row1 = []
row2 = []
for i, v in enumerate(y):	
	row1.append([Date(1000*int(y[i])), float(x1[i])])
	row2.append([Date(1000*int(y[i])), float(x2[i])])
data1 = system.dataset.toDataSet(["t_stamp", "Ozone"], row1)	
data2 = system.dataset.toDataSet(["t_stamp", "Pressure"], row2)	
event.source.parent.getComponent("Chart").Data1 = data1
event.source.parent.getComponent("Chart").Data2 = data2
#system.gui.messageBox("The value is %s" % rows)
```

## Design Notes
It's been a while since I've worked with Python. It came back quickly but I'm sure some of the for loops could be streamlined. There's no major performance issue here, more just coding style.

This is a complicated payload. With Ignition running on a well provisioned Ubuntu virtual host it's taking 400 to 800ms to run. But, since we're only executing it every two minutes we're not going to sink a ship or anything. The first run is the worst since the gateway has to create all the tags. From there we update and only remove and recreate those tags that are potentially stale and misleading like NOAA alerts.

For reasons of sanity all derived tag names begin with an underscore so it's easy to distinguish what came from the API and what's been coalesed. One of the challenges is Ignition prefers a reliable, defined set of tags and nearly all of the forecast.io API is optional. For any given location the API seems to be pretty consistent in the information it provides. If you're going to be sweeping the location all across the globe you'll definitely need to work more robust exception handling into the derived tags.

For the derived time series tags other encodings such as JSON are certainly possible. I opted for a string of delimited values because it's simple and, it's easier to understand the values if you're just browsing the tags. The trade off is you have to build the dictionary object in the client but that only takes a couple lines. If you know in advance exactly which series you're going to use, building the dictionary in the gateway script and storing it as a JSON tag would be the better way to go.

I've been testing this code for a couple days and it seems reliable with the possible exception of the alert tags.  The weather here has been mild so for testing purposes I've been changing the lat/lon and chasing storms all over North America. There may be some refinements to that little piece later.

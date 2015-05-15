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

All derived tag names begin with an underscore.
## Installation

'''        
shared.forecast_io

Map forcast.io into Ignition

MIT License
Copyright (c) 2015 Ductsoup
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE. 

Reference 

http://forecast.io
https://developer.forecast.io <-- get an API key here
https://developer.forecast.io/docs/v2 <-- API documentation
http://json.parser.online.fr <-- unrelated but very handy for debugging 
'''

from java.util import Date

def fetch():

        def isfloat(value):
                ''' determine if a string value quacks like a float '''
                try:
                        float(value)
                except:
                        return False
                else:
                        return True
        
        def mkdir(par, dir):
                ''' make a folder if necessary '''
                import system
                if (system.tag.exists(par + "/" + dir) == 0):
                        system.tag.addTag(parentPath=par, name=dir, tagType="Folder")
                return
        
        def pgdir(par, dir):
                ''' purge subfolders '''
                tags = system.tag.browseTags(parentPath=(par + "/" + dir))
                for tag in tags:
                        if (tag.isFolder()):
                                system.tag.removeTag(tag.fullPath)
                return
        
        def mktag(par, tag, typ, val):
                ''' make a tag if necessary then assign a value '''
                import system
                if (system.tag.exists(par + "/" + tag) == 0):
                        system.tag.addTag(parentPath=par, name=tag, tagType="MEMORY", dataType=typ)
                system.tag.write(par + "/" + tag, val)
                return
        
        def rmtag(par, tag):
                ''' remove a tag if it exists '''
                if (system.tag.exists(par + "/" + tag) == 1):
                        system.tag.removeTag(par + "/" + tag)
                return
        
        def mkblk(par, lst):
                ''' unpack a data block also saving each series as a comma separated string ''' 
                dic = {}
                for i, v in enumerate(lst):
                        for key in lst[i]:
                                try:
                                        dic[key].append(str(v[key]))
                                except:
                                        dic[key] = [str(v[key])]
                        mkdir(par, str(i))
                        mkdic(par + "/" + str(i), v)
                for key in dic:
                        mktag(par, "_" + key, "String", ','.join(dic[key])) 
                return
        
        def mkdic(par, dic):
                ''' recursively unpack a dictionary '''
                for key in dic.keys():
                        val = dic[key]
                        if (type(val) is dict):
                                mkdir(par, key)
                                mkdic(par + "/" + key, val) 
                        elif (type(val) is list): 
                                if (key == "data"): 
                                        mkdir(par, key)
                                        mkblk(par + "/" + key, val)
                                elif (key == "alerts"):
                                        mkdir(par, key)
                                        mkalt(par + "/" + key, val)
                                else:
                                        typ = "String"
                                        mktag(par, key, "String", ','.join(map(str, val)))                                
                        else:
                                if ((key == "time") or ("Time" in key) or ("expires" in key)):
                                        typ = "DateTime"
                                        val = int(val) * 1000
                                elif (isfloat(val)):
                                        typ = "Float4"
                                else:
                                        typ = "String"
                        mktag(par, key, typ, val)
                return
        
        def mkalt(par, lst):
                ''' unpack an alert block '''
                alt = []
                for i, v in enumerate(lst):
                        exp = int(v["expires"]) - int(res["currently"]["time"])
                        alt.append(v["title"] + " expires in " + friendlyTime(exp))
                        mkdir(par, str(i))
                        mkdic(par + "/" + str(i), v) 
                mktag(par, "_html", "String", '<br>'.join(alt)) 
                return

        def friendlyTime(i):
                ''' rounded time format '''
                i = i / 60
                d = 0
                if (int(i / 2880) > 0): 
                        d = int(i / 1440)
                h = int((i % 1440) / 60)
                m = i % 60
                s = ""
                #s = "%d %d %d %d " % (i, d, h, m)
                if (d > 0):
                        s = s + "%dd" % d
                if (h > 0):
                        s = s + "%dh" % h
                if (m > 0 and d == 0):
                        s = s + "%dm" % m
                return s

        ''' Main Function  '''

        # location details
        root = "forecast_io" # Ignition tag root folder
        APIKey = "yourapikeygoeshere"
        LatLon = "37.8267,-122.423" # Alcatraz

        # check root exists  
        mkdir("", root)

        # purge tags that may have vanished since last time
        mkdir(root, "alerts")
        pgdir(root, "alerts")
        mktag(root + "/alerts", "_html", "String", "")
        rmtag(root, "flags/darksky-unavailable")

        # fetch the API data
        json = system.net.httpGet("https://api.forecast.io/forecast/" + APIKey + "/" + LatLon)
        mktag(root, "_json", "String", json) 
        
        # map the payload 
        res = system.util.jsonDecode(json)
        mkdic(root, res)

        # additional derived values
        '''
        The API defines minutely, hourly and daily as optional and not available for all 
        locations. If you're working with fixed locations it'd be simpler to remove
        references to the missing data. For variable locations you'd have to use exception
        handling.  
        '''        
        cv = cmp(float(res["minutely"]["data"][0]["precipIntensity"]), 0)
        ct = int(res["currently"]["time"])
        st = None
        et = ct + 7 * 24 * 60 * 60
        for i, v in enumerate(res["minutely"]["data"] + res["hourly"]["data"] + res["daily"]["data"]):
                if (cmp(float(v["precipIntensity"]), 0) != cv):
                        if (st is None):
                                st = int(v["time"])
                                cv = cmp(float(v["precipIntensity"]), 0)
                        else:
                                et = int(v["time"])
                                break        
        if (st is None):
                mktag(root, "_nextChange", "String", "")
                mktag(root, "_nextChangeDate", "DateTime", 1000 * ct)
                mktag(root, "_nextChangeDuration", "String", "")
                mktag(root, "_nextChangeDurationDate", "DateTime", 1000 * ct)
        else:
                mktag(root, "_nextChange", "String", friendlyTime(st - ct))
                mktag(root, "_nextChangeDate", "DateTime", 1000 * st)        
                mktag(root, "_nextChangeDuration", "String", friendlyTime(et - st))
                mktag(root, "_nextChangeDurationDate", "DateTime", 1000 * et)
          
          sr = int(res["daily"]["data"][0]["sunriseTime"])
          ss = int(res["daily"]["data"][0]["sunsetTime"])
          mktag(root, "_daylightMinutes", "Int4", (ss - sr) / 60)
          mktag(root, "_daylightDuration", "String", friendlyTime(ss - sr))
          id = False
          if (ct > sr and ct < ss):
                  id = True
          mktag(root, "_isDaylight", "Boolean", id)          
          
        return

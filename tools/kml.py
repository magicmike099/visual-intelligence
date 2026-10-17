# Builds a Google My Maps layer (KML) from zones.json.
import json, sys, datetime
from shapely.geometry import LineString, Point
from xml.sax.saxutils import escape
Z=json.load(open(sys.argv[1] if len(sys.argv)>1 else 'zones.json'))
out=sys.argv[2] if len(sys.argv)>2 else 'paris-manif-17oct.kml'
LON0,LAT0,KX,KY=2.3488,48.8534,73305.0,110574.0
o=json.load(open('paris.json'))['origin']; LON0,LAT0,KX,KY=o
LL=lambda x,y:(LON0+x/KX,LAT0+y/KY)
COL={'confirmed':'2c36d4','likely':'1a73e8','possible':'069ac9','banned':'a83a7d','traffic':'b87f2f'}
LBL={'confirmed':'CONFIRMED','likely':'LIKELY','possible':'POSSIBLE','banned':'BANNED ROUTE','traffic':'TRAFFIC'}
FOLD=[('Confirmed and likely',('confirmed','likely')),('Possible routes (not agreed)',('possible',)),('Banned routes',('banned',)),('Traffic',('traffic',))]
def ring(z):
    g=Point(*z['center']) if z.get('center') else LineString(z['path'])
    poly=g.buffer(z['radius'],quad_segs=8).simplify(4)
    return ' '.join('%.6f,%.6f,0'%LL(x,y) for x,y in poly.exterior.coords)
D0=Z['day']
zday=lambda z:z.get('day',D0)
dlabel=lambda d:datetime.date.fromisoformat(d).strftime('%a %d %b')
OK=('official','observed','planned')
def desc(z):
    src=' · '.join(f'<a href="{Z["sources"][k]["url"]}">{escape(Z["sources"][k]["name"])}</a>' for k in z['src'])
    return f'<![CDATA[<b>{LBL[z["status"]]}</b> · {dlabel(zday(z))} {z["start"]}–{z["end"]}{" · last report "+z["seen"] if z.get("seen") else ""}<br><br>{escape(z["note"])}<br><br>Sources: {src}]]>'
k=['<?xml version="1.0" encoding="UTF-8"?>','<kml xmlns="http://www.opengis.net/kml/2.2"><Document>',
   f'<name>Paris protests and disruption {dlabel(D0)} to {dlabel(sorted({zday(z) for z in Z["zones"]})[-1])} (updated {escape(Z["updated"][5:16].replace("T"," "))})</name>',
   f'<description>{escape(Z["headline"])} Unofficial map built from press reports; check the Préfecture de police and RATP before travelling.</description>']
for s,c in COL.items():
    k.append(f'<Style id="{s}"><LineStyle><color>ff{c}</color><width>2</width></LineStyle><PolyStyle><color>{"55" if s=="possible" else "70"}{c}</color></PolyStyle></Style>')
k.append('<Style id="station"><IconStyle><color>ff2c36d4</color><scale>0.9</scale><Icon><href>https://maps.google.com/mapfiles/kml/shapes/rail.png</href></Icon></IconStyle></Style>')
for name,sts in FOLD:
    zs=[z for z in Z['zones'] if z['status'] in sts and zday(z)==D0 and z.get('outcome','official') in OK]
    if not zs: continue
    k.append(f'<Folder><name>{escape(name)}</name>')
    for z in zs:
        k.append(f'<Placemark><name>{escape(z["title"])} ({z["start"]}–{z["end"]})</name><description>{desc(z)}</description><styleUrl>#{z["status"]}</styleUrl><Polygon><outerBoundaryIs><LinearRing><coordinates>{ring(z)}</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>')
    k.append('</Folder>')
for d in sorted({zday(z) for z in Z['zones']}-{D0}):
    zs=[z for z in Z['zones'] if zday(z)==d and z.get('outcome','official') in OK]
    if not zs: continue
    k.append(f'<Folder><name>{escape(dlabel(d))}: road and transport disruption</name>')
    for z in zs:
        k.append(f'<Placemark><name>{escape(z["title"])} ({z["start"]}–{z["end"]})</name><description>{desc(z)}</description><styleUrl>#{z["status"]}</styleUrl><Polygon><outerBoundaryIs><LinearRing><coordinates>{ring(z)}</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>')
    k.append('</Folder>')
k.append('<Folder><name>Métro stations that may close</name>')
for s in Z['stations']:
    lon,lat=LL(*s['pos'])
    k.append(f'<Placemark><name>Métro {escape(s["name"])} (may close)</name><description>Lines {escape(s["lines"])}. {escape(Z["stationNote"])}</description><styleUrl>#station</styleUrl><Point><coordinates>{lon:.6f},{lat:.6f},0</coordinates></Point></Placemark>')
k.append('</Folder></Document></kml>')
open(out,'w').write('\n'.join(k))
print('wrote',out,sum(1 for z in Z['zones'] if z.get('outcome','official') in OK),'of',len(Z['zones']),'zones (unconfirmed and cancelled are left out)')

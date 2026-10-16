# Builds the installable app into ./pwa from index.html + data files.
import os, shutil, re, json, hashlib
from PIL import Image, ImageDraw, ImageFont
B=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(B,'pwa'); os.makedirs(OUT,exist_ok=True)
html=open(os.path.join(B,'index.html')).read()
html=html.replace('https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js','ml.js')
head='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><link rel="manifest" href="manifest.webmanifest"><link rel="icon" href="icon-192.png"><link rel="apple-touch-icon" href="icon-192.png"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="Manif Map"><meta name="apple-mobile-web-app-status-bar-style" content="default"><style>:root{color-scheme:light}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'
open(os.path.join(OUT,'index.html'),'w').write(head+html+'</body></html>')
for f in ['paris.json','zones.json','glyphs.json']: shutil.copy(os.path.join(B,f),OUT)
shutil.copy(os.path.join(B,'ml.js'),os.path.join(OUT,'ml.js'))
json.dump({"name":"Paris Manif Map","short_name":"Manif Map","description":"Protest and disruption zones in Paris, with routes that avoid them.","start_url":"./index.html","scope":"./","display":"standalone","orientation":"portrait","background_color":"#eef0ee","theme_color":"#1f4e8c","icons":[{"src":"icon-192.png","sizes":"192x192","type":"image/png","purpose":"any"},{"src":"icon-512.png","sizes":"512x512","type":"image/png","purpose":"any"},{"src":"icon-maskable-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]},open(os.path.join(OUT,'manifest.webmanifest'),'w'),indent=1)
def icon(size,pad):
    im=Image.new('RGB',(size,size),'#1f4e8c');d=ImageDraw.Draw(im);s=size
    m=s*pad  # safe margin
    # street-sign style: white pin with a red zone ring
    cx,cy=s/2,s/2; R=(s/2-m)
    d.ellipse([cx-R*.78,cy-R*.78,cx+R*.78,cy+R*.78],outline='#ffffff',width=max(2,int(s*.035)))
    d.ellipse([cx-R*.42,cy-R*.42,cx+R*.42,cy+R*.42],fill='#d4362c')
    d.ellipse([cx-R*.16,cy-R*.16,cx+R*.16,cy+R*.16],fill='#ffffff')
    return im
icon(192,.12).save(os.path.join(OUT,'icon-192.png'));icon(512,.12).save(os.path.join(OUT,'icon-512.png'));icon(512,.22).save(os.path.join(OUT,'icon-maskable-512.png'))
# service worker: precache the shell and data, zones network-first
files=['index.html','ml.js','paris.json','glyphs.json','manifest.webmanifest','icon-192.png','icon-512.png']
ver=hashlib.sha1(b''.join(open(os.path.join(OUT,f),'rb').read() for f in files)).hexdigest()[:10]
open(os.path.join(OUT,'sw.js'),'w').write('''// Offline cache for Paris Manif Map. Zones are fetched fresh when online, and the last copy is used offline.
const V='manif-%s';
const SHELL=%s;
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(SHELL.map(u=>new Request(u,{cache:'reload'})))).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==V&&k.startsWith('manif-')).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{
  const r=e.request;if(r.method!=='GET')return;const u=new URL(r.url);
  if(u.origin===location.origin&&u.pathname.endsWith('/zones.json')){
    e.respondWith(fetch(r).then(res=>{const cp=res.clone();caches.open(V).then(c=>c.put(r,cp));return res}).catch(()=>caches.match(r,{ignoreSearch:true})));return}
  if(u.origin===location.origin){
    e.respondWith(caches.match(r,{ignoreSearch:true}).then(h=>h||fetch(r)).catch(()=>caches.match('index.html')));return}
  if(u.hostname==='fonts.googleapis.com'||u.hostname==='fonts.gstatic.com'){
    e.respondWith(caches.open(V+'-fonts').then(c=>c.match(r).then(h=>h||fetch(r).then(res=>{c.put(r,res.clone());return res}))));}
});
'''%(ver,json.dumps(['./']+files)))
print('built',OUT,ver)

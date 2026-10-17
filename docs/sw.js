// Offline cache for Paris Manif Map. Zones are fetched fresh when online, and the last copy is used offline.
const V='manif-aa64c95029';
const SHELL=["./", "index.html", "ml.js", "paris.json", "glyphs.json", "manifest.webmanifest", "icon-192.png", "icon-512.png"];
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

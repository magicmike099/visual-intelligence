import json, math, heapq, re
d=json.load(open('paris.json'))
# clean station names
for p in d['places']:
    n=p[0]
    for pre in ['Arrêt ','Estación de ','Estación ','Noctilien ','Metro ','Métro ']:
        if n.startswith(pre): n=n[len(pre):]
    n=re.sub(r'\s*\[[^\]]*\]$','',n); n=n.replace(' (métro de Paris)','').replace(' (Métro de Paris)','')
    p[0]=n
seen=set();pl=[]
for p in d['places']:
    k=(p[0].lower(),p[1]=='s')
    if k in seen: continue
    seen.add(k);pl.append(p)
d['places']=pl
json.dump(d,open('paris.json','w'),separators=(',',':'),ensure_ascii=False)
LON0,LAT0,KX,KY=d['origin']
P=lambda lat,lon:((lon-LON0)*KX,(lat-LAT0)*KY)
N=d['nodes'];E=d['edges'];G=d['geo'];GO=d['geoOff']
nn=len(N)//2;adj=[[] for _ in range(nn)]
def epts(i):
    a,b=E[4*i],E[4*i+1]
    return [(N[2*a],N[2*a+1])]+[(G[2*k],G[2*k+1]) for k in range(GO[i],GO[i+1])]+[(N[2*b],N[2*b+1])]
L=[]
for i in range(len(E)//4):
    p=epts(i);l=sum(math.dist(p[j],p[j+1]) for j in range(len(p)-1));L.append(l)
    adj[E[4*i]].append((E[4*i+1],l,i));adj[E[4*i+1]].append((E[4*i],l*1,i))
def near(x,y):
    return min(range(nn),key=lambda k:(N[2*k]-x)**2+(N[2*k+1]-y)**2)
def route(a,b):
    # prefer big roads: weight by class
    dist={a:0};prev={};h=[(0,a)]
    while h:
        du,u=heapq.heappop(h)
        if u==b:break
        if du>dist[u]:continue
        for v,l,i in adj[u]:
            w=l*(1 if E[4*i+2]<=2 else 1.6)
            if du+w<dist.get(v,1e18): dist[v]=du+w;prev[v]=(u,i);heapq.heappush(h,(du+w,v))
    pts=[];u=b
    while u!=a:
        pu,i=prev[u];p=epts(i)
        if E[4*i]!=pu: p=p[::-1]
        pts=p[1:]+pts;u=pu
    return [(N[2*a],N[2*a+1])]+pts
def path(wps):
    ns=[near(*P(*w)) for w in wps];out=[]
    for a,b in zip(ns,ns[1:]):
        r=route(a,b); out+= r if not out else r[1:]
    # simplify: drop collinear-ish points
    return [[round(x),round(y)] for x,y in out]
def c(lat,lon): x,y=P(lat,lon);return [round(x),round(y)]
SRC={
 'sap':{'name':'Sortiraparis, updated 16 Oct','url':'https://www.sortiraparis.com/en/news/in-paris/articles/353967-october-17-mobilization-what-route-will-the-demonstration-in-paris-take'},
 'sap2':{'name':'Sortiraparis transport guide, updated 16 Oct','url':'https://www.sortiraparis.com/en/news/in-paris/articles/353907-strike-on-october-17-2026-yellow-vests-protests-by-high-school-students-transport-what-to-expect-in-paris'},
 'local':{'name':'The Local, 16 Oct','url':'https://www.thelocal.fr/20261016/map-what-are-the-routes-for-saturdays-paris-protest'},
 'yahoo':{'name':'Yahoo Actualités, banned sectors (night of 16 Oct)','url':'https://fr.news.yahoo.com/sport/mobilisation-17-octobre-interdiction-manifester-205841271.html'},
 'yahoo2':{'name':'Yahoo Actualités, why the route is stuck (16 Oct)','url':'https://fr.news.yahoo.com/sport/17-octobre-pourquoi-l-organisation-121828151.html'},
 'ban_ap':{'name':'Affiches Parisiennes (AFP), banned sectors, 16 Oct 19:31','url':'https://mesinfos.fr/75000-paris/manifestation-du-17-octobre-a-paris-plusieurs-secteurs-interdits-par-la-prefecture-341317.html'},
 'morandini':{'name':'Jean-Marc Morandini, banned sectors, 16 Oct','url':'https://www.jeanmarcmorandini.com/article-655004-inquietude-pour-le-17-octobre-la-prefecture-interdit-ce-soir-de-manifester-dans-plusieurs-secteurs-de-paris-mais-surtout-autour-de-l-elysee-et-matignon-mais-aussi-la-place-de-la-concorde.html'},
 'ratp':{'name':'Sortiraparis, 25 closed métro stations (RATP list)','url':'https://www.sortiraparis.com/en/news/in-paris/articles/353970-protests-on-saturday-october-17-25-paris-metro-stations-closed'},
 'ratp_x':{'name':'AlertesInfos on X, closed stations from 8:00','url':'https://x.com/AlertesInfos/status/2111160993007165603'},
 'mesinfos':{'name':'Affiches Parisiennes, 16 Oct','url':'https://mesinfos.fr/75000-paris/manifestation-du-17-octobre-a-paris-quel-parcours-pour-le-cortege-341287.html'},
}
SRC['aff17']={'name':'Affiches Parisiennes, routes and bans (17 Oct 09:53)','url':'https://mesinfos.fr/75000-paris/manifestations-du-17-octobre-a-paris-parcours-metro-quartiers-interdits-341322.html'}
SRC['psenat']={'name':'Public Sénat, 15 Oct','url':'https://www.publicsenat.fr/actualites/societe/17-octobre-le-mouvement-sorganise-peu-a-peu-entre-250-et-1000-actions-prevues-dans-toute-la-france'}
SRC['parisrouge']={'name':'Paris Rouge, route authorised (16 Oct 22:37)','url':'https://parisrouge.fr/2026/10/16/mobilisation-du-17-octobre-un-parcours-de-manifestation-parisienne-finalement-autorise-entre-republique-et-place-de-clichy/'}
SRC['aladom']={'name':'Aladom, gathering calls (updated 16 Oct 10:56)','url':'https://www.aladom.fr/actualites/secteur-service/11364/manifestations-du-17-octobre-2026-ou-sont-prevus-les-rassemblements-a-paris-rennes-lille-grenoble-et-bordeaux/'}
SRC['sap_fr']={'name':'Sortiraparis, route update (17 Oct 07:34)','url':'https://www.sortiraparis.com/actualites/a-paris/articles/353967-mobilisation-du-17-octobre-a-paris-quel-parcours-pour-la-manifestation-prevue-ce-samedi'}
SRC['sap_fr2']={'name':'Sortiraparis, what to expect (17 Oct)','url':'https://www.sortiraparis.com/actualites/a-paris/articles/353907-greve-du-17-octobre-2026-manif-gilets-jaunes-lyceens-transports-a-quoi-s-attendre-a-paris'}
B2R=[(48.8530,2.3693),(48.8590,2.3678),(48.8631,2.3666),(48.8673,2.3640)]
Z=[
 dict(id='bastille',title='Place de la Bastille: rally banned',short='Bastille: banned',kind='banned',status='banned',start='07:00',end='22:00',center=c(48.8532,2.3692),radius=380,
   note='A prefecture order bans any gathering at Place de la Bastille. The rally first called here for 14:00 is now reported to start at République instead. Bastille métro closes from 12:00. Calls to gather at Bastille and at Porte des Lilas are also circulating, with no times or routes published. People may still turn up, so expect police.',src=['sap_fr','sap_fr2','aff17','yahoo','morandini']),
 dict(id='republique',title='Rally at Place de la République, 14:00',short='République rally',kind='rally',status='confirmed',start='13:00',end='20:00',center=c(48.8676,2.3629),radius=300,
   note='Sortiraparis (citing Le Parisien), Affiches Parisiennes (09:53) and Paris Rouge all report the Gilets Jaunes and union march leaving République at 14:00, which matches the Gilets Jaunes call (Aladom). Student and high-school groups also gather here. Authorities expected 20,000 to 40,000 people in Paris (Public Sénat, 15 Oct).',src=['sap_fr','sap_fr2','aff17','parisrouge','aladom','psenat']),
 dict(id='r2clichy',title='March République → Place de Clichy (route authorised by the prefecture)',short='République to Clichy',kind='march',status='confirmed',start='14:00',end='20:00',path=path([(48.8676,2.3629),(48.8760,2.3582),(48.8838,2.3500),(48.8829,2.3440),(48.8822,2.3378),(48.8837,2.3323),(48.8836,2.3273)]),radius=150,
   note='Reported route: from République at 14:00 up Boulevard Magenta, past Barbès-Rochechouart, Anvers and Pigalle along Boulevard de Clichy to Place de Clichy. Sortiraparis, Affiches Parisiennes (09:53) and Paris Rouge (16 Oct, evening) all report this route as the one the prefecture authorised after talks failed; the Barbès, Anvers, Pigalle and Blanche stations close from 12:00.',src=['sap_fr','sap_fr2','aff17','parisrouge','mesinfos']),
 dict(id='r2nation',title='Student march République → Nation (not confirmed)',short='Students to Nation',kind='march',status='possible',start='14:00',end='20:00',path=path([(48.8676,2.3629),(48.8620,2.3722),(48.8576,2.3800),(48.8549,2.3850),(48.8520,2.3900),(48.8490,2.3952)]),radius=130,
   note='Affiches Parisiennes (09:53) says the student and high-school march (Interfac) goes from République to Nation along Boulevard Voltaire, with no start time given. The prefecture offered this route after banning République to Concorde (Public Sénat, 15 Oct). Sortiraparis instead says Interfac follows the Clichy route, so treat this as unconfirmed.',src=['aff17','psenat','sap_fr']),
 dict(id='grandsbd',title='Banned route: Grands Boulevards to Concorde',kind='banned',status='banned',start='13:00',end='21:00',path=path([(48.8680,2.3625),(48.8697,2.3541),(48.8705,2.3485),(48.8720,2.3390),(48.8710,2.3318),(48.8699,2.3247),(48.8660,2.3215)]),radius=170,
   note='The prefecture banned République → Concorde and Opéra → Bastille along the Grands Boulevards. A ban usually means heavy police presence, and unauthorised groups can still try to gather.',src=['local','sap']),
 dict(id='opera',title='Place de l\'Opéra (original Gilets Jaunes start)',kind='banned',status='banned',start='12:30',end='17:00',center=c(48.8710,2.3318),radius=250,
   note='First announced as the Gilets Jaunes meeting point (speeches from 13:00), then banned. Some people may still turn up.',src=['local']),
 dict(id='rex',title='17 October 1961 memorial march from the Grand Rex',kind='march',status='likely',start='16:30',end='19:00',path=path([(48.8706,2.3477),(48.8693,2.3527),(48.8662,2.3523),(48.8580,2.3478),(48.8550,2.3460),(48.8534,2.3446)]),radius=120,
   note='March for the 65th anniversary of 17 October 1961 starts at the Rex cinema (2nd arr.) at 16:30. The exact route is not published; the line shown is the usual way to Pont Saint-Michel.',src=['sap2']),
 dict(id='stmichel',title='Gathering at Pont Saint-Michel',kind='rally',status='confirmed',start='18:00',end='20:30',center=c(48.8534,2.3446),radius=220,
   note='Commemoration gathering at 18:30 (5th/6th arr.).',src=['sap2']),
 dict(id='champs',title='Gatherings banned: Champs-Élysées and Concorde',short='Banned: Champs-Élysées',kind='banned',status='banned',start='07:00',end='22:00',path=path([(48.8738,2.2950),(48.8698,2.3076),(48.8656,2.3212)]),radius=200,
   note='The prefecture banned undeclared gatherings on the Champs-Élysées and Place de la Concorde from 07:00 to 22:00 (fine of 135 euros). A Gilets Jaunes march had been requested here. Expect heavy police presence.',src=['yahoo','ban_ap','morandini']),
 dict(id='ban_elysee',title='Gatherings banned: around the Élysée and Interior Ministry',short='Banned: Élysée',kind='banned',status='banned',start='07:00',end='22:00',center=c(48.8708,2.3176),radius=300,
   note='Undeclared gatherings are banned around the Élysée, the Interior Ministry and nearby sites from 07:00 to 22:00. The exact perimeter was not published; the circle is an approximation.',src=['yahoo','ban_ap','morandini']),
 dict(id='ban_gov',title='Gatherings banned: Assemblée nationale, Matignon, Sénat',short='Banned: government quarter',kind='banned',status='banned',start='07:00',end='22:00',path=path([(48.8610,2.3187),(48.8487,2.3205),(48.8486,2.3371)]),radius=250,
   note='Undeclared gatherings are banned around the National Assembly, Matignon and the Senate from 07:00 to 22:00. The exact perimeters were not published; the corridor is an approximation.',src=['yahoo','ban_ap','morandini']),
 dict(id='ban_chatelet',title='Gatherings banned: Châtelet, Les Halles, Hôtel de Ville',short='Banned: Châtelet',kind='banned',status='banned',start='07:00',end='22:00',center=c(48.8584,2.3470),radius=500,
   note='Undeclared gatherings are banned at Place du Châtelet, the Les Halles area, the Hôtel de Ville, the Palais de Justice and the Préfecture de Police from 07:00 to 22:00. The exact perimeter was not published; the circle is an approximation.',src=['yahoo','morandini']),
 dict(id='ban_bourse',title='Gatherings banned: Place de la Bourse',short='Banned: Bourse',kind='banned',status='banned',start='07:00',end='22:00',center=c(48.8691,2.3412),radius=220,
   note='Undeclared gatherings are banned around Place de la Bourse from 07:00 to 22:00. The exact perimeter was not published.',src=['yahoo','morandini']),
 dict(id='ban_italie',title='Gatherings banned: Place d\'Italie',short='Banned: Place d\'Italie',kind='banned',status='banned',start='07:00',end='22:00',center=c(48.8312,2.3555),radius=300,
   note='Undeclared gatherings are banned around Place d\'Italie from 07:00 to 22:00. The exact perimeter was not published.',src=['yahoo','morandini']),
 dict(id='maillot',title='Taxi protest at Porte Maillot',kind='traffic',status='likely',start='06:00',end='20:00',center=c(48.8780,2.2830),radius=400,
   note='About 2,000 taxis rolling from Porte Maillot towards Roissy-CDG since Thursday. Road traffic to the airports may be slow; RER B is the alternative.',src=['sap2','local']),
]
STATIONS=[('Charles de Gaulle–Étoile',48.8739,2.2950,'1, 2, 6, RER A','08:00'),('Argentine',48.8756,2.2896,'1','08:00'),('George V',48.8719,2.3006,'1','08:00'),('Tuileries',48.8645,2.3296,'1','08:00'),('Franklin D. Roosevelt',48.8687,2.3099,'1, 9','08:00'),('Champs-Élysées–Clemenceau',48.8675,2.3144,'1, 13','08:00'),('Concorde',48.8656,2.3212,'1, 8, 12','08:00'),('Opéra',48.8707,2.3317,'3, 7, 8','08:00'),("Chaussée d'Antin–La Fayette",48.8730,2.3336,'7, 9','08:00'),('Pyramides',48.8661,2.3344,'7, 14','08:00'),('Madeleine',48.8700,2.3249,'8, 12, 14','08:00'),('Miromesnil',48.8731,2.3150,'9, 13','08:00'),('Assemblée nationale',48.8609,2.3200,'12','08:00'),('Solférino',48.8586,2.3228,'12','08:00'),('Rue du Bac',48.8559,2.3257,'12','08:00'),('Varenne',48.8571,2.3149,'13','08:00'),
 ('Bastille',48.8532,2.3692,'1, 5, 8','12:00'),('Anvers',48.8828,2.3441,'2','12:00'),('Blanche',48.8838,2.3330,'2','12:00'),('Barbès–Rochechouart',48.8838,2.3499,'2, 4','12:00'),('Pigalle',48.8820,2.3379,'2, 12','12:00'),('Bourse',48.8686,2.3411,'3','12:00'),('Chemin Vert',48.8571,2.3683,'8','12:00'),('Saint-Sébastien–Froissart',48.8610,2.3673,'8','12:00'),('Filles du Calvaire',48.8632,2.3665,'8','12:00')]
st=[{'name':n,'lines':l,'pos':c(a,b),'from':f} for n,a,b,l,f in STATIONS]
out=dict(updated='2026-10-17T12:25:00+02:00',day='2026-10-17',headline='Route authorised by the prefecture: from République at 14:00 along Boulevard Magenta, Barbès and Boulevard de Clichy to Place de Clichy. A student march towards Nation is also reported but not confirmed. The Bastille rally is banned. 25 métro stations are closed, and undeclared gatherings are banned in central Paris until 22:00.',
  stations=st,stationTitle='Métro stations closed on Saturday',stationNote='RATP announced these closures at the request of the Préfecture de police: trains pass through without stopping and there are no connections. The stations closed from 12:00 reopen only when the prefecture allows it. République, Oberkampf and Richard-Lenoir are not on the list, but the prefecture can add closures at short notice. Line 6 ends at Kléber from 08:00. Station positions on the map are approximate. Several bus routes will be diverted.',
  traffic='No public transport strike is announced. Slow-roll road protests are possible on the Périphérique and airport motorways, and the interior ministry says blockades of key roads and facilities will not be tolerated. School holidays start, so expect heavy road traffic out of Paris.',
  sources=SRC,zones=Z)
json.dump(out,open('zones.json','w'),ensure_ascii=False,indent=0)
print({z['id']:len(z.get('path',[])) for z in Z})

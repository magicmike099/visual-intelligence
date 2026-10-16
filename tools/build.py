import pyarrow.parquet as pq, json, math
from shapely import wkb
from shapely.geometry import LineString
from shapely.ops import substring
LON0,LAT0=2.3488,48.8534
KX=math.cos(math.radians(LAT0))*111320; KY=110574
def P(lon,lat): return (round((lon-LON0)*KX), round((lat-LAT0)*KY))
X0,Y0,X1,Y1=2.24,48.812,2.46,48.904
seg=pq.read_table('seg.parquet').to_pylist()
WALK={'primary':1,'secondary':2,'tertiary':3,'residential':4,'living_street':4,'unclassified':4,'pedestrian':5,'unknown':4}
DRAWONLY={'motorway':0,'trunk':0}
nodes={};nodexy=[]
def nid(cid,xy):
    if cid not in nodes:
        nodes[cid]=len(nodexy); nodexy.append(xy)
    return nodes[cid]
names=[];nameidx={}
def nm(s):
    if not s: return -1
    if s not in nameidx: nameidx[s]=len(names); names.append(s)
    return nameidx[s]
edges=[];geo=[];extra={'rail':[],'hw':[]}
for s in seg:
    g=wkb.loads(s['geometry'])
    if g.geom_type!='LineString': continue
    c=g.centroid
    if not (X0<c.x<X1 and Y0<c.y<Y1): continue
    cl=s['class']
    if s['subtype']=='rail':
        if cl in ('subway','tram','light_rail','standard_gauge'):
            extra['rail'].append([cl=='subway' and 1 or 2,[P(*p) for p in g.simplify(0.00003).coords]])
        continue
    if cl in DRAWONLY:
        extra['hw'].append([[P(*p) for p in g.simplify(0.00003).coords], (s['names'] or {}).get('primary') or ''])
        continue
    if cl not in WALK: continue
    conns=sorted(s['connectors'] or [], key=lambda c:c['at'])
    if len(conns)<2: continue
    name=nm((s['names'] or {}).get('primary'))
    for a,b in zip(conns,conns[1:]):
        if b['at']-a['at']<=0: continue
        sub=substring(g,a['at'],b['at'],normalized=True)
        if sub.geom_type!='LineString': continue
        pts=[P(*p) for p in sub.simplify(0.00002).coords]
        A=nid(a['connector_id'],pts[0]); B=nid(b['connector_id'],pts[-1])
        if A==B: continue
        edges.append((A,B,WALK[cl],name)); geo.append(pts[1:-1])
# largest component
import collections
adj=collections.defaultdict(list)
for i,(a,b,_,_) in enumerate(edges): adj[a].append(b); adj[b].append(a)
comp={};best=None
for n in range(len(nodexy)):
    if n in comp: continue
    st=[n];comp[n]=n;cnt=0
    while st:
        u=st.pop();cnt+=1
        for v in adj[u]:
            if v not in comp: comp[v]=n;st.append(v)
    if best is None or cnt>best[1]: best=(n,cnt)
keep=[i for i,e in enumerate(edges) if comp[e[0]]==best[0]]
# reindex nodes
used=sorted({edges[i][0] for i in keep}|{edges[i][1] for i in keep})
remap={o:i for i,o in enumerate(used)}
N=[];[N.extend(nodexy[o]) for o in used]
E=[];G=[];GO=[0]
for i in keep:
    a,b,c,n=edges[i]; E.extend([remap[a],remap[b],c,n])
    for p in geo[i]: G.extend(p)
    GO.append(len(G)//2)
# water
water=[]
for w in pq.read_table('water.parquet').to_pylist():
    g=wkb.loads(w['geometry'])
    if g.geom_type in('Polygon','MultiPolygon') and g.area>2e-7:
        polys=[g] if g.geom_type=='Polygon' else list(g.geoms)
        for p in polys:
            p=p.simplify(0.00003)
            if p.is_empty: continue
            water.append([P(*q) for q in p.exterior.coords])
    elif g.geom_type=='LineString' and w['class'] in ('river','canal'):
        water.append({'l':[P(*q) for q in g.simplify(0.00003).coords]})
# places
places=[]
for p in pq.read_table('places.parquet').to_pylist():
    bc=p['basic_category']; conf=p['confidence'] or 0
    k={'train_station':'s','public_transit_facility_or_service':'s','monument':'m','museum':'u','park':'p','college_university':'c'}.get(bc)
    if not k: continue
    if k in 'upc' and conf<0.9: continue
    if k=='m' and conf<0.75: continue
    g=wkb.loads(p['geometry']); n=(p['names'] or {}).get('primary')
    if not n or g.geom_type!='Point': continue
    if not (X0<g.x<X1 and Y0<g.y<Y1): continue
    places.append([n,k,*P(g.x,g.y)])
out={'origin':[LON0,LAT0,KX,KY],'nodes':N,'edges':E,'geo':G,'geoOff':GO,'names':names,'rail':extra['rail'],'hw':extra['hw'],'water':water,'places':places}
json.dump(out,open('paris.json','w'),separators=(',',':'),ensure_ascii=False)
print(len(N)//2,'nodes',len(E)//4,'edges',len(G)//2,'geo pts',len(places),'places',len(water),'water',best)

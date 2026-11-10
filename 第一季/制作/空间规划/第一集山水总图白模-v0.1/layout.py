"""Landscape-first reference coordinates, metres; inferred dimensions, not surveyed."""
import numpy as np, math
NODES=np.array([[-260,830],[-185,655],[2,482],[48,318],[-63,147],[-75,-17],[52,-183],[237,-320],[345,-474],[365,-665]],float)
def catmull(p,n=160):
 out=[]
 for i in range(len(p)-1):
  a=p[max(0,i-1)];b=p[i];c=p[i+1];d=p[min(len(p)-1,i+2)]
  for t in np.linspace(0,1,n,endpoint=False):out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
 return np.vstack([out,p[-1]])
RAW=catmull(NODES);DIST=np.r_[0,np.cumsum(np.linalg.norm(np.diff(RAW,axis=0),axis=1))];LENGTH=float(DIST[-1]);SS=np.linspace(0,1,1501);XY=np.column_stack([np.interp(SS*LENGTH,DIST,RAW[:,j]) for j in range(2)])
TANG=np.gradient(XY,axis=0);TANG/=np.linalg.norm(TANG,axis=1)[:,None];NORMAL=np.column_stack([-TANG[:,1],TANG[:,0]])
def center(s):return np.column_stack([np.interp(np.atleast_1d(s),SS,XY[:,j]) for j in range(2)])
def basis(s):
 t=np.array([np.interp(s,SS,TANG[:,j]) for j in range(2)]);t/=np.linalg.norm(t);return t,np.array([-t[1],t[0]])
def water_z(s):
 # Pools stay level. Elevation changes are concentrated in the narrow connecting reaches.
 s=np.asarray(s);z=np.full_like(s,96.,dtype=float)
 for a,b,drop in [(.12,.23,16),(.23,.40,30),(.40,.55,12),(.72,.87,20),(.975,1.,10)]:
  t=np.clip((s-a)/(b-a),0,1);z-=drop*(t*t*(3-2*t))
 return z
def width(s,side):
 s=np.asarray(s)
 return (9+17*np.exp(-((s-.065)/.065)**2)+ (37 if side>0 else 49)*np.exp(-((s-.615)/.095)**2)+4*np.exp(-((s-.93)/.05)**2))
def extent(s,side):return 155+38*np.sin(np.asarray(s)*math.pi)**2+(15 if side>0 else 0)
def point(s,d=0,z=None):
 xy=center(s)[0]+basis(s)[1]*d
 return np.r_[xy,water_z(s) if z is None else z]
def nearest(xy):
 xy=np.atleast_2d(xy);ids=[]
 for i in range(0,len(xy),384):ids.extend(np.argmin(np.sum((xy[i:i+384,None,:]-XY[None,:,:])**2,axis=2),axis=1))
 ids=np.array(ids);delta=xy-XY[ids];d=np.sum(delta*NORMAL[ids],axis=1)
 # Project onto the local tangent instead of quantising elevation to the nearest 1.2m station.
 continuous=np.clip(SS[ids]+np.sum(delta*TANG[ids],axis=1)/LENGTH,0,1)
 return continuous,d,ids
def natural(xy,known=None):
 s,d,_=nearest(xy) if known is None else known;side=np.where(d>=0,1,-1);w=np.where(d>=0,width(s,1),width(s,-1));q=np.abs(d)-w
 z=water_z(s)+1.8+.035*np.maximum(q,0)+.32*np.maximum(q-50,0)
 # Offset cloud ridges, branching shoulders and open low saddles.
 ridge=(78*np.exp(-((s-.27)/.105)**2)+48*np.exp(-((s-.73)/.12)**2))*np.exp(-((q-112)/44)**2)*(side>0)
 ridge+=(55*np.exp(-((s-.38)/.075)**2)+34*np.exp(-((s-.11)/.11)**2))*np.exp(-((q-125)/42)**2)*(side<0)
 z+=ridge
 inner=q<0;z=np.where(inner,water_z(s)-2.4+1.4*np.exp(np.minimum(q,0)/3),z)
 return z
def make_courts():
 rows=[]
 # Curated clusters, interruptions at valley, public banks and crossings.
 clusters=[('School',1,[.025,.055,.085,.115],45),('School',-1,[.04,.075,.11],45),
 ('West-neighbourhood',1,[.435,.467,.50,.54],43),('East-neighbourhood',-1,[.45,.483,.519,.55],46),
 ('Water-bay',1,[.575,.61,.645,.68,.715],44),('Water-bay',-1,[.58,.615,.65,.687,.72],45),
 ('Lower-lane',1,[.765,.798,.83,.86,.89,.924,.954],41),('Lower-lane',-1,[.775,.808,.84,.875,.908,.94,.968],42),
 ('Slope-neighbourhood',1,[.47,.51,.66,.70,.74],97),('Slope-neighbourhood',-1,[.49,.535,.69,.735,.79,.84],96)]
 for group,side,stations,offset in clusters:
  # Small local clusters share an axis, with only deliberate bend changes.
  for j,s in enumerate(stations):
   d=side*(float(width(s,side))+offset+([0,3,-2,2][j%4] if offset<80 else 0));xy=point(s,d)[:2]
   orient_s=stations[(j//2)*2] if group!='School' else .065;t,n=basis(orient_s);n=n*side
   floor=float(water_z(s)+(13 if group=='Slope-neighbourhood' else 3.5));name=f'{group}-{side:+d}-{j:02}'
   if group=='Water-bay' and side==1 and j==1:name='Two-level-water-court'
   if group=='Lower-lane' and side==1 and j==6:name='Zhixia-home'
   if group=='Lower-lane' and side==-1 and j==6:name='Repair-workshop'
   sizes=([17,16] if group=='School' else ([13,14] if group=='Slope-neighbourhood' else [[15,15],[17,15],[14,16],[16,14]][j%4]))
   if name=='Two-level-water-court':sizes=[18.5,18.5]
   rows.append({'id':name,'s':s,'side':side,'d':d,'center':xy.tolist(),'tangent':t.tolist(),'outward':n.tolist(),'floor':floor,'half_size':sizes,'group':group})
 return rows
COURTS=make_courts()
UPPER_COURT=next(p for p in COURTS if p['id']=='Two-level-water-court')
HILL_ARCS={}
for side in [-1,1]:
 hs=np.linspace(.40,.88,1001);hp=np.array([point(s,side*(width(s,side)+72))[:2] for s in hs]);ha=np.r_[0,np.cumsum(np.linalg.norm(np.diff(hp,axis=0),axis=1))];HILL_ARCS[side]=(hs,ha)
def hill_z(s,side=1):
 hs,ha=HILL_ARCS[side];anchor=np.interp(UPPER_COURT['s'],hs,ha)
 return UPPER_COURT['floor']+8.4+.035*(anchor-np.interp(s,hs,ha))
for p in COURTS:
 if p['group']=='Slope-neighbourhood':p['floor']=float(hill_z(p['s'],p['side']))
LINKS=[]
for p in COURTS:
 sc=np.array(p['half_size'])/18.5;end=np.array(p['center'])-np.array(p['outward'])*18*sc[1]
 q=72 if p['group']=='Slope-neighbourhood' else 7
 start=point(p['s'],p['side']*(width(p['s'],p['side'])+q))[:2]
 LINKS.append((start,end,float(hill_z(p['s'],p['side']) if q==72 else water_z(p['s'])+2.1),p['floor'],2.0,'hill' if q==72 else 'bank',p['side']))
for side,stations in [(1,[.423,.752]),(-1,[.433,.568,.852])]:
 for s in stations:
  a=point(s,side*(width(s,side)+7))[:2];b=point(s,side*(width(s,side)+72))[:2];LINKS.append((a,b,float(water_z(s)+2.1),float(hill_z(s,side)),2.4,'connector',side))
def terrain(xy,known=None):
 xy=np.atleast_2d(xy);z=natural(xy,known)
 s,d,_=nearest(xy) if known is None else known
 # A continuous bench carries the hill street; it is cut into the slope, not draped over its peaks.
 q=np.abs(d)-np.where(d>=0,width(s,1),width(s,-1));bank_q=q.copy();active=((d>=0)&(s>=.415)&(s<=.77))|((d<0)&(s>=.425)&(s<=.87))
 hz=np.where(d>=0,hill_z(s,1),hill_z(s,-1))
 a=np.clip((np.abs(q-72)-4)/9,0,1);a=a*a*(3-2*a);a=np.where(active,a,1);z=z*a+hz*(1-a)
 for p in COURTS:
  local=xy-np.array(p['center']);u=local@np.array(p['tangent']);v=local@np.array(p['outward']);q=np.maximum(np.abs(u)-(p['half_size'][0]+3),np.abs(v)-(p['half_size'][1]+3));a=np.clip(q/8,0,1);a=a*a*(3-2*a);z=z*a+p['floor']*(1-a)
 # Hard court footprints win over every other court's feathered terrain transition.
 for p in COURTS:
  delta=xy-np.array(p['center']);u=delta@np.array(p['tangent']);v=delta@np.array(p['outward']);inside=(np.abs(u)<=p['half_size'][0]+2)&(np.abs(v)<=p['half_size'][1]+2);z=np.where(inside,p['floor'],z)
 # Walking surfaces are hard constraints too: a hill/court feather cannot raise a road.
 bank=np.abs(bank_q-7)<=4.;hill=(np.abs(bank_q-72)<=3.8)&active
 z=np.where(bank,water_z(s)+2.1,z);z=np.where(hill,hz,z)
 for a,b,za,zb,hw,kind,side in LINKS:
  ab=b-a;t=np.clip(np.sum((xy-a)*ab,axis=1)/np.dot(ab,ab),0,1);distance=np.linalg.norm(xy-(a+t[:,None]*ab),axis=1)
  length=np.linalg.norm(ab);lead=3.8 if kind=='hill' else 5.;u=np.clip((t*length-lead)/(length-(10 if kind=='connector' else lead)),0,1)
  base=hill_z(s,side) if kind=='hill' else water_z(s)+2.1;dest=hill_z(s,side) if kind=='connector' else zb
  z=np.where(distance<=hw,base+(dest-base)*u,z)
 z=np.where(bank,water_z(s)+2.1,z);z=np.where(hill,hz,z)
 return z
def pathline(svals,side,extra=7):
 result=np.array([point(s,side*(width(s,side)+extra)) for s in svals]);result[:,2]=terrain(result[:,:2])+.16
 return result

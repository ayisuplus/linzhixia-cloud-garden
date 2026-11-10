"""v15 connected side-water network. Inferred spatial reference, no fluid simulation."""
import bpy,sys,json,math,hashlib
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);D=Path(__file__).parent
sys.path.insert(0,str(D.parent/'第一集山水总图白模-v0.1'));import layout as L
sys.path.insert(0,str(D.parent/'第一集水巷街桥-v0.1'));import geometry as G
SRC=R/'视频制作/第一集云山园巷-20261024-v0.1';O=R/'视频制作/第一集枝水园城-20261024-v0.1';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SRC/'cloud-garden-route-58s-v14.blend'));S=bpy.context.scene
for m in bpy.data.materials:
 if ' / ' in m.name:G.M[m.name.split(' / ')[-1].split(' [')[0]]=m
def col(name):c=bpy.data.collections.new(name);S.collection.children.link(c);return c
W=col('24 Connected branch waters');B=col('25 Branch stone banks and road crossings')
def verts(o):
 a=np.empty(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);a=a.reshape(-1,3);m=np.array(o.matrix_world);return a@m[:3,:3].T+m[:3,3]
def combine(obs):
 vs=[];fs=[];names=[]
 for ob in obs:
  off=len(vs);vs.extend(verts(ob));fs.extend(tuple(off+i for i in f.vertices) for f in ob.data.polygons);names.extend([ob.name]*len(ob.data.polygons))
 return BVHTree.FromPolygons([Vector(x) for x in vs],fs),names
ground=bpy.data.objects['Continuous stable cloud terrain / river bed and inhabited slopes'];gv=verts(ground);oldb,_=combine([ground])
def height(b,xy):
 h=b.ray_cast(Vector((*xy,500)),Vector((0,0,-1)),1000)[0];return None if h is None else float(h.z)
roads=[o for o in S.objects if o.type=='MESH' and (o.name.startswith(('Continuous bank lane','Upper slope street','Bank to slope connector','Shared waterside landing')) or o.name.endswith('entry connection') or 'walking deck' in o.name)]
rb,rnames=combine(roads)
def smooth(x):x=np.clip(x,0,1);return x*x*x*(10+x*(-15+6*x))
specs=[
 ('N1 East neighbourhood water lane',1,[.425,.445,.473,.507,.53,.545],[0,19,23,22,15,0],4.4,'stepped'),
 ('N2 West courtyard runnel',-1,[.448,.467,.498,.525,.552],[0,20,22,20,0],3.8,'stepped'),
 ('N3 East quiet basin',1,[.565,.583,.596,.610,.621],[0,30,35,31,0],4.0,'pool'),
 ('N4 West bay garden loop',-1,[.647,.666,.686,.710,.726],[0,24,27,22,0],4.2,'pool'),
 ('N5 Lower stepped water lane',-1,[.753,.772,.798,.827,.842,.852],[0,18,22,21,14,0],3.6,'stepped')]
data={'source_sha256':hashlib.sha256((SRC/'cloud-garden-route-58s-v14.blend').read_bytes()).hexdigest(),'branches':[],'crossings':[],'relocated_plants':[],'foundations':[]}
newz=gv[:,2].copy();allwater=[];footprints=[]
for ident,side,knots,offsets,width,kind in specs:
 ss=np.linspace(knots[0],knots[-1],max(120,int((knots[-1]-knots[0])*L.LENGTH/.65)))
 ix=np.clip(np.searchsorted(knots,ss)-1,0,len(knots)-2);u=smooth((ss-np.array(knots)[ix])/(np.array(knots)[ix+1]-np.array(knots)[ix]));dd=(np.array(offsets)[ix]*(1-u)+np.array(offsets)[ix+1]*u)*side
 xy=np.array([L.point(s,d)[:2] for s,d in zip(ss,dd)]);t=np.gradient(xy,axis=0);t/=np.linalg.norm(t,axis=1)[:,None];nn=np.column_stack([-t[:,1],t[:,0]])
 base=L.water_z(ss);zz=base.copy()
 if kind=='stepped':
  step=1.0 if ident.startswith(('N1','N2')) else 1.25;h=(base[0]-base)/step;k=np.floor(h);zz=base[0]-step*(k+smooth((h-k-.72)/.28));tail=smooth((ss-(ss[-1]-.008))/.008);zz=zz*(1-tail)+base*tail
 zz+=.018
 widths=np.full(len(ss),width)
 if ident.startswith('N3'):widths+=4.5*np.exp(-((ss-.596)/.009)**4)
 if ident.startswith('N4'):widths+=2.0*np.exp(-((ss-.688)/.012)**4)
 bankL=xy-nn*widths[:,None]/2;bankR=xy+nn*widths[:,None]/2
 vs=np.array([np.r_[p,z] for pair,z in zip(np.stack([bankL,bankR],axis=1),zz) for p in pair]);fs=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(ss)-1)]
 water=G.mesh(ident+' connected water',vs,fs,'water',W,False);allwater.append(water)
 # Dense sample distance carves a real trench beneath each water strip. The
 # transition extends beyond the visible bank to cover 2.5m terrain triangles.
 nearest=np.empty(len(gv),int);dist=np.empty(len(gv))
 for start in range(0,len(gv),512):
  ar=np.sum((gv[start:start+512,None,:2]-xy[None,:,:])**2,axis=2);idx=np.argmin(ar,axis=1);nearest[start:start+512]=idx;dist[start:start+512]=np.sqrt(ar[np.arange(len(idx)),idx])
 hw=widths[nearest]/2;inner=dist<=hw+1.8;blend=1-smooth((dist-hw-1.8)/3.0);bed=zz[nearest]-1.35;goal=gv[:,2]*(1-blend)+bed*blend;newz=np.minimum(newz,goal)
 # Banks have physical thickness. Their top matches local ground/road so
 # crossing paths do not meet an arbitrary high wall. Mouths remain open.
 main=bpy.data.objects['Main water spine / upstream to downstream collection'];mv=verts(main).reshape(-1,2,3);mi=np.clip(np.round(ss*(len(mv)-1)).astype(int),0,len(mv)-1);mainwidth=np.linalg.norm(mv[mi,1,:2]-mv[mi,0,:2],axis=1)
 away=abs(dd)>mainwidth/2+widths/2+1
 for sign in [-1,1]:
  edge=xy+nn*sign*(widths/2+.15)[:,None];outer=xy+nn*sign*(widths/2+.65)[:,None];bv=[];tops=[]
  for i,(a,b) in enumerate(zip(edge,outer)):
   gh=height(oldb,b);rh=height(rb,b);top=max(zz[i]+.12,gh if gh is not None else zz[i]+1.6)
   if rh is not None:top=min(top,rh-.10)
   tops.append(top);bv.extend([(*a,zz[i]-1.6),(*b,zz[i]-1.6),(*a,top),(*b,top)])
  bf=[]
  for i in range(len(ss)-1):
   if not(away[i] and away[i+1]):continue
   k0=4*i;bf.extend([(k0+2,k0+3,k0+7,k0+6),(k0,k0+4,k0+6,k0+2),(k0+1,k0+3,k0+7,k0+5)])
  G.mesh(ident+f' stone bank {sign}',bv,bf,'stone',B)
 # Discover crossings against actual saved walking faces, not guessed stations.
 hits=[]
 for i,p in enumerate(xy):
  h=rb.ray_cast(Vector((*p,500)),Vector((0,0,-1)),1000)
  if h[0] is not None and away[i]:hits.append((i,rnames[h[2]],float(h[0].z)))
 runs=[]
 for item in hits:
  if runs and item[0]<=runs[-1][-1][0]+2 and item[1]==runs[-1][-1][1]:runs[-1].append(item)
  else:runs.append([item])
 for ci,run in enumerate(runs):
  i=run[len(run)//2][0];roadname=run[0][1];top=min(h[2] for h in run);halfspan=widths[i]/2+.8;crossangle=math.atan2(nn[i,1],nn[i,0]);ident2=f'{ident} crossing {ci+1}'
  # A visible stone soffit reinforces the old road deck. Grounded abutments
  # stand outside the water, leaving the branch channel open beneath.
  roadb,_=combine([bpy.data.objects[roadname]])
  def underside(p):
   hit=roadb.ray_cast(Vector((*p,zz[i]-8)),Vector((0,0,1)),80)[0]
   if hit is None:hit=roadb.find_nearest(Vector((*p,top)),5)[0]
   return float(hit.z) if hit is not None else top
  soffit=G.box(ident2+' supporting soffit',(*xy[i],top-.32),(2*halfspan,2.2,.22),'stone',B,crossangle)
  for vi,v in enumerate(soffit.data.vertices):v.co.z=underside(v.co[:2])+.025-(.32 if vi<4 else 0)
  soffit.data.update()
  for side2 in [-1,1]:
   p=xy[i]+nn[i]*side2*(widths[i]/2+.65);bottom=zz[i]-1.8;ab=G.box(ident2+' bank abutment',(*p,(top-.35+bottom)/2),(.8,2.2,top-.35-bottom),'stone',B,crossangle)
   for v in list(ab.data.vertices)[4:]:v.co.z=underside(v.co[:2])-.27
   ab.data.update()
  data['crossings'].append({'id':ident2,'road':roadname,'center':xy[i].tolist(),'top':top,'water_z':float(zz[i]),'clearance_under_soffit_m':float(top-.43-zz[i]),'branch':ident,'sample':int(i)})
 data['branches'].append({'id':ident,'side':side,'kind':kind,'s_range':[knots[0],knots[-1]],'samples':[{'s':float(s),'center':p.tolist(),'width':float(w),'water_z':float(z)} for s,p,w,z in zip(ss,xy,widths,zz)],'length_m':float(np.linalg.norm(np.diff(xy,axis=0),axis=1).sum()),'water_drop_m':float(zz[0]-zz[-1]),'maximum_uphill_m':float(max(0,np.diff(zz).max()))})
 footprints.append((xy,widths,zz))
for i,v in enumerate(ground.data.vertices):v.co.z=newz[i]
ground.data.update();gb,_=combine([ground]);data['terrain']={'changed_vertices':int(np.sum(abs(newz-gv[:,2])>.001)),'max_lowering_m':float((gv[:,2]-newz).max()),'method':'Z-only trench; actual bank strips; no changes to XY, color attributes or original water'}
# Carved banks can expose the former earth bearing under a garden floor.
# Add continuous masonry in the actual floor/wall footprint, down to the
# final terrain, instead of allowing a historical thin slab to float.
for ob in list(S.objects):
 if ob.type!='MESH' or not (ob.name.endswith('court floor') or 'front wall' in ob.name or 'railing post' in ob.name):continue
 vv=verts(ob);low=float(vv[:,2].min());samples=vv[vv[:,2]<low+.04];cut=False
 for p in samples:
  a=height(oldb,p[:2]);b=height(gb,p[:2])
  if a is not None and b is not None and p[2]-a<.18 and a-b>.10:cut=True;break
 if not cut:continue
 ob.data.calc_loop_triangles();tris=[]
 for tri in ob.data.loop_triangles:
  ids=list(tri.vertices);a,b,c=vv[ids];cross=np.cross(b[:2]-a[:2],c[:2]-a[:2])
  if cross>1e-7:tris.append(ids)
 if not tris:
  tris=[list(t.vertices) for t in ob.data.loop_triangles if abs(np.cross((vv[t.vertices[1]]-vv[t.vertices[0]])[:2],(vv[t.vertices[2]]-vv[t.vertices[0]])[:2]))>1e-7]
 if not tris:continue
 # Deduplicate projected vertices so triangulation diagonals are not skirts.
 lookup={};pts=[];faces=[]
 for tr in tris:
  ids=[]
  for j in tr:
   key=tuple(np.round(vv[j,:2],5))
   if key not in lookup:lookup[key]=len(pts);pts.append(vv[j,:2].copy())
   ids.append(lookup[key])
  faces.append(tuple(ids))
 count=len(pts);topz=low+.035;vs=[(*p,topz) for p in pts]+[(*p,min(topz-.35,height(gb,p)-.65)) for p in pts];allfaces=faces+[tuple(count+j for j in reversed(f)) for f in faces];edges={}
 for f in faces:
  for a,b in zip(f,f[1:]+f[:1]):key=tuple(sorted([a,b]));edges.setdefault(key,[]).append((a,b))
 for key,vals in edges.items():
  if len(vals)==1:a,b=vals[0];allfaces.append((a,count+a,count+b,b))
 name='Water-side continuous foundation '+ob.name;G.mesh(name,vs,allfaces,'stone',B);data['foundations'].append({'name':name,'supports':ob.name,'top':topz})
# Support bridge abutments at the final cut terrain, and leave their top fixed.
for ob in B.objects:
 if 'bank abutment' not in ob.name:continue
 for v in list(ob.data.vertices)[:4]:v.co.z=min(v.co.z,height(gb,v.co[:2])-.25)
 ob.data.update()
# Original low vegetation is relocated only when its ground has been cut.
# Woodland remains untouched: branches are in the inhabited lower districts.
for collname in ['21 Garden water edge clusters']:
 for ob in list(bpy.data.collections[collname].objects):
  if ob.type!='MESH' or not ob.name.startswith(('Grouped riparian shrub','Bank rooted rock cluster')):continue
  vv=verts(ob);p=vv[:,:2].mean(0);h0=height(oldb,p);h1=height(gb,p)
  if h0 is None or h1 is None or h0-h1<.12:continue
  st,d0,_=L.nearest(p[None,:]);t,n=L.basis(float(st[0]));chosen=None
  for off in [t*7,-t*7,t*12,-t*12,n*np.sign(d0[0])*9]:
   h=height(gb,p+off);oh=height(oldb,p+off)
   if h is not None and oh is not None and abs(h-oh)<.08:chosen=(off,h);break
  if chosen:
   off,h=chosen;delta=np.r_[off,h-h0];ob.location+=Vector(delta);data['relocated_plants'].append({'name':ob.name,'delta':delta.tolist()})
data['new_objects']=[o.name for o in W.objects]+[o.name for o in B.objects]
poses=json.loads((SRC/'route-poses.json').read_text('utf8'));(O/'route-poses.json').write_text(json.dumps(poses),encoding='utf8')
(O/'design-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
S['v15_scope']='Connected bilateral water lanes and pools, real carved beds, road crossings; v14 58s camera retained';S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'branch-garden-route-58s-v15.blend'))
print('V15_READY',[(b['id'],round(b['length_m']),round(b['water_drop_m'],2)) for b in data['branches']],len(data['crossings']),data['terrain'],flush=True)

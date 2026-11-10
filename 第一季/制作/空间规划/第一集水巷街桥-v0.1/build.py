"""v09: inhabited waterfront arcades and connected crossings, retaining v08 terrain."""
import bpy,sys,json,math
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);D=Path(__file__).parent
sys.path.insert(0,str(D));import geometry as G
sys.path.insert(0,str(D.parent/'第一集山水总图白模-v0.1'));import layout as L
OLD=R/'视频制作/第一集山水总图白模-20261024-v0.1';O=R/'视频制作/第一集水巷街桥-20261024-v0.1';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(OLD/'landscape-masterplan-v08.blend'));S=bpy.context.scene
P=json.loads((OLD/'layout-plan.json').read_text('utf8'))
def col(name):
 c=bpy.data.collections.new(name);S.collection.children.link(c);return c
A=col('09 Waterfront streets and inhabited bridgeheads');B=col('10 Connected bridges and quays');V=col('11 Garden canopy rhythm');G.ARCH=A
for m in bpy.data.materials:
 if ' / ' in m.name:G.M[m.name.split(' / ')[-1]]=m
for key,h in [('pine','#355d49'),('leaf','#779550')]:
 if key not in G.M:
  a=[int(h[i:i+2],16)/255 for i in (1,3,5)];rgba=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)+(1,)
  m=bpy.data.materials.new('Retained CITY05 palette / '+key);m.use_nodes=True;m.diffuse_color=rgba;nodes=m.node_tree.nodes;nodes.clear();bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Base Color'].default_value=rgba;out=nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(bs.outputs[0],out.inputs['Surface']);G.M[key]=m
removed=[]
for ob in list(S.objects):
 if ob.name.startswith('Planting reserve'):ob.hide_render=True
 if ob.name.startswith(('School valley framing aperture','Framing gate pier','Bridge railing post','Cross-water bridge','Framing bridge supported bank to bank')):
  removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
ground=bpy.data.objects['Continuous stable cloud terrain / river bed and inhabited slopes']
gb=BVHTree.FromPolygons([ground.matrix_world@v.co for v in ground.data.vertices],[tuple(f.vertices) for f in ground.data.polygons])
def groundz(xy):
 h=gb.ray_cast(Vector((*xy,400)),Vector((0,0,-1)),800);return h[0].z if h[0] else 0
def loc(s,side,x,q,z):
 t,n=L.basis(s);return np.r_[L.center(s)[0]+t*x+n*side*(L.width(s,side)+q),z]
def ang(s):
 t,_=L.basis(s);return math.atan2(t[1],t[0])
paths=[]
for p in P['paths']:
 pts=np.array(p['points']);paths.append((pts[:,:2],p['width']/2))
def on_path(xy,r=.35):
 for pts,w in paths:
  if np.min(np.linalg.norm(pts-xy,axis=1))<w+r:return True
 return False
records=[]
groups=[('School-arcade',1,[.028,.041,.054,.067,.080,.093]),('Bay-east-quay',-1,[.575,.590,.605]),('Bay-west-tea',1,[.658,.673,.688]),('Lower-west',1,[.866,.881,.896]),('Workshop-lane',-1,[.872,.887,.902,.927,.942])]
for group,side,stations in groups:
 for i,s in enumerate(stations):
  name=f'{group}-{i+1:02d}';wz=float(L.water_z(s));a=ang(s);length=17 if group=='School-arcade' else 18.5;upper=wz+6.8;h=[4.7,5.8,4.2][i%3]
  # Open ground storey retains the full public bank lane and transverse court entries.
  G.box(name+' upper floor',loc(s,side,0,8.5,upper),(length,15,.35),'wood',A,a)
  G.box(name+' upper rooms',loc(s,side,0,9.8,upper+h/2),(length-.5,11.5,h),'wall',A,a)
  G.roof(name+' tiled roof',loc(s,side,0,9.8,upper+h),(length+3,17),2.4+(i%2)*.5,a)
  for x in [-length/2+1,0,length/2-1]:
   for q in [1.8,15.2]:
    postx=x+3 if name=='Workshop-lane-03' and x< -6 and q==1.8 else x
    pos=loc(s,side,postx,q,upper)
    if on_path(pos[:2],.55):continue
    foot=groundz(pos[:2]);G.beam(name+' arcade column',[np.r_[pos[:2],foot-.3],pos],.23,'redwood',A)
    G.box(name+' stone column foot',np.r_[pos[:2],max(foot,wz+1.7)+.22],(.8,.8,.44),'stone',A,a)
  # Windows and timber balcony face the water. Ground level is genuinely passable.
  for x in [-5.3,5.3]:
   # Ground-floor shops at the back of the arcade. Keep each existing transverse entry open.
   corners=[loc(s,side,x+dx,14.3+dq,wz+2)[:2] for dx in [-3.2,0,3.2] for dq in [-2.2,0,2.2]]
   if not any(on_path(c,.4) for c in corners):
    G.box(name+' ground shop',loc(s,side,x,14.3,wz+4.3),(6.4,4.4,4.6),'wall',A,a)
    G.box(name+' shop shutter',loc(s,side,x,12.03,wz+3.7),(3.9,.12,3.2),'wood',A,a)
    G.box(name+' shop transom',loc(s,side,x,11.95,wz+5.8),(4.1,.14,.7),'window',A,a)
  for x in [-5.5,0,5.5]:
   G.box(name+' water window',loc(s,side,x,3.98,upper+2.2),(3.3,.14,2.7),'window',A,a)
   for xx in [x-1.15,x,x+1.15]:G.box(name+' window lattice',loc(s,side,xx,3.86,upper+2.2),(.09,.12,2.75),'wood',A,a)
  for x in np.linspace(-length/2+.3,length/2-.3,8):G.beam(name+' balcony baluster',[loc(s,side,x,1.3,upper+.2),loc(s,side,x,1.3,upper+1.2)],.06,'wood',A)
  G.beam(name+' balcony handrail',[loc(s,side,-length/2,1.3,upper+1.2),loc(s,side,length/2,1.3,upper+1.2)],.08,'wood',A)
  # Two lateral eave beams frame street depth; no decorative hoop.
  for q in [1.8,15.2]:G.beam(name+' eave beam',[loc(s,side,-length/2,q,upper-.25),loc(s,side,length/2,q,upper-.25)],.18,'wood',A)
  records.append({'id':name,'s':s,'side':side,'length':length,'q_range':[1,16],'ground_arcade_clear_height_m':4.5,'upper_floor':upper,'upper_access':'reserved at group gaps; interiors not detailed'})
 # Continuous quay follows actual curved shoreline, leaving transverse access open.
 ss=np.linspace(stations[0]-.006,stations[-1]+.006,120);vs=[]
 for s in ss:
  wz=float(L.water_z(s))
  for q,z in [(-2.5,wz-2),(-2.5,wz+2),(4.3,wz+2),(4.3,wz-2)]:vs.append(loc(s,side,0,q,z))
 fs=[]
 for i in range(len(ss)-1):
  for k in range(4):fs.append((4*i+k,4*i+(k+1)%4,4*(i+1)+(k+1)%4,4*(i+1)+k))
 G.mesh(group+' continuous inhabited quay',vs,fs,'stone',B)
 # Short water steps project into channel, away from the flight lane on bank q7.
 s=stations[len(stations)//2]+.007
 for j in range(6):G.box(group+' water stair',loc(s,side,0,-2.5-j*.55,float(L.water_z(s))+1.85-j*.27),(3.8,.7,.32),'stone',B,ang(s))
bridges=[]
for s,kind in [(.105,'covered school bridge'),(.18,'garden footbridge'),(.355,'valley footbridge'),(.465,'neighbourhood bridge'),(.51,'covered market bridge'),(.735,'bay mouth bridge'),(.84,'stone garden bridge'),(.91,'lower lane bridge'),(.955,'workshop bridge')]:
 t,n=L.basis(s);a=math.atan2(n[1],n[0]);ends=[L.point(s,side*(L.width(s,side)+9)) for side in [-1,1]]
 for p in ends:p[2]=groundz(p[:2])+.22
 def deckz(xy):
  st,dd,_=L.nearest(xy);st=float(st[0]);dd=float(dd[0]);side=1 if dd>=0 else -1;w=float(L.width(st,side));q=abs(dd)-w
  if q>=3.5:return groundz(xy)+.15
  base=float(L.water_z(st))+2.1
  if q>0:return base+(groundz(xy)+.15-base)*(q/3.5)
  f=(dd+float(L.width(st,-1)))/(float(L.width(st,-1))+float(L.width(st,1)))
  return base+(0 if s==.105 else 1)*math.sin(math.pi*f)**2
 pts=np.linspace(ends[0],ends[1],61)
 for p in pts:p[2]=deckz(p[:2])
 vs=[]
 for p in pts:
  for side in [-1,1]:
   v=p+np.r_[t*side*2.5,0];v[2]=deckz(v[:2]);vs.append(v)
 G.mesh(kind+' deck',vs,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(60)],'stone' if s in [.84,.955] else 'wood',B)
 # Railings end before bank lanes, so both side streets remain continuous.
 for side in [-1,1]:
  inner=pts[8:-8]+np.r_[t*side*2.25,0]
  G.beam(kind+' railing',inner+np.array([0,0,1.05]),.065,'wood',B)
  for p in inner[::5]:G.beam(kind+' railing post',[p,p+np.array([0,0,1.05])],.085,'wood',B)
 covered=s in [.105,.51]
 if covered:
  roofz=max(pts[:,2])+5.4;length=np.linalg.norm(ends[1][:2]-ends[0][:2]);mid=(ends[0]+ends[1])/2;mid[2]=roofz
  G.roof(kind+' continuous roof',mid,(length+1,7),2.5,a)
  for p in pts[::5]:
   for side in [-1,1]:
    xy=p[:2]+t*side*2.55
    if on_path(xy,.4) and (np.linalg.norm(xy-ends[0][:2])<5 or np.linalg.norm(xy-ends[1][:2])<5):continue
    G.beam(kind+' roof column',[np.r_[xy,p[2]],np.r_[xy,roofz]],.18,'redwood',B)
 # Piers stop at deck, carrying every bridge visibly.
 for p in pts[[12,48]]:G.box(kind+' abutment',np.r_[p[:2],(float(L.water_z(s))-3+p[2])/2],(2.1,4.6,p[2]-float(L.water_z(s))+3),'stone',B,a)
 bridges.append({'s':s,'kind':kind,'from':'bank--1','to':'bank-1','points':pts.tolist(),'width':5,'covered':covered})
# Trees articulate ridge gardens and bridgeheads; never place trunks on walking routes.
for i,(s,side,q) in enumerate([(.12,-1,26),(.16,1,35),(.24,-1,48),(.33,1,40),(.40,1,55),(.455,-1,22),(.555,1,22),(.63,-1,23),(.705,1,26),(.74,-1,32),(.815,1,32),(.85,-1,24),(.935,1,24)]):
 pos=loc(s,side,0,q,0)
 if on_path(pos[:2],2):continue
 z=groundz(pos[:2]);G.beam('Garden pine trunk',[np.r_[pos[:2],z],np.r_[pos[:2]+[1.5,0],z+8]],.45,'wood',V)
 for j,(dx,dy,dz,r) in enumerate([(0,0,7,4),(2,0,10,3.5),(-2,1,8.5,3.8)]):
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=(* (pos[:2]+[dx,dy]),z+dz));ob=bpy.context.object;ob.name='Garden pine canopy';ob.scale=(r,r*.8,r*.35)
  for c in list(ob.users_collection):c.objects.unlink(ob)
  V.objects.link(ob);ob.data.materials.append(G.M['pine' if (i+j)%3 else 'leaf']);ob['physical']=True
  for f in ob.data.polygons:f.use_smooth=True
bpy.data.collections['05 Atmospheric envelope optional'].hide_render=True
S.render.engine='BLENDER_EEVEE'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'waterlane-masterplan-v09.blend'))
(O/'design-data.json').write_text(json.dumps({'source':'landscape-masterplan-v08.blend','removed':removed,'frontages':records,'bridges':bridges,'palette':'unchanged CITY05','scope':'waterfront massing, connected public passages, reference precision'},ensure_ascii=False,indent=2),encoding='utf8')
print('WATERLANE_BUILD_READY',len(records),len(bridges),flush=True)

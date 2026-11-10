"""Add connected cloud/stone landscape and real receiving water to the retained v06 city."""
import bpy,sys,json,math,random,hashlib,argparse
import numpy as np
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--proxy',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);R=Path(a.root);O=R/'视频制作/第一集云山水城-20261024-v0.1'
src=R/'视频制作/第一集云中园城-20261024-v0.4'/('render-only-batched-v06.blend' if a.proxy else 'cloud-city-layered-58s-v06.blend');bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
c=bpy.data.collections.new('LANDSCAPE07 Cloud stone and water');s.collection.children.link(c);added=[];rng=random.Random(707)
def mat(name):
 m=bpy.data.materials.get(name) or bpy.data.materials.get('BATCH shader '+name)
 assert m,name
 return m
water=mat('CITY05 water / V04 water');stonewalk=mat('CITY05 stone / V04 stone');wood=mat('CITY05 wood / V04 wood');foam=mat('V04 foam');cloud=mat('MOTHER CLOUD feathered folded shoulders')
rock=mat('CITY05 stone / V04 stone').copy();rock.name='LANDSCAPE07 weathered gray green limestone';n=rock.node_tree.nodes;l=rock.node_tree.links;bs=next(q for q in n if q.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=.88
tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=7;noise.inputs['Detail'].default_value=4;l.new(tc.outputs['Generated'],noise.inputs['Vector']);ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.24;ramp.color_ramp.elements[0].color=(.11,.145,.135,1);ramp.color_ramp.elements[1].position=.78;ramp.color_ramp.elements[1].color=(.39,.41,.35,1);l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],bs.inputs['Base Color']);b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.28;b.inputs['Distance'].default_value=.32;l.new(noise.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],bs.inputs['Normal'])
fall=water.copy();fall.name='LANDSCAPE07 falling water';bs=next(q for q in fall.node_tree.nodes if q.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=.2
for link in list(bs.inputs['Base Color'].links):fall.node_tree.links.remove(link)
bs.inputs['Base Color'].default_value=(.35,.62,.58,1)
def mesh(name,v,f,m,physical=True):
 d=bpy.data.meshes.new('LANDSCAPE07 '+name);d.from_pydata(v,[],f);d.update();ob=bpy.data.objects.new('LANDSCAPE07 '+name,d);c.objects.link(ob);d.materials.append(m);ob['physical']=physical;added.append(ob.name);return ob
def ell(name,loc,sc,m,physical=True,rough=0):
 vv=[];ff=[];nr=14;ns=28
 for j in range(nr+1):
  ph=math.pi*j/nr
  for i in range(ns):
   t=math.tau*i/ns;k=1+rough*(.6*math.sin(t*5+ph*3)+.4*math.sin(t*9-ph*4));vv.append((loc[0]+sc[0]*math.sin(ph)*math.cos(t)*k,loc[1]+sc[1]*math.sin(ph)*math.sin(t)*k,loc[2]+sc[2]*math.cos(ph)*k))
 for j in range(nr):
  for i in range(ns):ff.append((j*ns+i,j*ns+(i+1)%ns,(j+1)*ns+(i+1)%ns,(j+1)*ns+i))
 ob=mesh(name,vv,ff,m,physical)
 for q in ob.data.polygons:q.use_smooth=True
 return ob
def tube(name,pts,r,m,physical=True):
 vs=[];faces=[]
 for k,p in enumerate(pts):
  tangent=Vector(pts[min(k+1,len(pts)-1)])-Vector(pts[max(k-1,0)]);u=tangent.normalized().cross(Vector((0,0,1)))
  if u.length<.01:u=Vector((1,0,0))
  u.normalize();v=tangent.normalized().cross(u)
  for i in range(8):vs.append(Vector(p)+r*(u*math.cos(i*math.tau/8)+v*math.sin(i*math.tau/8)))
 for j in range(len(pts)-1):
  for i in range(8):faces.append((j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i))
 faces.extend([tuple(reversed(range(8))),tuple(range((len(pts)-1)*8,len(pts)*8))]);return mesh(name,vs,faces,m,physical)
def ribbon(name,pts,width,m,physical=False):
 vs=[]
 for k,p in enumerate(pts):
  d=Vector(pts[min(k+1,len(pts)-1)])-Vector(pts[max(k-1,0)]);side=Vector((-d.y,d.x,0)).normalized()*width/2;vs.extend([Vector(p)+side,Vector(p)-side])
 return mesh(name,vs,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(pts)-1)],m,physical)
for name,shift in [('Main-cloud-stone',(0,0,0)),('Middle-low-ridge',(0,30,0))]:
 d=np.load(O/(name+'.npz'));v=d['vertices']+np.array(shift);ob=mesh(name,v.tolist(),d['faces'].tolist(),rock)
 for q in ob.data.polygons:q.use_smooth=True
 ob['role']='Connected rock mass exposed inside enclosing cloud; no separate stone island'
# High receiving basin carved into the rock shoulder; its narrow spill feeds the retained first pool.
center=(-985,801,68.02);ring=[(center[0]+13.8*math.cos(t*math.tau/72),center[1]+7.9*math.sin(t*math.tau/72),center[2]) for t in range(72)]
mesh('Rock shoulder reservoir',ring,[tuple(range(72))],water,False)
ribbon('Shoulder spill channel',[(-992,801,68.02),(-998,801,67.98),(-1003,801,67.95)],3.5,water)
# Short vertical water curtain, landing basin, then short horizontal connection into existing upper pool45m.
v=[];f=[]
for j in range(21):
 z=67.95+(45.06-67.95)*j/20
 for i in range(13):v.append((-1004-.18*math.sin(j*.7+i),799.2+i*.3,z))
for j in range(20):
 for i in range(12):f.append((j*13+i,j*13+i+1,(j+1)*13+i+1,(j+1)*13+i))
mesh('High rock waterfall',v,f,fall,False)
ribbon('Rockfall receiving runnel',[(-1004,801,45.06),(-1010,801,45.04),(-1017,801,45.02)],4.8,water)
for sign in [-1,1]:
 tube('Receiving runnel stone bank',[(-1004,801+sign*2.65,45),(-1017,801+sign*2.65,45)],.38,rock)
for i in range(18):ell('Waterfall foam',(-1004+rng.uniform(-.5,.5),801+rng.uniform(-1.8,1.8),45.1),(rng.uniform(.15,.55),rng.uniform(.12,.4),.06),foam,False)
# A connected cliff walk starts at existing upper catchment rim, enters the carved rock opening.
walk=[(-1016,823,45.3),(-1018,842,45.3),(-991,842,45.3),(-991,812,45.3),(-991,790,45.3)]
deck=ribbon('Upper rim to grotto walk',walk,2.8,stonewalk,True);sol=deck.modifiers.new('Walk slab thickness','SOLIDIFY');sol.thickness=.45
for j,(pa,pb) in enumerate(zip(walk,walk[1:])):
 d=Vector(pb)-Vector(pa);side=Vector((-d.y,d.x,0)).normalized()*1.35
 for sign in [-1,1]:
  aa=Vector(pa)+side*sign;bb=Vector(pb)+side*sign;tube('Cliff walk rail',[aa+Vector((0,0,1.05)),bb+Vector((0,0,1.05))],.07,wood)
  for k in range(int(d.length/3)+1):
   q=aa+(bb-aa)*k/max(1,int(d.length/3));tube('Cliff walk post',[q,q+Vector((0,0,1.05))],.055,wood)
for p0 in [walk[0],walk[1],walk[2]]:tube('Cliff walk pier',[(p0[0],p0[1],23),p0],.55,rock)
# A few exposed shore stones articulate the existing waterfall outlets; leave the central water sheets open.
for cx,cy,z in [(-1070,745,23),(-1025,686,0)]:
 for sign in [-1,1]:
  for k in range(3):ell('Cascade flank outcrop',(cx+sign*(8+k*3),cy+3+k*2,z+2+k*.8),(4.5,5.2,4.2),rock,True,.10)
# Low bank stones echo the main mountain in the middle pond, not a second field of peaks.
for i,(x,y,z,sc) in enumerate([(-660,604,24,(5,4,3)),(-655,606,25,(3,3,4)),(-648,605,24,(3.5,2.8,2.5)),(-394,330,5,(4,3,3))]):ell('Pond side stone',(x,y,z),sc,rock,True,.12)
# Cloud ridges rise behind the rock, with lower connected folds around its foot. Existing envelope remains.
for name,loc,sc in [('Main mountain foot',(-977,824,17),(58,41,28)),('Main mountain rear saddle',(-950,851,55),(42,31,40)),('High cloud ridge',(-932,888,111),(92,52,65)),('High ridge receding',(-822,924,139),(100,66,78)),('Middle ridge foot',(-674,668,3),(50,27,22))]:
 ob=ell(name,loc,sc,cloud,False);ob['role']='Ordinary enveloping cloud; not walkable rock or a new platform'
s['revision']='v07 cloud-stone-water landscape: main perforated rock mass, receiving cascade, connected grotto walk, low ridge and enclosing cloud folds; retained58s route.'
target=O/('render-only-batched-v07.blend' if a.proxy else 'cloud-stone-water-city-58s-v07.blend');bpy.ops.wm.save_as_mainfile(filepath=str(target))
if not a.proxy:
 (O/'construction-plan.json').write_text(json.dumps({'source':str(src.relative_to(R)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'added_objects':added,'existing_objects_modified':[],'walk_points':walk,'water_chain':['Rock shoulder reservoir z68','High rock waterfall to z45','Receiving runnel into existing catchment basin0','Existing waterfall to catchment1 z23','Existing waterfall to catchment2 z0'],'duration_s':58,'fps':24,'frames':1392,'scope':'Reference geometry and visible water continuity; not fluid simulation, final game asset or construction engineering'},ensure_ascii=False,indent=2),encoding='utf8')
print('LANDSCAPE_READY',len(added),flush=True)

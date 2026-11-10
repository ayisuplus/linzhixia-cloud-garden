"""Local finishing of verified blockout: trim unused court corners, close gallery, support ramps."""
import bpy,sys,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集山水总图白模-20261024-v0.1';P=json.loads((O/'layout-plan.json').read_text('utf8'))
bpy.ops.wm.open_mainfile(filepath=str(O/'landscape-masterplan-v08.blend'));S=bpy.context.scene
for ob in list(S.objects):
 if ob.name.startswith('Continuous middle gallery deck') or (ob.name.startswith('Bank to slope connector') and 'supported fill' in ob.name):bpy.data.objects.remove(ob,do_unlink=True)
ground=bpy.data.objects['Continuous stable cloud terrain / river bed and inhabited slopes'];bv=BVHTree.FromPolygons([v.co for v in ground.data.vertices],[tuple(p.vertices) for p in ground.data.polygons])
def height(x,y):
 hit=bv.ray_cast(Vector((x,y,1000)),Vector((0,0,-1)),2000);return hit[0].z if hit[0] else 0
changes=[]
for name,corner in [('West-neighbourhood-+1-00',(-1,1)),('Two-level-water-court',(-1,1)),('Lower-lane--1-02',(1,1))]:
 p=next(c for c in P['courts'] if c['id']==name);ob=bpy.data.objects[name+' court floor'];hx,hy=p['half_size'];poly=[(-hx,-hy),(hx,-hy),(hx,hy),(-hx,hy)];k=poly.index((corner[0]*hx,corner[1]*hy));prev=np.array(poly[(k-1)%4]);cur=np.array(poly[k]);nxt=np.array(poly[(k+1)%4]);leg=3.
 poly=poly[:k]+[tuple(cur+(prev-cur)/np.linalg.norm(prev-cur)*leg),tuple(cur+(nxt-cur)/np.linalg.norm(nxt-cur)*leg)]+poly[k+1:]
 vs=[]
 for z in [p['floor']-.04,p['floor']+.12]:
  for x,y in poly:vs.append((*tuple(np.array(p['center'])+np.array(p['tangent'])*x+np.array(p['outward'])*y),z))
 n=len(poly);fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 # Trim unused paving to the actual slope intersection, rather than clipping through a building footprint.
 coords=[];flags=[];step=.5;xx=np.linspace(-hx,hx,int(2*hx/step)+1);yy=np.linspace(-hy,hy,int(2*hy/step)+1)
 for y in yy:
  for x in xx:
   pt=np.array(p['center'])+np.array(p['tangent'])*x+np.array(p['outward'])*y;coords.append((pt[0],pt[1],p['floor']+.12));flags.append(height(*pt)-(p['floor']+.08))
 trimmed=[];tf=[];nx=len(xx)
 for j in range(len(yy)-1):
  for i in range(nx-1):
   for ids in [(j*nx+i,j*nx+i+1,(j+1)*nx+i+1),(j*nx+i,(j+1)*nx+i+1,(j+1)*nx+i)]:
    polygon=[]
    for ia,ib in zip(ids,ids[1:]+ids[:1]):
     a=np.array(coords[ia]);b=np.array(coords[ib]);fa=flags[ia];fb=flags[ib]
     if fa<=0:polygon.append(a)
     if (fa<=0)!=(fb<=0):polygon.append(a+(b-a)*fa/(fa-fb))
    if len(polygon)>=3:
     start=len(trimmed);trimmed.extend(polygon);tf.append(tuple(range(start,start+len(polygon))))
 old=ob.data;me=bpy.data.meshes.new(name+' slope-fitted paving');me.from_pydata(trimmed,[],tf);me.materials.append(old.materials[0]);ob.data=me;changes.append({'court':name,'method':'unused perimeter paving clipped at the actual terrain intersection','grid_m':step})
# Full gallery rectangle covers the entire right-angle turn, including its outside corner.
p=next(c for c in P['courts'] if c['id']=='Two-level-water-court');z=P['upper_entry']['middle_floor'];vs=[]
for zz in [z-.24,z]:
 for x,y in [(-1.8,5.2),(7.8,5.2),(7.8,8.8),(-1.8,8.8)]:vs.append((*tuple(np.array(p['center'])+np.array(p['tangent'])*x+np.array(p['outward'])*y),zz))
me=bpy.data.meshes.new('Continuous middle gallery deck');me.from_pydata(vs,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.materials.append(bpy.data.materials['Retained CITY05 palette / wood']);ob=bpy.data.objects.new('Continuous middle gallery deck',me);bpy.data.collections['03 Daily routes and crossings'].objects.link(ob);ob['physical']=True
supported=[]
for ob in list(bpy.data.collections['03 Daily routes and crossings'].objects):
 if not ob.name.startswith('Bank to slope connector'):continue
 vs=[];fs=[]
 for face in ob.data.polygons:
  top=[ob.data.vertices[i].co.copy() for i in face.vertices];bottom=[Vector((v.x,v.y,min(v.z-.12,height(v.x,v.y)-.25))) for v in top];start=len(vs);vs.extend(bottom+top);fs.extend(tuple(start+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
 me=bpy.data.meshes.new(ob.name+' fill');me.from_pydata(vs,[],fs);me.materials.append(bpy.data.materials['Retained CITY05 palette / stone']);o=bpy.data.objects.new(ob.name+' supported fill',me);bpy.data.collections['03 Daily routes and crossings'].objects.link(o);o['physical']=True;supported.append(ob.name)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'landscape-masterplan-v08.blend'));(O/'local-geometry-fixes.json').write_text(json.dumps({'trimmed_corners':changes,'gallery':'9.6m x 3.6m continuous deck','filled_connections':supported},ensure_ascii=False,indent=2),encoding='utf8');print('LOCAL_FIX_READY',flush=True)

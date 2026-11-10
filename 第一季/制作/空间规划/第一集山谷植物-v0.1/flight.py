"""Fresh 58-second blockout route, saved transforms and swept carrier envelope check."""
import bpy,sys,json,math,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);D=Path(__file__).parent;sys.path.insert(0,str(D.parent/'第一集山水总图白模-v0.1'));import layout as L
O=R/'视频制作/第一集山谷植物-20261024-v0.1';bpy.ops.wm.open_mainfile(filepath=str(O/'valley-masterplan-v10.blend'));S=bpy.context.scene
P=json.loads((R/'视频制作/第一集山水总图白模-20261024-v0.1/layout-plan.json').read_text('utf8'));end=next(p for p in P['courts'] if p['id']=='Repair-workshop');target=np.array(end['entry']);target[:2]-=np.array(end['outward'])*3;target[2]=end['floor']+2.3
ss=np.linspace(.018,.968,6001)
def smooth(t):t=np.clip(t,0,1);return t*t*t*(10+t*(-15+6*t))
# d is signed lateral position; bank offsets follow changing river width.
keys=[(.018,1,7,4.5),(.098,1,7,4.5),(.118,1,7,4.5),(.16,0,0,18),(.205,1,25,22),(.27,1,35,25),(.34,1,27,23),(.405,0,0,18),(.53,0,0,16),(.57,-1,7,4.5),(.61,-1,7,4.5),(.66,0,0,16),(.75,0,0,14),(.825,-1,-7,8),(.86,-1,-7,5.5),(.895,-1,-7,5.5),(.916,0,0,5.5),(.93,0,0,1.6),(.94,0,0,1.6),(.952,0,0,6.5),(.963,-1,7,6.0),(.968,-1,7,6.0)]
def control(k):
 s,side,q,h=k;return (side*(float(L.width(s,side))+q) if side else 0),h
raw=[]
for s in ss:
 for ka,kb in zip(keys,keys[1:]):
  if s<=kb[0]:
   da,ha=control(ka);db,hb=control(kb);f=smooth((s-ka[0])/(kb[0]-ka[0]));d=da+(db-da)*f;h=ha+(hb-ha)*f;break
 # Exact shoreline offset for the three inhabited arcade runs.
 for lo,hi,side in [(.018,.118,1),(.57,.61,-1)]:
  if lo<=s<=hi:d=side*(float(L.width(s,side))+7)
 if .825<=s<=.895:d=-(float(L.width(s,-1))-7)
 p=L.point(s,d,float(L.water_z(s)+h))
 # Last arrival looks into workshop; keep the endpoint tied to the actual door.
 if s>.955:
  endbase=L.point(.968,-(float(L.width(.968,-1))+7),float(L.water_z(.968)+6.0));p+=(target-endbase)*smooth((s-.955)/.013)
 raw.append(p)
raw=np.array(raw)
# Smooth the sampled polyline before timing so fine segment corners do not produce velocity jolts.
k=np.arange(-30,31);kernel=np.exp(-.5*(k/10)**2);kernel/=kernel.sum()
for j in range(3):
 padded=np.r_[raw[0,j]+(raw[0,j]-raw[1,j])*np.arange(30,0,-1),raw[:,j],raw[-1,j]+(raw[-1,j]-raw[-2,j])*np.arange(1,31)]
 raw[:,j]=np.convolve(padded,kernel,mode='valid')
arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(raw,axis=0),axis=1))];length=arc[-1]
times=np.arange(1392)/24;duration=1391/24
vec=np.gradient(raw,axis=0);unit=vec/np.maximum(np.linalg.norm(vec,axis=1)[:,None],1e-8);curv=np.linalg.norm(np.gradient(unit,axis=0),axis=1)/np.maximum(np.linalg.norm(vec,axis=1),1e-6)
speed=np.minimum(54,np.sqrt(8/np.maximum(curv,1e-5)));speed[0]=speed[-1]=.1
for i in range(1,len(speed)):speed[i]=min(speed[i],np.sqrt(speed[i-1]**2+2*10*(arc[i]-arc[i-1])))
for i in range(len(speed)-2,-1,-1):speed[i]=min(speed[i],np.sqrt(speed[i+1]**2+2*10*(arc[i+1]-arc[i])))
travel_time=np.r_[0,np.cumsum(2*np.diff(arc)/(speed[:-1]+speed[1:]))];travel_time*=duration/travel_time[-1]
dist=np.interp(times,travel_time,arc);positions=np.column_stack([np.interp(dist,arc,raw[:,j]) for j in range(3)])
data=bpy.data.cameras.new('FPV landscape route');cam=bpy.data.objects.new('FPV landscape route',data);S.collection.objects.link(cam);data.lens=21;data.clip_start=.08;data.clip_end=5000;cam.rotation_mode='QUATERNION';quats=[]
for i,(d,p) in enumerate(zip(dist,positions)):
 ahead=min(d+22,length);behind=max(d-8,0);aa=np.array([np.interp(ahead,arc,raw[:,j]) for j in range(3)]);bb=np.array([np.interp(behind,arc,raw[:,j]) for j in range(3)]);direction=aa-bb
 arrival=np.array([*end['center'],end['floor']+2.3])-p;mix=smooth((d-(length-150))/150);direction=direction/max(np.linalg.norm(direction),1e-8)*(1-mix)+arrival/max(np.linalg.norm(arrival),1e-8)*mix
 # Keep the horizon stable; a gentle downward view exposes foreground water and bank levels.
 direction[2]-=.035*np.linalg.norm(direction[:2]);q=Vector(direction).to_track_quat('-Z','Y')
 if quats and q.dot(Quaternion(quats[-1]))<0:q.negate()
 cam.location=p;cam.rotation_quaternion=q;cam.keyframe_insert('location',frame=i+1);cam.keyframe_insert('rotation_quaternion',frame=i+1);quats.append(list(q))
S.camera=cam;S.frame_start=1;S.frame_end=1392;S.render.fps=24
# The atmospheric envelope is a separate layer, default muted for geometric inspection.
S.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(O/'valley-route-58s-v10.blend'))
# Audit the complete saved scene against 27 sample points of a 1.1m carrier envelope.
vs=[];faces=[];owners=[]
for ob in S.objects:
 if ob.type!='MESH' or not ob.get('physical',False) or ob.hide_render:continue
 owners.extend([ob.name]*len(ob.data.polygons));start=len(vs);vs.extend(ob.matrix_world@v.co for v in ob.data.vertices);faces.extend(tuple(start+j for j in f.vertices) for f in ob.data.polygons)
bvh=BVHTree.FromPolygons(vs,faces);hits=[];offsets=[Vector((x,y,z)) for x in [-.55,0,.55] for y in [-.55,0,.55] for z in [-.35,0,.35]]
for i in range(1391):
 a=Vector(positions[i]);b=Vector(positions[i+1]);d=b-a
 if d.length<1e-6:continue
 for shift in offsets:
  h=bvh.ray_cast(a+shift,d.normalized(),d.length)
  if h[0] is not None:hits.append({'frame':i+1,'point':list(h[0]),'object':owners[h[2]]});break
v=np.diff(positions,axis=0)*24;acc=np.diff(v,axis=0)*24;turns=[math.degrees(Quaternion(a).rotation_difference(Quaternion(b)).angle) for a,b in zip(quats,quats[1:])]
poses=[{'frame':i+1,'time':i/24,'position':p.tolist(),'quaternion':q} for i,(p,q) in enumerate(zip(positions,quats))]
report={'duration_seconds':58,'frames':1392,'fps':24,'length_m':float(length),'max_speed_m_s':float(np.linalg.norm(v,axis=1).max()),'max_acceleration_m_s2':float(np.linalg.norm(acc,axis=1).max()),'max_rotation_deg_per_frame':max(turns),'swept_sample_collisions':hits,'envelope_m':[1.1,1.1,.7],'scope':'Geometric reference route, not physical flight dynamics; 27 swept samples are not an exact swept-solid proof. Cloud layer disabled in source default.'}
(O/'route-poses.json').write_text(json.dumps(poses),encoding='utf8');(O/'route-check.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('ROUTE_READY',json.dumps({k:v for k,v in report.items() if k!='swept_sample_collisions'}),'collision_count',len(hits),flush=True)

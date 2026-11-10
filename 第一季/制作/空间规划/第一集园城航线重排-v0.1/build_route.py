"""An explicit visual route; gates face the travel direction well before the aperture."""
import bpy,sys,argparse,json,math,bisect,hashlib,ast
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);root=Path(a.root)
out=root/'视频制作/第一集园城航线重排-20261023-v0.1';source=out/'garden-city-space-v01.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));S=bpy.context.scene;S.frame_set(1)
plan=json.loads((out/'space-plan.json').read_text(encoding='utf8'));nodes=[Vector(q) for q in plan['nodes']];labels=plan['labels']
exclude={'E01_FLIGHT_PROXY','V05_TEMPORARY_QUADROTOR','V06_CLOUD_EDGE_REFINEMENT','V03_ROUTE_GUIDES'}
dg=bpy.context.evaluated_depsgraph_get();verts=[];faces=[];names=[]
for o in S.objects:
    if o.type not in {'MESH','CURVE'} or not o.get('physical',True) or o.hide_render or any(c.name in exclude for c in o.users_collection):continue
    ev=o.evaluated_get(dg);mesh=ev.to_mesh()
    if mesh is None:continue
    base=len(verts);verts.extend(ev.matrix_world@v.co for v in mesh.vertices)
    faces.extend(tuple(base+i for i in f.vertices) for f in mesh.polygons);names.extend([o.name]*len(mesh.polygons));ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,faces)
offsets=[Vector((x,y,z)) for x in [-.7,0,.7] for y in [-.7,0,.7] for z in [-.085,.17,.41]]
def hits_path(path,offs=offsets):
    hits={}
    for i,(u,v) in enumerate(zip(path,path[1:])):
        d=v-u
        if d.length<1e-6:continue
        for off in offs:
            h=bvh.ray_cast(u+off,d.normalized(),d.length+.00001)
            if h[2] is not None:hits.setdefault(names[h[2]],{'segment':i,'from':list(u),'to':list(v)})
    return hits
path=[nodes[0]];corners=[]
def line(u,v):
    n=max(1,math.ceil((v-u).length/.3));path.extend(u.lerp(v,j/n) for j in range(1,n+1))
for i in range(1,len(nodes)-1):
    q=nodes[i];before=(q-nodes[i-1]).normalized();after=(nodes[i+1]-q).normalized()
    r=min(75,(q-nodes[i-1]).length*.48,(nodes[i+1]-q).length*.48)
    u=q-before*r;v=q+after*r;n=max(6,math.ceil(2*r/.15))
    controls=[u,u+(q-u)*.4,u+(q-u)*.8,v-(v-q)*.8,v-(v-q)*.4,v]
    arc=[sum((controls[k]*(math.comb(5,k)*(1-t)**(5-k)*t**k) for k in range(6)),Vector()) for t in np.linspace(0,1,n+1)]
    corners.append({'node':i,'trim_m':r});line(path[-1],u);path.extend(arc[1:])
line(path[-1],nodes[-1]);hits=hits_path(path)
print('GEOMETRY_HITS',json.dumps(hits),flush=True)
(out/'route-geometry-check.json').write_text(json.dumps({'hits':hits,'corners':corners},indent=2),encoding='utf8')
if hits:sys.exit(2)
dist=[0]
for u,v in zip(path,path[1:]):dist.append(dist[-1]+(v-u).length)
def pos(s):
    s=max(0,min(dist[-1],s));i=min(len(path)-2,max(0,bisect.bisect_right(dist,s)-1));den=dist[i+1]-dist[i]
    return path[i].lerp(path[i+1],(s-dist[i])/den if den else 0)
resampled=[pos(float(s)) for s in np.linspace(0,dist[-1],math.ceil(dist[-1]/.2)+1)];path=resampled;dist=[0]
for u,v in zip(path,path[1:]):dist.append(dist[-1]+(v-u).length)
xyz=np.array([list(q) for q in path]);sd=np.array(dist);ds=np.diff(sd)
directions=np.diff(xyz,axis=0);directions/=np.maximum(np.linalg.norm(directions,axis=1)[:,None],1e-9)
curv=np.zeros(len(path));curv[1:-1]=np.arccos(np.clip(np.sum(directions[:-1]*directions[1:],axis=1),-1,1))/np.maximum((ds[:-1]+ds[1:])/2,1e-6)
cap=np.minimum(80,np.minimum(np.sqrt(17/np.maximum(curv,1e-7)),math.radians(38)/np.maximum(curv,1e-7)))
for g in plan['gates']:
    dd=np.linalg.norm(xyz-np.array(g['center']),axis=1);cap=np.minimum(cap,18+np.maximum(0,dd-14)*.8)
skim_index=int(np.argmin(np.linalg.norm(xyz-np.array(nodes[labels['skim']]),axis=1)))
cap[skim_index:]=np.minimum(cap[skim_index:],19)
cap[0]=cap[-1]=.15
for i in range(1,len(cap)):cap[i]=min(cap[i],math.sqrt(cap[i-1]**2+2*18*ds[i-1]))
for i in range(len(cap)-2,-1,-1):cap[i]=min(cap[i],math.sqrt(cap[i+1]**2+2*18*ds[i]))
kernel=np.exp(-.5*(np.arange(-30,31)/10)**2);kernel/=sum(kernel)
vel=np.minimum(cap,np.convolve(np.pad(cap,(30,30),mode='edge'),kernel,mode='valid'))
clock=np.r_[0,np.cumsum(2*ds/np.maximum(vel[:-1]+vel[1:],.01))];unscaled=float(clock[-1]);clock=.4+clock*(56.8/clock[-1])
def at(t):return float(np.interp(t,clock,sd))
positions=[pos(at(i/24)) for i in range(1392)]
raw_yaw=[];raw_pitch=[]
for i in range(1392):
    t=i/24;s=at(t);lookahead=max(8,(at(t+.1)-at(t-.1))*1.1)
    d=pos(min(dist[-1],s+lookahead))-pos(max(0,s-1))
    if d.length<.001:d=(nodes[1]-nodes[0]) if t<1 else (nodes[-1]-nodes[-2])
    yaw=math.atan2(d.y,d.x);pitch=max(math.radians(-18),min(math.radians(5),math.atan2(d.z,math.hypot(d.x,d.y))))
    if raw_yaw:
        while yaw-raw_yaw[-1]>math.pi:yaw-=math.tau
        while yaw-raw_yaw[-1]<-math.pi:yaw+=math.tau
    raw_yaw.append(yaw);raw_pitch.append(pitch)
def smooth(vals,sigma=4):
    r=int(sigma*3);w=np.exp(-.5*(np.arange(-r,r+1)/sigma)**2);w/=w.sum();return np.convolve(np.pad(vals,(r,r),mode='edge'),w,mode='valid')
yaws=smooth(raw_yaw);pitches=smooth(raw_pitch)
cam=S.objects['FAST_ROUTE_FPV'];drone=S.objects['Same carrier ROOT placeholder'];cam.animation_data_clear();drone.animation_data_clear();cam.rotation_mode=drone.rotation_mode='QUATERNION'
records=[];quats=[];arc=0
for i,(q,yaw,pitch) in enumerate(zip(positions,yaws,pitches)):
    forward=Vector((math.cos(pitch)*math.cos(yaw),math.cos(pitch)*math.sin(yaw),math.sin(pitch)))
    cam.location=q+Vector((0,0,.34));cam.rotation_quaternion=forward.to_track_quat('-Z','Y')
    if quats and cam.rotation_quaternion.dot(quats[-1])<0:cam.rotation_quaternion.negate()
    quats.append(cam.rotation_quaternion.copy());drone.location=q;drone.rotation_quaternion=Vector((math.cos(yaw),math.sin(yaw),0)).to_track_quat('Y','Z')
    for ob in [cam,drone]:ob.keyframe_insert('location',frame=i+1);ob.keyframe_insert('rotation_quaternion',frame=i+1)
    if i:arc+=(positions[i]-positions[i-1]).length
    records.append({'frame':i+1,'time_s':i/24,'position':list(q),'camera':list(cam.location),'forward':list(forward),'arc_m':arc})
for ob in [cam,drone]:
    for layer in ob.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for k in fc.keyframe_points:k.interpolation='LINEAR'
actual_hits=hits_path(positions);camera_hits=hits_path([Vector(r['camera']) for r in records],[Vector()])
turns=[math.degrees(2*math.acos(min(1,abs(u.dot(v))))) for u,v in zip(quats,quats[1:])]
vv=np.diff(np.array([list(q) for q in positions]),axis=0)*24;aa=np.diff(vv,axis=0)*24
gates=[]
for g in plan['gates']:
    c=Vector(g['center']);normal=Vector(g['normal']);signed=[(q-c).dot(normal) for q in positions];cross=[]
    for i,(s0,s1) in enumerate(zip(signed,signed[1:])):
        if s0<0<=s1:
            q=positions[i].lerp(positions[i+1],-s0/(s1-s0));cross.append({'frame':i+1,'time_s':i/24,'point':list(q),'radial_offset':(q-c).length})
    gates.append(dict(g,crossings=cross))
report={'duration_s':58,'fps':24,'frame_count':1392,'distance_m':arc,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'max_frame_speed_m_s':float(np.linalg.norm(vv,axis=1).max()),'max_frame_acceleration_m_s2':float(np.linalg.norm(aa,axis=1).max()),'max_camera_turn_deg_per_frame':max(turns),'path_hits':hits,'frame_envelope_hits':actual_hits,'camera_hits':camera_hits,'gates':gates,'nodes':plan['nodes'],'records':records,'unscaled_duration_s':unscaled,'lens_mm':cam.data.lens,'batches':[{'id':'B01','start_frame':1,'end_frame':720},{'id':'B02','start_frame':673,'end_frame':1392}]}
(out/'flight-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('FLIGHT_CHECK',json.dumps({k:v for k,v in report.items() if k not in ['records','nodes']}),flush=True)
assert not actual_hits and not camera_hits
assert all(any(c['radial_offset']<.05 for c in g['crossings']) for g in gates)
S.camera=cam;S.frame_start=1;S.frame_end=1392;S.render.fps=24;S.render.fps_base=1;S.frame_set(1)
for m in list(S.timeline_markers):S.timeline_markers.remove(m)
for g in gates:S.timeline_markers.new(g['id'],frame=g['crossings'][0]['frame'])
S['episode_scope']='58-second route replan, forward-readable gates and populated gardens; candidate.'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'garden-city-flight-58s-v04.blend'))
print('ROUTE_READY',flush=True)

"""58 seconds: three real moon-window crossings, smoothed gaze, water skim."""
import bpy,sys,argparse,json,math,bisect,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser();p.add_argument('--root',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);root=Path(a.root)
source=root/'视频制作/第一集园城设计-20261023-v0.1/garden-city-design-v01.blend'
out=root/'视频制作/第一集园城设计-20261023-v0.1';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source));S=bpy.context.scene
old=json.loads((root/'视频制作/第一集全程快飞-20261023-v0.2/flight-checks.json').read_text(encoding='utf8'))
original=json.loads((root/'视频制作/第一集浮空园城-20261022-v0.4/route-layout.json').read_text(encoding='utf8'))['flight_points']
nodes=[];labels={}
def add(q,label=None):
    if label:labels[label]=len(nodes)
    nodes.append(Vector(q))
for i,q in enumerate(original[:6]):add(q,'start' if i==0 else 'exit' if i==5 else None)
for q in original[6:9]:add(q)
add((-1215,852,47));add((-1203,852,47),'gateA');add((-1190,852,47))
for q in original[11:16]:add(q)
add((-930,630,55));add((-910,630,55),'gateB');add((-890,630,55));add(original[19],'open')
for q in original[20:27]:add(q)
add((-235,5,6));add((-225,-4,5));add((-210,-4,5),'gateC');add((-195,-4,5))
add((-180,13.5,4));add((-145,23,2.3));add((-130,27,1.6));add((-112,27,.25),'skim')
add((-95,27,.25));add((-70,13.5,.25));add((-30,13.5,.25));add((-10,13.5,.25),'lift')
add((-3,13.5,1));add((4.5,13.5,2));add((9,16,2));add(original[-1],'end')
exclude={'E01_FLIGHT_PROXY','V05_TEMPORARY_QUADROTOR','V06_CLOUD_EDGE_REFINEMENT','V03_ROUTE_GUIDES'}
dg=bpy.context.evaluated_depsgraph_get();verts=[];faces=[];names=[]
for o in S.objects:
    if o.type not in {'MESH','CURVE'} or not o.get('physical',True) or o.hide_render or any(c.name in exclude for c in o.users_collection):continue
    ev=o.evaluated_get(dg);mesh=ev.to_mesh()
    if mesh is None:continue
    base=len(verts);verts.extend(ev.matrix_world@v.co for v in mesh.vertices)
    faces.extend(tuple(base+i for i in f.vertices) for f in mesh.polygons);names.extend([o.name]*len(mesh.polygons));ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,faces)
offsets=[Vector((x,y,z)) for x in [-.61,0,.61] for y in [-.61,0,.61] for z in [-.085,.17,.41]]
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
    n=max(1,math.ceil((v-u).length/.30));path.extend(u.lerp(v,j/n) for j in range(1,n+1))
for i in range(1,len(nodes)-1):
    q=nodes[i];before=(q-nodes[i-1]).normalized();after=(nodes[i+1]-q).normalized()
    r=min(30,(q-nodes[i-1]).length*.4,(nodes[i+1]-q).length*.4)
    if i<=5:r=min(4,(q-nodes[i-1]).length*.7,(nodes[i+1]-q).length*.7)
    if i>=labels['skim']:r=min(r,3)
    while True:
        u=q-before*r;v=q+after*r;n=max(5,math.ceil(2*r/.15))
        controls=[u,u+(q-u)*.4,u+(q-u)*.8,v-(v-q)*.8,v-(v-q)*.4,v]
        arc=[sum((controls[k]*(math.comb(5,k)*(1-t)**(5-k)*t**k) for k in range(6)),Vector()) for t in [j/n for j in range(n+1)]]
        collision=hits_path(arc)
        if not collision or r<.01:break
        r*=.5
    corners.append({'node':i,'trim_m':r,'hits':collision});line(path[-1],u);path.extend(arc[1:])
line(path[-1],nodes[-1]);hits=hits_path(path)
dist=[0]
for u,v in zip(path,path[1:]):dist.append(dist[-1]+(v-u).length)
def pos(s):
    s=max(0,min(dist[-1],s));i=min(len(path)-2,max(0,bisect.bisect_right(dist,s)-1));den=dist[i+1]-dist[i]
    return path[i].lerp(path[i+1],(s-dist[i])/den if den else 0)
# Sample the C2 geometric curve uniformly, then allocate time by curvature.
# Total length stays 58 s; internal window timestamps are free to move.
raw_dist=dist.copy();raw_path=path.copy()
resampled=[pos(float(s)) for s in np.linspace(0,dist[-1],math.ceil(dist[-1]/.15)+1)]
path=resampled;dist=[0]
for u,v in zip(path,path[1:]):dist.append(dist[-1]+(v-u).length)
xyz=np.array([list(q) for q in path]);sd=np.array(dist);ds=np.diff(sd)
directions=np.diff(xyz,axis=0);directions/=np.maximum(np.linalg.norm(directions,axis=1)[:,None],1e-9)
curv=np.zeros(len(path));curv[1:-1]=np.arccos(np.clip(np.sum(directions[:-1]*directions[1:],axis=1),-1,1))/np.maximum((ds[:-1]+ds[1:])/2,1e-6)
# Preserve passages, with less arbitrary slow-down at the actual opening plane.
cap=np.minimum(115,np.minimum(np.sqrt(35/np.maximum(curv,1e-7)),math.radians(70)/np.maximum(curv,1e-7)))
# Low altitude speed cap is local to the final water approach.
skim_index=int(np.argmin(np.linalg.norm(xyz-np.array(nodes[labels['skim']]),axis=1)))
cap[skim_index:]=np.minimum(cap[skim_index:],18+np.maximum(0,xyz[skim_index:,2]-.25)*12)
for key in ['gateA','gateB','gateC']:
    dd=np.linalg.norm(xyz-np.array(nodes[labels[key]]),axis=1)
    cap=np.minimum(cap,18+np.maximum(0,dd-8)*1.3)
cap[0]=cap[-1]=.15
for i in range(1,len(cap)):cap[i]=min(cap[i],math.sqrt(cap[i-1]**2+2*30*ds[i-1]))
for i in range(len(cap)-2,-1,-1):cap[i]=min(cap[i],math.sqrt(cap[i+1]**2+2*30*ds[i]))
kernel=np.exp(-.5*(np.arange(-24,25)/8)**2);kernel/=sum(kernel)
vel=np.minimum(cap,np.convolve(np.pad(cap,(24,24),mode='edge'),kernel,mode='valid'))
clock=np.r_[0,np.cumsum(2*ds/np.maximum(vel[:-1]+vel[1:],.01))]
unscaled_duration=float(clock[-1]);clock=.8+clock*(56.2/clock[-1]);speed_scale=unscaled_duration/56.2
anchor_names=['start','exit','gateA','gateB','open','gateC','skim','lift','end']
ss=[dist[min(range(len(path)),key=lambda j:(path[j]-nodes[labels[k]]).length_squared)] for k in anchor_names]
ts=[float(np.interp(s,sd,clock)) for s in ss]
def at(t):return float(np.interp(t,clock,sd))
positions=[pos(at((f-1)/24)) for f in range(1,1393)]
# Local C2 arrival correction: reach x=10.8 before passing the porch column.
# Preserve the validated 0-55 s positions and the global 58 s duration.
tail_start=55.;tail_mid=56.05;tail_end=57.;j0=round(tail_start*24)
P0=np.array(positions[j0]);V0=(np.array(positions[j0+1])-np.array(positions[j0-1]))*12
A0=(np.array(positions[j0+1])-2*P0+np.array(positions[j0-1]))*576
PM=np.array((10.8,16.,2.));VM=np.array((0,2.6,-.6));AM=np.zeros(3)
PE=np.array(original[-1]);ZERO=np.zeros(3)
def quintic_segment(t,duration,p0,v0,a0,p1,v1,a1):
    u=t/duration;c0=p0;c1=v0*duration;c2=a0*duration**2/2
    rhs=np.array([p1-c0-c1-c2,v1*duration-c1-2*c2,a1*duration**2-2*c2])
    c3,c4,c5=np.linalg.solve(np.array([[1,1,1],[3,4,5],[6,12,20]],dtype=float),rhs)
    return Vector(c0+c1*u+c2*u*u+c3*u**3+c4*u**4+c5*u**5)
for j in range(j0,len(positions)):
    t=j/24
    if t<tail_mid:positions[j]=quintic_segment(t-tail_start,tail_mid-tail_start,P0,V0,A0,PM,VM,AM)
    elif t<tail_end:positions[j]=quintic_segment(t-tail_mid,tail_end-tail_mid,PM,VM,AM,PE,ZERO,ZERO)
    else:positions[j]=Vector(PE)
def actual_position(t):
    f=max(0,min(len(positions)-1,t*24));i=min(len(positions)-2,int(f));return positions[i].lerp(positions[i+1],f-i)
raw_yaw=[];raw_pitch=[]
last_forward=(nodes[1]-nodes[0]).normalized()
for f in range(1,1393):
    t=(f-1)/24
    if t+.16<tail_start:d=pos(at(min(57,t+.16)))-pos(at(max(.8,t-.12)))
    else:d=actual_position(min(57,t+.16))-actual_position(max(.8,t-.12))
    if d.length<.001:d=(nodes[1]-nodes[0]) if t<1 else last_forward.copy()
    d.normalize()
    last_forward=d.copy()
    yaw=math.atan2(d.y,d.x);pitch=math.atan2(d.z,math.hypot(d.x,d.y))
    if raw_yaw:
        while yaw-raw_yaw[-1]>math.pi:yaw-=math.tau
        while yaw-raw_yaw[-1]<-math.pi:yaw+=math.tau
    raw_yaw.append(yaw);raw_pitch.append(pitch)
def smooth(vals,sigma=6):
    radius=int(sigma*3);weights=[math.exp(-.5*(j/sigma)**2) for j in range(-radius,radius+1)];den=sum(weights)
    return [sum(w*vals[min(len(vals)-1,max(0,i+j))] for j,w in zip(range(-radius,radius+1),weights))/den for i in range(len(vals))]
yaws=smooth(raw_yaw);pitches=smooth(raw_pitch)
for values,raw in [(yaws,raw_yaw),(pitches,raw_pitch)]:
    wide=smooth(raw,12)
    for i in range(len(values)):
        w=max(0,min(1,(i/24-53.5)/1.5));w=w*w*(3-2*w);values[i]=values[i]*(1-w)+wide[i]*w
cam=S.objects['FAST_ROUTE_FPV'];drone=S.objects['Same carrier ROOT placeholder']
cam.animation_data_clear();drone.animation_data_clear();cam.rotation_mode=drone.rotation_mode='QUATERNION'
records=[];quats=[]
for i,(q,yaw,pitch) in enumerate(zip(positions,yaws,pitches)):
    f=i+1;t=i/24;forward=Vector((math.cos(pitch)*math.cos(yaw),math.cos(pitch)*math.sin(yaw),math.sin(pitch)))
    cam.location=q+Vector((0,0,.34));cam.rotation_quaternion=forward.to_track_quat('-Z','Y')
    if quats and cam.rotation_quaternion.dot(quats[-1])<0:cam.rotation_quaternion.negate()
    quats.append(cam.rotation_quaternion.copy());drone.location=q;drone.rotation_quaternion=Vector((math.cos(yaw),math.sin(yaw),0)).to_track_quat('Y','Z')
    for ob in [cam,drone]:
        ob.keyframe_insert('location',frame=f);ob.keyframe_insert('rotation_quaternion',frame=f)
    records.append({'frame':f,'time_s':t,'arc_m':at(t),'position':list(q),'camera':list(cam.location),'speed_m_s':(at(t+.02)-at(t-.02))/.04})
for ob in [cam,drone]:
    for layer in ob.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for k in fc.keyframe_points:k.interpolation='LINEAR'
actual_hits=hits_path(positions);camera_hits=hits_path([Vector(r['camera']) for r in records],[Vector((0,0,0))])
turns=[math.degrees(2*math.acos(min(1,abs(u.dot(v))))) for u,v in zip(quats,quats[1:])]
gate_reports=[]
for key,center,radius in [('gateA',(-1203,852,47),2.5),('gateB',(-910,630,55),3),('gateC',(-210,-4,5),2.3)]:
    center=Vector(center)
    near=[i for i,q in enumerate(positions) if abs(q.x-center.x)<6 and (q-center).length<9]
    i=min(range(len(positions)),key=lambda j:(positions[j]-center).length)
    crossings=[]
    for j in near:
        if j==len(positions)-1:continue
        u,v=positions[j:j+2]
        if u.x<=center.x<v.x:
            q=u.lerp(v,(center.x-u.x)/(v.x-u.x));crossings.append({'frames':[j+1,j+2],'point':list(q),'radial_offset_m':math.hypot(q.y-center.y,q.z-center.z)})
    gate_reports.append({'id':key,'center':list(center),'radius_m':radius,'nearest_frame':i+1,'time_s':i/24,'crossings':crossings})
vv=np.diff(np.array([list(q) for q in positions]),axis=0)*24
aa=np.diff(vv,axis=0)*24
motion_metrics={'max_frame_speed_m_s':float(np.max(np.linalg.norm(vv,axis=1))),'max_frame_acceleration_m_s2':float(np.max(np.linalg.norm(aa,axis=1))),'p99_frame_acceleration_m_s2':float(np.percentile(np.linalg.norm(aa,axis=1),99))}
report={'motion_metrics':motion_metrics,'version':'design-v01-motion-v03','time_profile_scale':speed_scale,'unscaled_duration_s':unscaled_duration,'source':str(source.relative_to(root)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'duration_s':58,'fps':24,'frame_count':1392,'distance_m':dist[-1],'max_speed_m_s':max(r['speed_m_s'] for r in records),'max_camera_turn_deg_per_frame':max(turns),'camera_turns_over_10deg':sum(x>10 for x in turns),'source_max_camera_turn_deg_per_frame':54.8118200815,'anchors':[{'name':n,'time_s':t,'arc_m':s} for n,t,s in zip(anchor_names,ts,ss)],'control_points':[list(q) for q in nodes],'corners':corners,'dense_path_samples':len(path),'path_hits':hits,'frame_envelope_hits':actual_hits,'camera_hits':camera_hits,'gates':gate_reports,'skim':{'root_z_m':.25,'water_z_m':-.48,'minimum_body_z_m':.165,'nominal_body_water_clearance_m':.645,'camera_height_over_water_m':1.07,'lift_before_bridge':True},'batches':old['batches'],'records':records}
report['base_path_distance_m']=report['distance_m'];actual_arc=0.
for j,r in enumerate(report['records']):
    r['reference_arc_m']=r['arc_m']
    if j:actual_arc+=(positions[j]-positions[j-1]).length
    r['arc_m']=actual_arc
    r['speed_m_s']=(positions[min(j+1,len(positions)-1)]-positions[max(0,j-1)]).length*24/(min(j+1,len(positions)-1)-max(0,j-1))
report['sampled_actual_distance_m']=actual_arc
report['arrival_correction']={'position_start_s':55,'midpoint_time_s':56.05,'midpoint':[10.8,16,2],'end_time_s':57,'camera_blend_start_s':53.5,'purpose':'Clear porch column before entering receiver position','reference_arc_note':'anchors and distance_m refer to base geometric route; records arc_m/speed_m_s and motion_metrics describe actual sampled motion'}
(out/'flight-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('PATH_CHECK',json.dumps({'hits':hits,'actual_hits':actual_hits,'camera_hits':camera_hits,'gates':gate_reports,'max_turn':max(turns)},ensure_ascii=False),flush=True)
assert not hits and not actual_hits and not camera_hits,'Resolve geometry before saving'
assert all(g['crossings'] for g in gate_reports)
assert max(turns)<6.0
S.camera=cam;S.frame_start=1;S.frame_end=1392;S.render.fps=24;S.render.fps_base=1;S.frame_set(1)
for m in list(S.timeline_markers):S.timeline_markers.remove(m)
for name,t in zip(anchor_names,ts):S.timeline_markers.new(name,frame=1+round(t*24))
S['episode_scope']='58s v03 garden design candidate, C2 corner geometry and curvature-based timing, real moon openings and water skim. Reference only.'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'garden-city-flight-58s-v03.blend'))
print('FLIGHT_V03_READY',dist[-1],max(turns),flush=True)

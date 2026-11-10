"""58 seconds: three real moon-window crossings, smoothed gaze, water skim."""
import bpy,sys,argparse,json,math,bisect,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser();p.add_argument('--root',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);root=Path(a.root)
source=root/'视频制作/第一集全程快飞-20261023-v0.1/episode1-full-route-58s-v01.blend'
out=root/'视频制作/第一集全程快飞-20261023-v0.2';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source));S=bpy.context.scene
old=json.loads((source.parent/'timing-and-batches.json').read_text(encoding='utf8'))
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
add((-3,13.5,1));add((4.5,13.5,2));add((10.8,13.5,2));add((10.8,15.5,1.132));add(original[-1],'end')
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
    if i<=5:r=min(r,2)
    if i>=labels['skim']:r=min(r,3)
    while True:
        u=q-before*r;v=q+after*r;n=max(5,math.ceil(2*r/.15))
        arc=[(1-t)**2*u+2*(1-t)*t*q+t*t*v for t in [j/n for j in range(n+1)]]
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
anchor_names=['start','exit','gateA','gateB','open','gateC','skim','lift','end']
ts=[.8,5.5,10.5,22,25.5,42.5,47,53.5,57]
ss=[dist[min(range(len(path)),key=lambda j:(path[j]-nodes[labels[k]]).length_squared)] for k in anchor_names]
rates=[(b-a)/(tb-ta) for a,b,ta,tb in zip(ss,ss[1:],ts,ts[1:])]
slopes=[0]+[2*x*y/(x+y) for x,y in zip(rates,rates[1:])]+[0]
for name,speed in [('gateA',10),('gateB',12),('gateC',10),('skim',18),('lift',8)]:slopes[anchor_names.index(name)]=speed
def at(t):
    if t<=ts[0]:return 0
    if t>=ts[-1]:return dist[-1]
    i=bisect.bisect_right(ts,t)-1;dt=ts[i+1]-ts[i];u=(t-ts[i])/dt
    return (2*u**3-3*u*u+1)*ss[i]+(u**3-2*u*u+u)*dt*slopes[i]+(-2*u**3+3*u*u)*ss[i+1]+(u**3-u*u)*dt*slopes[i+1]
positions=[pos(at((f-1)/24)) for f in range(1,1393)]
raw_yaw=[];raw_pitch=[]
for f in range(1,1393):
    t=(f-1)/24;d=pos(at(min(57,t+.38)))-pos(at(max(.8,t-.22)))
    if d.length<.001:d=(nodes[1]-nodes[0]) if t<1 else nodes[-1]-nodes[-2]
    d.normalize()
    for gate in ['gateA','gateB','gateC']:
        delta=ss[anchor_names.index(gate)]-at(t)
        if -14<delta<40:
            center=nodes[labels[gate]];q=positions[f-1]
            target=(center-q).normalized() if q.x<center.x-1 else Vector((1,0,0))
            weight=min(1,(40-delta)/25,(delta+14)/8);weight=max(0,weight);weight=weight*weight*(3-2*weight)
            d=d.lerp(target,weight).normalized()
    yaw=math.atan2(d.y,d.x);pitch=math.atan2(d.z,math.hypot(d.x,d.y))
    if raw_yaw:
        while yaw-raw_yaw[-1]>math.pi:yaw-=math.tau
        while yaw-raw_yaw[-1]<-math.pi:yaw+=math.tau
    raw_yaw.append(yaw);raw_pitch.append(pitch)
def smooth(vals,sigma=10):
    radius=int(sigma*3);weights=[math.exp(-.5*(j/sigma)**2) for j in range(-radius,radius+1)];den=sum(weights)
    return [sum(w*vals[min(len(vals)-1,max(0,i+j))] for j,w in zip(range(-radius,radius+1),weights))/den for i in range(len(vals))]
yaws=smooth(raw_yaw);pitches=smooth(raw_pitch)
# Offline anticipation and bounded turn rate. No roll, no one-frame path-heading snaps.
for values in [yaws,pitches]:
    limit=math.radians(2.2)
    for _ in range(4):
        for i in range(1,len(values)):values[i]=max(values[i-1]-limit,min(values[i-1]+limit,values[i]))
        for i in range(len(values)-2,-1,-1):values[i]=max(values[i+1]-limit,min(values[i+1]+limit,values[i]))
    values[:]=smooth(values,3)
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
report={'version':'v0.2','source':str(source.relative_to(root)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'duration_s':58,'fps':24,'frame_count':1392,'distance_m':dist[-1],'max_speed_m_s':max(r['speed_m_s'] for r in records),'max_camera_turn_deg_per_frame':max(turns),'camera_turns_over_10deg':sum(x>10 for x in turns),'source_max_camera_turn_deg_per_frame':54.8118200815,'anchors':[{'name':n,'time_s':t,'arc_m':s} for n,t,s in zip(anchor_names,ts,ss)],'control_points':[list(q) for q in nodes],'corners':corners,'dense_path_samples':len(path),'path_hits':hits,'frame_envelope_hits':actual_hits,'camera_hits':camera_hits,'gates':gate_reports,'skim':{'root_z_m':.25,'water_z_m':-.48,'minimum_body_z_m':.165,'nominal_body_water_clearance_m':.645,'camera_height_over_water_m':1.07,'lift_before_bridge':True},'batches':old['batches'],'records':records}
(out/'flight-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('PATH_CHECK',json.dumps({'hits':hits,'actual_hits':actual_hits,'camera_hits':camera_hits,'gates':gate_reports,'max_turn':max(turns)},ensure_ascii=False),flush=True)
assert not hits and not actual_hits and not camera_hits,'Resolve geometry before saving'
assert all(g['crossings'] for g in gate_reports)
assert max(turns)<3.3
S.camera=cam;S.frame_start=1;S.frame_end=1392;S.render.fps=24;S.render.fps_base=1;S.frame_set(1)
for m in list(S.timeline_markers):S.timeline_markers.remove(m)
for name,f in [('B01 start',1),('Moon A',253),('Moon B',529),('B02 start',673),('Moon C',1021),('Water skim',1129),('Bridge climb',1285),('End',1392)]:S.timeline_markers.new(name,frame=f)
S['episode_scope']='58s v0.2 three real moon openings, low water flight, smooth camera. Reference only.'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'episode1-full-route-58s-v02.blend'))
print('FLIGHT_V02_READY',dist[-1],max(turns),flush=True)

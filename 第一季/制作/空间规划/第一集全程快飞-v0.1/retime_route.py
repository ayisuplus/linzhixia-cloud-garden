"""58-second end-to-end flight timeline, two 30-second windows with 2 seconds shared."""
import bpy,json,math,sys,hashlib,argparse,bisect
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);ROOT=Path(a.root)
SOURCE=ROOT/'视频制作/第一集无人机试飞-20261022-v0.2/episode1-drone-rehearsal-v02.blend';OUT=ROOT/'视频制作/第一集全程快飞-20261023-v0.1';OUT.mkdir(exist_ok=True,parents=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));S=bpy.context.scene
data=json.loads((ROOT/'视频制作/第一集浮空园城-20261022-v0.4/route-layout.json').read_text(encoding='utf8'));points=[Vector(x) for x in data['flight_points']]
dg=bpy.context.evaluated_depsgraph_get();verts=[];faces=[];names=[]
for o in S.objects:
    if o.type!='MESH' or not o.get('physical',True) or any(c.name in {'E01_FLIGHT_PROXY','V05_TEMPORARY_QUADROTOR','V06_CLOUD_EDGE_REFINEMENT'} for c in o.users_collection):continue
    ev=o.evaluated_get(dg);mesh=ev.to_mesh();base=len(verts);verts.extend(ev.matrix_world@v.co for v in mesh.vertices);faces.extend(tuple(base+i for i in f.vertices) for f in mesh.polygons);names.extend([o.name]*len(mesh.polygons));ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,faces);offsets=[Vector((x,y,z)) for x in [-.61,0,.61] for y in [-.61,0,.61] for z in [-.085,.17,.41]]
def hits_path(path):
    hits=[]
    for aa,bb in zip(path,path[1:]):
        d=bb-aa
        if d.length<1e-6:continue
        for off in offsets:
            h=bvh.ray_cast(aa+off,d.normalized(),d.length+.00001)
            if h[2] is not None:hits.append(names[h[2]])
    return sorted(set(hits))
path=[points[0]];corners=[]
def append_line(a,b):
    count=max(1,math.ceil((b-a).length/.35));path.extend(a.lerp(b,j/count) for j in range(1,count+1))
for i in range(1,len(points)-1):
    q=points[i];before=(q-points[i-1]).normalized();after=(points[i+1]-q).normalized();r=min(12,(q-points[i-1]).length*.2,(points[i+1]-q).length*.2)
    if i<=10 or 14<=i<=19 or i>=27:r=min(r,2)
    while True:
        aa=q-before*r;bb=q+after*r;n=max(4,math.ceil(2*r/.2));arc=[(1-t)**2*aa+2*(1-t)*t*q+t*t*bb for t in [j/n for j in range(n+1)]]
        hit=hits_path(arc)
        if not hit or r<.01:break
        r*=.5
    if hit:raise RuntimeError(f'Unresolved corner {i}: {hit}')
    append_line(path[-1],aa);path.extend(arc[1:]);corners.append({'index':i,'trim_m':r})
append_line(path[-1],points[-1]);hits=hits_path(path);assert not hits,hits
dist=[0]
for a0,b0 in zip(path,path[1:]):dist.append(dist[-1]+(b0-a0).length)
def position(s):
    s=max(0,min(dist[-1],s));i=min(len(path)-2,max(0,bisect.bisect_right(dist,s)-1));den=dist[i+1]-dist[i];return path[i].lerp(path[i+1],(s-dist[i])/den if den else 0)
indices=[0,5,10,14,19,27,34,36];ts=[1,6,12,20,28,45,54,57]
ss=[dist[min(range(len(path)),key=lambda j:(path[j]-points[i]).length_squared)] for i in indices]
rates=[(b-a)/(tb-ta) for a,b,ta,tb in zip(ss,ss[1:],ts,ts[1:])];slopes=[0]+[2*x*y/(x+y) for x,y in zip(rates,rates[1:])]+[0]
def distance_at(t):
    if t<=ts[0]:return 0
    if t>=ts[-1]:return dist[-1]
    i=bisect.bisect_right(ts,t)-1;dt=ts[i+1]-ts[i];u=(t-ts[i])/dt
    return (2*u**3-3*u*u+1)*ss[i]+(u**3-2*u*u+u)*dt*slopes[i]+(-2*u**3+3*u*u)*ss[i+1]+(u**3-u*u)*dt*slopes[i+1]
drone=S.objects['Same carrier ROOT placeholder'];drone.animation_data_clear();drone.rotation_mode='QUATERNION'
rotors=[o for o in S.objects if o.name.startswith('Rotor hub')]
for j,o in enumerate(rotors):
    o.animation_data_clear()
    for frame in [1,1392]:
        o.rotation_euler.z=(1 if j%2 else -1)*(frame-1)/24*math.tau*43.7;o.keyframe_insert('rotation_euler',frame=frame)
camdata=bpy.data.cameras.new('Fast full-route lens');camdata.lens=22;camdata.clip_start=.03;camdata.clip_end=3000
cam=bpy.data.objects.new('FAST_ROUTE_FPV',camdata);S.collection.objects.link(cam);cam.rotation_mode='QUATERNION';S.camera=cam
# This is an on-board path rehearsal. The carrier remains in the scene, hidden only from its own camera.
for name in ['E01_FLIGHT_PROXY','V05_TEMPORARY_QUADROTOR']:
    for o in bpy.data.collections[name].objects:
        if o.type=='MESH':o.visible_camera=False
records=[];camera_hits=[]
lastq=None
for frame in range(1,1393):
    t=(frame-1)/24;s=distance_at(t);q=position(s);velocity=(distance_at(t+.02)-distance_at(t-.02))/.04
    look=position(s+max(1.5,min(12,velocity*.12)))-position(max(0,s-.4))
    if look.length<.001:look=points[-1]-points[-2]
    forward=look.normalized();orientation=forward.to_track_quat('Y','Z');drone.location=q;drone.rotation_quaternion=orientation;drone.keyframe_insert('location',frame=frame);drone.keyframe_insert('rotation_quaternion',frame=frame)
    # Centered within the original checked envelope; no multi-metre chase offset through walls.
    eye=q+Vector((0,0,.34));cam.location=eye;cam.rotation_quaternion=forward.to_track_quat('-Z','Y');cam.keyframe_insert('location',frame=frame);cam.keyframe_insert('rotation_quaternion',frame=frame)
    if lastq is not None:
        delta=eye-lastq
        if delta.length>1e-6:
            h=bvh.ray_cast(lastq,delta.normalized(),delta.length)
            if h[2] is not None:camera_hits.append([frame,names[h[2]]])
    lastq=eye;records.append({'frame':frame,'time_s':t,'arc_m':s,'position':list(q),'camera':list(eye),'speed_m_s':velocity})
assert not camera_hits,camera_hits
for ob in [drone,cam]+rotors:
    for layer in ob.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for k in fc.keyframe_points:k.interpolation='LINEAR'
# Preserve the rigid parcel upright: the path proxy yaws, it does not pitch the cradle with a steep camera look.
for frame,r in enumerate(records,1):
    s=r['arc_m'];v=position(s+1)-position(s-1);v.z=0
    if v.length<.001:v=Vector((0,1,0))
    drone.rotation_quaternion=Vector((0,1,0)).rotation_difference(v.normalized());drone.keyframe_insert('rotation_quaternion',frame=frame)
S.frame_start=1;S.frame_end=1392;S.render.fps=24;S.render.fps_base=1;S.frame_set(1)
for m in list(S.timeline_markers):S.timeline_markers.remove(m)
for name,f in [('B01 start',1),('B02 start / overlap begins',673),('B01 end / overlap ends',720),('Delivery complete',1392)]:S.timeline_markers.new(name,frame=f)
S['episode_scope']='58-second full-route timing draft; on-board camera rehearsal; not final filmed handoff or generated video.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'episode1-full-route-58s-v01.blend'))
report={'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'duration_s':58,'fps':24,'frame_count':1392,'distance_m':dist[-1],'old_route_distance_m':data['flight_distance_m'],'max_speed_m_s':max(r['speed_m_s'] for r in records),'average_speed_m_s':dist[-1]/58,'corners':corners,'path_samples':len(path),'obstacle_hits':hits,'camera_hits':camera_hits,'anchors':[{'route_point':i,'time_s':t,'arc_m':s} for i,t,s in zip(indices,ts,ss)],'batches':[{'id':'E01-C-FAST-B01','duration_s':30,'global_frames':[1,720],'global_time_s':[0,30]},{'id':'E01-C-FAST-B02','duration_s':30,'global_frames':[673,1392],'global_time_s':[28,58],'trim_first_frames_after_matching':48}],'records':records,'limits':['Timeline draft and sampled geometry checks, not flight dynamics certification.','On-board camera, not final parcel-follow camera; carrier is hidden from its own camera.','Endpoint proxies hold 1s; human loading, releasing hands and receiving parcel are not animated.','Cloud appearance retained, optical visibility and full-speed viewing remain unrendered.','No AI video generation submitted.']}
(OUT/'timing-and-batches.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('FULL_ROUTE_TIMELINE_READY',dist[-1],report['max_speed_m_s'],len(path),flush=True)

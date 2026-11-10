"""A continuous local drone rehearsal over the accepted route, without AI generation."""
import bpy,math,json,sys,argparse,ast,hashlib,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--render',default='preview');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
ROOT=Path(a.root).resolve();SOURCE=ROOT/'视频制作/第一集浮空园城-20261022-v0.4/episode1-floating-garden-v04.blend'
OUT=ROOT/'视频制作/第一集无人机试飞-20261022-v0.1';OUT.mkdir(exist_ok=True,parents=True)
data=json.loads(SOURCE.with_name('route-layout.json').read_text(encoding='utf8'))
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));S=bpy.context.scene
helper=ROOT/'第一季/制作/空间规划/第一集场景-v0.1/build_episode.py';names={'section','group','box','ell','rod','surf'}
exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(helper),'exec'))
COL={};G=None;M={k:bpy.data.materials[n] for k,n in {'ceramic':'Ivory ceramic','sage':'Sage bedding','ink':'School ink timber','brass':'Muted brass'}.items()}
root=S.objects['Same carrier ROOT placeholder'];root.animation_data_clear();root.rotation_mode='QUATERNION'
for o in bpy.data.collections['E01_FLIGHT_PROXY'].objects:
    o.hide_render=False;o.hide_set(False)
    if o.name.startswith(('Carrier body','Folded wing')):o.hide_render=True;o.hide_set(True)
section('V05_TEMPORARY_QUADROTOR')
body=ell('Temporary quadrotor fuselage',(0,0,.21),(.19,.27,.12),'ceramic');body.parent=root
rotors=[]
for x,y in [(-.28,-.28),(-.28,.28),(.28,-.28),(.28,.28)]:
    rod('Drone arm',(x*.25,y*.25,.19),(x,y,.29),.026,'sage').parent=root
    ell('Drone motor',(x,y,.30),(.047,.047,.055),'ink').parent=root
    rotor=bpy.data.objects.new('Rotor hub',None);G.objects.link(rotor);rotor.parent=root;rotor.location=(x,y,.36);rotors.append(rotor)
    blade=ell('Rotor blade',(0,0,0),(.19,.022,.009),'ink');blade.parent=rotor
    rod('Landing strut',(x*.70,y*.70,.14),(x*.70,y*.70,-.07),.014,'brass').parent=root
root['role']='Temporary generic quadrotor carrying the existing rigid parcel; not adopted vehicle design'
points=[Vector(v) for v in data['flight_points'][15:20]];times=[0,7,12,16,24];FPS=24;N=24*FPS
lengths=[(b-c).length for c,b in zip(points,points[1:])];cum=[0]
for d in lengths:cum.append(cum[-1]+d)
def sample_distance(t):
    t=max(0,min(24,t));i=min(3,next((j for j in range(4) if t<=times[j+1]),3));u=(t-times[i])/(times[i+1]-times[i]);e=u*u*(3-2*u)
    return cum[i]+lengths[i]*e
def at_distance(s):
    if s<0:return points[0]+(points[1]-points[0]).normalized()*s
    if s>cum[-1]:return points[-1]+(points[-1]-points[-2]).normalized()*(s-cum[-1])
    i=min(3,next((j for j in range(4) if s<=cum[j+1]),3));return points[i].lerp(points[i+1],(s-cum[i])/lengths[i])
def heading(t):
    # Anticipate turns over a 1.4 s window, including the momentary stop at each corner.
    d=at_distance(sample_distance(t+.7)+.05)-at_distance(sample_distance(t-.7)-.05);d.z=0;return d.normalized()
camdata=bpy.data.cameras.new('Drone rehearsal follow lens');camdata.lens=26;camdata.clip_start=.05;camdata.clip_end=2800
cam=bpy.data.objects.new('Drone rehearsal FOLLOW',camdata);G.objects.link(cam);cam.rotation_mode='QUATERNION';S.camera=cam
records=[]
for f in range(1,N+1):
    t=(f-1)/(N-1)*24;d=sample_distance(t);q=at_distance(d);forward=heading(t)
    root.location=q;root.rotation_quaternion=Vector((0,1,0)).rotation_difference(forward);root.keyframe_insert('location',frame=f);root.keyframe_insert('rotation_quaternion',frame=f)
    # Side-follow oriented toward the water pavilion, so the actual screen-to-reveal relationship stays in frame.
    reveal=Vector((-810,678,q.z))-q;reveal.normalize();side=Vector((-reveal.y,reveal.x,0))
    cp=q-reveal*4+side*.45+Vector((0,0,1.05))
    target=q+reveal+Vector((0,0,1.05));cam.location=cp;cam.rotation_quaternion=(target-cp).to_track_quat('-Z','Y');cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_quaternion',frame=f)
    for j,rotor in enumerate(rotors):
        rotor.rotation_euler.z=(1 if j%2 else -1)*t*math.tau*43.7;rotor.keyframe_insert('rotation_euler',frame=f)
    records.append({'frame':f,'time_s':t,'drone':list(q),'camera':list(cp),'target':list(target),'forward':list(forward)})
for o in [root,cam]+rotors:
    if o.animation_data and o.animation_data.action:
        for layer in o.animation_data.action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for k in fc.keyframe_points:k.interpolation='LINEAR'
S.frame_start=1;S.frame_end=N;S.render.fps=FPS;S.render.fps_base=1;S.frame_set(1)
# One combined evaluated BVH, excluding the carrier. Geometric checks are sampled, not a flight physics simulation.
dg=bpy.context.evaluated_depsgraph_get();vs=[];fs=[];ns=[]
for o in S.objects:
    if o.type!='MESH' or o.get('physical',True)==False or any(c.name in {'E01_FLIGHT_PROXY','V05_TEMPORARY_QUADROTOR'} for c in o.users_collection):continue
    ev=o.evaluated_get(dg);mesh=ev.to_mesh();base=len(vs);vs.extend(ev.matrix_world@v.co for v in mesh.vertices);fs.extend(tuple(base+i for i in p.vertices) for p in mesh.polygons);ns.extend([o.name]*len(mesh.polygons));ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(vs,fs)
def ray(a,b):
    delta=b-a
    if delta.length<.00001:return None
    hit=bvh.ray_cast(a,delta.normalized(),delta.length)
    return ns[hit[2]] if hit[2] is not None else None
hits=[];camera_hits=[];sight_hits=[]
for r,n in zip(records,records[1:]):
    aa,bb=Vector(r['drone']),Vector(n['drone']);steps=max(1,math.ceil((bb-aa).length/.2))
    for j in range(steps):
        p0=aa.lerp(bb,j/steps);p1=aa.lerp(bb,(j+1)/steps)
        for dx in [-.61,0,.61]:
            for dy in [-.61,0,.61]:
                for dz in [-.085,.17,.41]:
                    off=Vector((dx,dy,dz));hit=ray(p0+off,p1+off)
                    if hit:hits.append([r['frame'],hit])
    ca,cb=Vector(r['camera']),Vector(n['camera'])
    for off in [Vector(),Vector((.12,0,0)),Vector((-.12,0,0)),Vector((0,.12,0)),Vector((0,-.12,0)),Vector((0,0,.12)),Vector((0,0,-.12))]:
        hit=ray(ca+off,cb+off)
        if hit:camera_hits.append([r['frame'],hit])
    hit=ray(ca,aa+Vector((0,0,.15)))
    if hit:sight_hits.append([r['frame'],hit])
reveal_rays=[{'frame':r['frame'],'first_hit':ray(Vector(r['camera']),Vector((-810,678,68)))} for r in records]
report={'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'route_indices':[15,16,17,18,19],'duration_s':24,'fps':FPS,'frames':N,'distance_m':cum[-1],'max_analytic_speed_m_s':max(1.5*l/(b-a) for l,a,b in zip(lengths,times,times[1:])),'drone_hits':hits,'camera_hits':camera_hits,'carrier_sightline_hits':sight_hits,'landmark_sightlines':reveal_rays,'scope':'27 rays across +/-0.61m xy and -0.085..0.41m z envelope, <=0.2m forward spacing; camera center and 6 offset tracks; per-frame camera-to-carrier ray. Sampled geometry, not complete swept-volume or physical flight simulation. Temporary vehicle, 24 native fps, no audio.','same_parcel_object':'SAME_PARCEL','records':records}
(OUT/'flight-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('FLIGHT_CHECKS',len(hits),len(camera_hits),len(sight_hits),flush=True)
if hits or camera_hits or sight_hits:raise RuntimeError('Flight checks failed; inspect flight-checks.json before rendering')
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
S.render.engine='CYCLES';S.cycles.device='GPU';S.cycles.samples=12;S.cycles.max_bounces=3;S.cycles.volume_bounces=0;S.cycles.volume_step_rate=4;S.cycles.volume_max_steps=128;S.cycles.use_denoising=True;S.render.use_persistent_data=True
S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG'
S['episode_scope']='24s continuous B reveal rehearsal, existing route indices15-19, not full route or final C sequence.'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'episode1-drone-rehearsal-v01.blend'))
frames=range(1,N+1) if a.render=='all' else [1,120,200,288,384,480,576] if a.render=='preview' else []
folder=OUT/('frames' if a.render=='all' else 'preview');folder.mkdir(exist_ok=True)
for f in frames:
    S.frame_set(f);S.render.filepath=str(folder/f'{f:04d}.png');t=time.time();bpy.ops.render.render(write_still=True);print('FLIGHT_FRAME',f,round(time.time()-t,2),flush=True)
print('FLIGHT_BUILD_COMPLETE',flush=True)

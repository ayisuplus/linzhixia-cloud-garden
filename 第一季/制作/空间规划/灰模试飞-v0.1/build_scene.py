"""Blender 5.1: local garden blockout and camera rehearsal, metres, Z up.
Run: blender -b --python build_scene.py -- [stills|flight]
The source route stays unchanged. Outputs are preproduction candidates.
"""
import bpy, json, math, sys
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / '视频制作' / '灰模试飞-v0.1'
OUT.mkdir(parents=True, exist_ok=True)
DATA = json.loads((HERE.parent / '无人机航线-v0.1.json').read_text(encoding='utf-8-sig'))
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.render.engine = 'BLENDER_WORKBENCH'
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.render.image_settings.file_format = 'PNG'
shade = scene.display.shading
shade.light = 'STUDIO'
shade.studiolight_rotate_z = 0.5
shade.color_type = 'MATERIAL'
shade.show_shadows = True
shade.show_cavity = True
shade.cavity_type = 'BOTH'
shade.curvature_ridge_factor = 1.4
shade.curvature_valley_factor = 1.1
shade.show_object_outline = True
shade.background_type = 'WORLD'
scene.world = bpy.data.worlds.new('pale sky')
scene.world.color = (0.68, 0.74, 0.79)
scene.view_settings.view_transform = 'Standard'

def material(name, color):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    return m
stone = material('warm gray plaster', (.66,.66,.63))
roofmat = material('roof gray', (.32,.37,.38))
base = material('floating foundation', (.46,.48,.47))
water = material('water placeholder', (.48,.66,.70))
green = material('vegetation proxy', (.53,.59,.52))
parcelmat = material('parcel marker', (.78,.58,.35))
route_mat = material('route marker', (.9,.43,.17))
obstacles = []

def box(name, pos, size, mat=stone, collision=True):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if collision: obstacles.append(o)
    return o

def roof(name, x, y, z, w, d, h):
    # Gable mass: envelope remains below the source roof maximum.
    verts = [(x-w/2,y-d/2,z),(x+w/2,y-d/2,z),(x+w/2,y+d/2,z),
             (x-w/2,y+d/2,z),(x-w/2,y,z+h),(x+w/2,y,z+h)]
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], [(0,4,3),(1,2,5),(0,1,5,4),(3,4,5,2),(0,3,2,1)])
    mesh.update()
    o=bpy.data.objects.new(name,mesh)
    scene.collection.objects.link(o)
    o.data.materials.append(roofmat)
    obstacles.append(o)

def house(name,x,y,z,w,d,h):
    box(name+' walls',(x,y,z+h*.34),(w,d,h*.68))
    roof(name+' roof',x,y,z+h*.68,w+3,d+3,h*.32)

def label(text, pos, size=8):
    curve=bpy.data.curves.new(text,'FONT'); curve.body=text; curve.size=size
    curve.align_x='CENTER'
    o=bpy.data.objects.new(text,curve); scene.collection.objects.link(o)
    o.location=pos
    o.data.materials.append(roofmat)
    return o

for g in DATA['gardens']:
    a,b,c,d = g['bounds_xy']; z=g['floor_z']; h=g['roof_max_z']-z
    x,y=(a+c)/2,(b+d)/2; w,dep=c-a,d-b
    box(g['id']+' floating slab',(x,y,z-3),(w,dep,6),base)
    box(g['id']+' lower foundation',(x,y,z-8),(w*.75,dep*.72,4),base)
    # Three building wings around an open court; southern edge remains readable.
    house(g['id']+' north hall',x,b+13,z,w*.67,16,h)
    box(g['id']+' porch eave',(x,b+24,z+h*.56),(w*.67,5,.8),roofmat)
    for px in range(int(x-w*.30),int(x+w*.31),8):
        box(g['id']+' porch column',(px,b+25,z+h*.28),(.6,.6,h*.56),base)
    house(g['id']+' west wing',a+12,y+3,z,14,dep*.42,h*.7)
    if g['id']!='F': house(g['id']+' east wing',c-13,y+3,z,14,dep*.38,h*.75)
    box(g['id']+' pond',(x+8,y+6,z+.10),(w*.27,dep*.27,.18),water)
    box(g['id']+' court path',(x-9,y+5,z+.2),(5,dep*.52,.4))
    for tx,ty in [(a+25,d-14),(c-22,d-18),(x-10,b+30)]:
        box(g['id']+' trunk',(tx,ty,z+2),(1,1,4),base)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=5,location=(tx,ty,z+6))
        tree=bpy.context.object; tree.name=g['id']+' canopy proxy'
        tree.data.materials.append(green); obstacles.append(tree)
    label(g['id'],(x,y-5,z+.5),10 if g['id']!='F' else 7)
    # Low perimeter walls leave a central opening on the southern side.
    box(g['id']+' south wall L',(a+w*.18,d-1,z+1),(w*.36,1,2))
    box(g['id']+' south wall R',(c-w*.18,d-1,z+1),(w*.36,1,2))

def steps(name, start, end, width=5):
    start,end=Vector(start),Vector(end)
    horizontal=Vector((end.x-start.x,end.y-start.y,0))
    length=horizontal.length; n=max(2,math.ceil(abs(end.z-start.z)/.3),math.ceil(length/2))
    for i in range(n):
        t=(i+.5)/n; p=start.lerp(end,t)
        o=box(name+f' {i:03}',(p.x,p.y,p.z-.3),(length/n+.04,width,.6))
        o.rotation_euler.z=math.atan2(horizontal.y,horizontal.x)

steps('AB stair',(140,50,60),(190,50,40))
steps('BC stair',(310,60,40),(340,60,60))
steps('BD west walk',(190,100,40),(160,220,18))
steps('CE east walk',(450,120,60),(445,220,30))
steps('D south walk',(160,310,18),(220,350,0))
steps('F approach',(220,350,0),(255,350,0))
# Crossing bridge: stairs at the ends, clear central underside at Z=21.
steps('bridge west stairs',(265,300,18),(280,300,24),8)
box('DE bridge central span',(307.5,300,22.5),(55,8,3))
steps('bridge east stairs',(335,300,24),(350,300,30),8)
for yy in [296,304]:
    box('bridge rail',(307.5,yy,25),(55,.5,2))
    for xx in range(282,335,5): box('bridge post',(xx,yy,25.2),(.5,.5,2.4))
# Water leaves the southern edge of C and falls to its own collecting platform.
box('C channel support',(345,124,56.8),(12,16,2.4),base)
box('C upper water channel',(345,124,58.1),(8,16,.2),water)
box('waterfall sheet',(345,130,41),(7,.6,34),water,False)
box('collector platform',(345,132,22),(23,23,4),base)
box('collector pool',(345,132,24.12),(20,20,.24),water)
box('canal bed',(275,337,-1),(120,9,2),base)
box('canal water',(275,337,.12),(118,7,.24),water)
box('departure apron',(145,85,59.7),(10,10,.6))
box('receiving apron',(260,350,-.3),(10,10,.6))
# Half Garden front entrance stays north, away from the aerial corridor.
for xx in [254,266]: box('F gate pillar',(xx,355,3),(.8,.8,6))
roof('F north gate roof',260,355,6,15,4,2)

route=[Vector(p['xyz']) for p in DATA['route']]
lengths=[0.]
for a,b in zip(route,route[1:]): lengths.append(lengths[-1]+(b-a).length)

def route_at(t):
    distance=max(0,min(1,t))*lengths[-1]
    for i in range(len(route)-1):
        if distance<=lengths[i+1]:
            return route[i].lerp(route[i+1],(distance-lengths[i])/(lengths[i+1]-lengths[i]))
    return route[-1].copy()

bpy.ops.object.empty_add(); drone=bpy.context.object; drone.name='PARCEL_DRONE'
def dronepart(name,pos,size,mat):
    o=box(name,pos,size,mat,False); o.parent=drone; return o
dronepart('rigid tray',(0,0,-.45),(1.2,1,.15),roofmat)
dronepart('old-shoe parcel',(0,0,-.2),(.85,.65,.4),parcelmat)
dronepart('parcel tie',(0,0,.01),(.10,.67,.03),stone)
dronepart('drone body',(0,0,.35),(.8,.8,.25),stone)
for xx in [-.83,.83]:
    for yy in [-.83,.83]:
        arm=dronepart('rotor arm',(xx/2,yy/2,.35),(1.15,.13,.12),roofmat)
        arm.rotation_euler.z=math.atan2(yy,xx)
        bpy.ops.mesh.primitive_torus_add(major_radius=.30,minor_radius=.055,major_segments=16,minor_segments=6,location=(xx,yy,.4))
        o=bpy.context.object; o.name='rotor guard'; o.parent=drone; o.data.materials.append(roofmat)

bpy.ops.object.camera_add(); camera=bpy.context.object; camera.name='FLIGHT_CAMERA'
scene.camera=camera; camera.data.lens=28; camera.data.clip_end=2500
camera.data.clip_start=.15

def aim(obj,p):
    quaternion=(Vector(p)-obj.location).to_track_quat('-Z','Y')
    if obj.rotation_quaternion.dot(quaternion)<0: quaternion.negate()
    obj.rotation_mode='QUATERNION'
    obj.rotation_quaternion=quaternion
def flight_camera(p):
    # Camera position keys blended along the route, no roll or sudden height step.
    # The middle east-facing view reveals C's waterfall; the bridge view lowers early.
    keys=[(0,(10,0,7)),(94,(-14,18,7)),(223,(-14,18,5)),
          (482,(-14,18,5))]
    # Closest point on the input polyline supplies its travelled distance.
    best=(float('inf'),0)
    for i,(a,b) in enumerate(zip(route,route[1:])):
        v=b-a; t=max(0,min(1,(p-a).dot(v)/v.length_squared))
        error=(p-(a+v*t)).length
        if error<best[0]: best=(error,lengths[i]+v.length*t)
    distance=best[1]
    # Explicit editorial cut after P5. Do not interpolate through the drone's head.
    if distance>=270:
        height=6-3*min(1,max(0,(distance-309)/57))
        if distance>432: height=3+3*(distance-432)/50
        return p+Vector((10,-14,height))
    for (d0,o0),(d1,o1) in zip(keys,keys[1:]):
        if distance<=d1:
            return p+Vector(o0).lerp(Vector(o1),(distance-d0)/(d1-d0))
    return p+Vector(keys[-1][1])

N=480
scene.frame_start=1; scene.frame_end=N
for f in range(1,N+1):
    p=route_at((f-1)/(N-1)); drone.location=p
    drone.keyframe_insert(data_path='location',frame=f)
    camera.location=flight_camera(p); aim(camera,p+Vector((0,0,1)))
    camera.keyframe_insert(data_path='location',frame=f)
    camera.keyframe_insert(data_path='rotation_quaternion',frame=f)

for obj in [drone,camera]:
    for layer in obj.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:
                        key.interpolation='LINEAR'
                        if obj==camera and int(key.co.x)==269:
                            key.interpolation='CONSTANT'

# Dense conservative bounding-box audit: inflated obstacle boxes catch close passes.
# It does not model physical air, dynamics, vegetation movement, or final art detail.
bpy.context.view_layer.update()
bounds=[]
for o in obstacles:
    v=[o.matrix_world@Vector(c) for c in o.bound_box]
    bounds.append((o.name,Vector(tuple(min(p[k] for p in v) for k in range(3))),
                            Vector(tuple(max(p[k] for p in v) for k in range(3)))))
def overlaps(p,half,lo,hi): return all(p[k]+half[k]>lo[k]+1e-4 and p[k]-half[k]<hi[k]-1e-4 for k in range(3))
hits={'drone':[],'camera':[]}
for j in range(4001):
    p=route_at(j/4000); c=flight_camera(p)
    for name,lo,hi in bounds:
        if overlaps(p,(1.2,1.2,1),lo,hi): hits['drone'].append((j,name))
        if overlaps(c,(.3,.3,.3),lo,hi): hits['camera'].append((j,name))
report={'samples':4001,'method':'conservative world AABB against solid blockout meshes; route linear',
        'drone_envelope_m':[2.4,2.4,2.0],'camera_half_extent_m':.3,
        'route_length_m':round(lengths[-1],3),'collisions':hits,
        'preview_seconds':N/24,'camera_cut_frame':270,
        'minimum_camera_subject_distance_m':round(min((flight_camera(route_at(j/4000))-route_at(j/4000)).length for j in range(4001)),3),
        'note':'20-second compressed technical rehearsal, not episode timing; explicit cut at frame 270; linear keys, no fluid or flight dynamics'}
(OUT/'flight-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
scene.frame_set(170)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'garden-route-v01.blend'))

mode=sys.argv[-1] if '--' in sys.argv else 'stills'
if mode=='flight':
    (OUT/'frames').mkdir(exist_ok=True)
    scene.render.resolution_x,scene.render.resolution_y=960,540
    scene.render.filepath=str(OUT/'frames'/'flight-')
    bpy.ops.render.render(animation=True)
else:
    # Separate overview camera, leaving the saved flight animation intact.
    bpy.ops.object.camera_add(location=(690,690,590)); overview=bpy.context.object
    overview.name='OVERVIEW'; overview.data.type='ORTHO'; overview.data.ortho_scale=900
    overview.data.clip_end=3000
    aim(overview,(240,210,20)); scene.camera=overview
    curve=bpy.data.curves.new('flight path','CURVE'); curve.dimensions='3D'; curve.bevel_depth=.45
    spline=curve.splines.new('POLY'); spline.points.add(len(route)-1)
    for point,p in zip(spline.points,route): point.co=(*p,1)
    path=bpy.data.objects.new('flight path overview only',curve); scene.collection.objects.link(path)
    path.data.materials.append(route_mat)
    scene.render.filepath=str(OUT/'overview.png'); bpy.ops.render.render(write_still=True)
    path.hide_render=True; scene.camera=camera
    for f,name in [(85,'01-school'),(218,'02-waterfall'),(285,'03-gardens'),(402,'04-under-bridge'),(476,'05-arrival')]:
        scene.frame_set(f); scene.render.filepath=str(OUT/(name+'.png')); bpy.ops.render.render(write_still=True)
print('BLOCKOUT_OUTPUT',str(OUT)); print('COLLISION_COUNTS',{k:len(v) for k,v in hits.items()})

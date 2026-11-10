"""Audit the saved animation, including half frames, rather than just its design path."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[4]/'视频制作'/'灰模试飞-v0.1'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'garden-route-v01.blend'))
scene=bpy.context.scene; camera=scene.camera; drone=bpy.data.objects['PARCEL_DRONE']
solid=[]
for obj in scene.objects:
    if obj.type!='MESH' or obj.parent==drone or obj.name=='waterfall sheet': continue
    corners=[obj.matrix_world@Vector(v) for v in obj.bound_box]
    solid.append((obj.name,[min(v[k] for v in corners) for k in range(3)],
                           [max(v[k] for v in corners) for k in range(3)]))
hits=[]; occluded=[]; min_distance=1e9; bridge_gap=1e9; max_angle=0; previous=None
for j in range(959):
    frame=1+j/2; scene.frame_set(int(frame),subframe=frame%1)
    p=drone.matrix_world.translation; c=camera.matrix_world.translation
    min_distance=min(min_distance,(c-p).length)
    for kind,pos,half in [('drone',p,(1.2,1.2,1)),('camera',c,(.3,.3,.3))]:
        for name,lo,hi in solid:
            if all(pos[k]+half[k]>lo[k]+1e-4 and pos[k]-half[k]<hi[k]-1e-4 for k in range(3)):
                hits.append([frame,kind,name])
    if 278.8<p.x<336.2 and 294.8<p.y<305.2:
        bridge_gap=min(bridge_gap,21-p.z-1)
    direction=p-c
    hit,loc,normal,index,obj,matrix=scene.ray_cast(bpy.context.evaluated_depsgraph_get(),c,direction.normalized(),distance=direction.length)
    if hit and obj.parent!=drone and (loc-c).length<direction.length-1.5:
        occluded.append([frame,obj.name])
    quaternion=camera.matrix_world.to_quaternion()
    if previous and frame!=270:
        angle=math.degrees(previous.rotation_difference(quaternion).angle)
        max_angle=max(max_angle,min(angle,360-angle))
    previous=quaternion
report={'samples':959,'spacing_frames':.5,'actual_saved_animation':True,
        'static_AABB_collisions':hits,'camera_to_drone_center_occlusions':occluded,
        'minimum_camera_subject_distance_m':round(min_distance,3),
        'bridge_envelope_top_clearance_m':round(bridge_gap,3),
        'max_rotation_degrees_per_half_frame_excluding_cut':round(max_angle,3),
        'limits':'Static graybox only; center visibility is not whole-silhouette visibility; dense sampling is not continuous swept-volume proof. Wind, braking, water, final architecture and human comfort not validated.'}
(OUT/'saved-animation-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
assert not hits, 'Saved animation collision'
assert not occluded, 'Drone center occluded'

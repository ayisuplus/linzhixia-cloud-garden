"""4-second 2.5D layout test: painted cards animated using the blockout cameras.
Not frame-by-frame AI video transfer. No water/rotor animation is asserted.
Run after build_scene.py: blender -b --python style_shot.py -- [still|animation]
"""
import bpy, sys, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'视频制作'/'灰模试飞-v0.1'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'garden-route-v01.blend'))
scene=bpy.context.scene
camera=scene.camera
drone=bpy.data.objects['PARCEL_DRONE']
poses=[]
for f in range(96):
    # Frames 216–226 of the technical route, retimed to four seconds.
    frame=216+10*f/95
    scene.frame_set(int(frame),subframe=frame%1)
    poses.append((camera.location.copy(),camera.matrix_world.to_quaternion().to_euler(),drone.location.copy()))
scene.frame_set(218)
reference_location=camera.location.copy()
reference_rotation=camera.matrix_world.to_quaternion().to_euler()
for obj in list(scene.objects):
    if obj!=camera: bpy.data.objects.remove(obj,do_unlink=True)
camera.animation_data_clear()
camera.rotation_mode='XYZ'
scene.render.engine='CYCLES'
scene.cycles.samples=32
scene.cycles.use_denoising=False
scene.cycles.max_bounces=2
scene.cycles.transparent_max_bounces=4
scene.render.resolution_x,scene.render.resolution_y=1280,720
scene.render.resolution_percentage=100
scene.render.fps=24
scene.frame_start=1; scene.frame_end=96
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.view_settings.view_transform='Standard'
scene.view_settings.look='None'
scene.view_settings.exposure=0
scene.view_settings.gamma=1

def card(name,path,position,width,height,alpha=False):
    bpy.ops.mesh.primitive_plane_add(size=2,location=position)
    obj=bpy.context.object; obj.name=name
    obj.scale=(width/2,height/2,1)
    obj.rotation_euler=reference_rotation
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    nodes=mat.node_tree.nodes; nodes.clear(); links=mat.node_tree.links
    tex=nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(path))
    tex.interpolation='Linear'; tex.extension='EXTEND'
    emission=nodes.new('ShaderNodeEmission'); links.new(tex.outputs['Color'],emission.inputs['Color'])
    out=nodes.new('ShaderNodeOutputMaterial')
    if alpha:
        transparent=nodes.new('ShaderNodeBsdfTransparent')
        mix=nodes.new('ShaderNodeMixShader')
        links.new(tex.outputs['Alpha'],mix.inputs[0])
        links.new(transparent.outputs[0],mix.inputs[1]); links.new(emission.outputs[0],mix.inputs[2])
        links.new(mix.outputs[0],out.inputs['Surface'])
    else: links.new(emission.outputs[0],out.inputs['Surface'])
    obj.data.materials.append(mat)
    return obj

distance=110
width=distance*camera.data.sensor_width/camera.data.lens
position=reference_location+reference_rotation.to_quaternion()@Vector((0,0,-distance))
# Overscan is checked against all animated camera frustum corners below.
background=card('2D painted garden background',OUT/'waterfall-2d-background-v01.png',position,width*1.16,width*9/16*1.16)
sprite=card('2D parcel drone cel',OUT/'drone-2d-sprite-v01.png',poses[0][2],3.5,3.5*1024/1536,True)
for f,(loc,rot,p) in enumerate(poses,1):
    camera.location=loc; camera.rotation_euler=rot
    camera.keyframe_insert(data_path='location',frame=f)
    camera.keyframe_insert(data_path='rotation_euler',frame=f)
    sprite.location=p
    sprite.keyframe_insert(data_path='location',frame=f)
for obj in [camera,sprite]:
    for layer in obj.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points: key.interpolation='LINEAR'
scene.frame_set(20)
bpy.context.view_layer.update()
normal=reference_rotation.to_quaternion()@Vector((0,0,1))
for loc,rot,p in poses:
    for corner in camera.data.view_frame(scene=scene):
        ray=rot.to_quaternion()@corner
        hit=loc+ray*((position-loc).dot(normal)/ray.dot(normal))
        local=background.matrix_world.inverted()@hit
        assert abs(local.x)<1 and abs(local.y)<1, 'Painted background edge exposed'
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'waterfall-2d-layout-v01.blend'))
if sys.argv[-1]=='animation':
    (OUT/'style-frames').mkdir(exist_ok=True)
    scene.render.filepath=str(OUT/'style-frames'/'style-')
    bpy.ops.render.render(animation=True)
else:
    scene.render.filepath=str(OUT/'style-shot-preview.png')
    bpy.ops.render.render(write_still=True)

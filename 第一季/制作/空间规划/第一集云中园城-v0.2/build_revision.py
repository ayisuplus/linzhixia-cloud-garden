"""Local cloud openings and a smooth camera glance; source buildings and flight positions retained."""
import bpy,sys,json,math,hashlib,time
from pathlib import Path
from mathutils import Quaternion
R=Path(sys.argv[sys.argv.index('--')+1]); O=R/'视频制作/第一集云中园城-20261024-v0.2';O.mkdir(exist_ok=True)
src=R/'视频制作/第一集云中园城-20261024-v0.1/city-within-cloud-reference-v03.blend'
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
origin=bpy.data.objects.new('Cloud clearing world coordinate origin',None);s.collection.objects.link(origin)
# The openings reach the sightlines above the terraces, not just 26 m above their floors.
openings=[('Cascade connected air',(-1050,775,58),(163,103,104)),('Middle courtyard air',(-655,570,46),(165,98,82)),('Lower eastern water air',(-370,325,23),(132,112,72))]
modified=[]
for m in bpy.data.materials:
 if not m.use_nodes or not m.name.startswith(('ENCLOSING CLOUD','MOTHER CLOUD','Ordinary mist /')):continue
 n=m.node_tree.nodes;l=m.node_tree.links;v=next(x for x in n if x.type=='PRINCIPLED_VOLUME');old=v.inputs['Density'].links[0].from_socket
 tc=n.new('ShaderNodeTexCoord');tc.object=origin;tc.label='World coordinates for local inhabited air'
 mask=None
 for name,center,radii in openings:
  sub=n.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';l.new(tc.outputs['Object'],sub.inputs[0]);sub.inputs[1].default_value=center
  div=n.new('ShaderNodeVectorMath');div.operation='DIVIDE';l.new(sub.outputs[0],div.inputs[0]);div.inputs[1].default_value=radii
  length=n.new('ShaderNodeVectorMath');length.operation='LENGTH';l.new(div.outputs[0],length.inputs[0])
  fade=n.new('ShaderNodeMapRange');fade.label=name;fade.clamp=True;fade.interpolation_type='SMOOTHERSTEP';fade.inputs['From Min'].default_value=.62;fade.inputs['From Max'].default_value=1.10;fade.inputs['To Min'].default_value=.015;fade.inputs['To Max'].default_value=1;l.new(length.outputs['Value'],fade.inputs['Value'])
  if mask is None:mask=fade.outputs[0]
  else:
   mn=n.new('ShaderNodeMath');mn.operation='MINIMUM';l.new(mask,mn.inputs[0]);l.new(fade.outputs[0],mn.inputs[1]);mask=mn.outputs[0]
 mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.label='Cloud density reduced only in viewing pockets';l.new(old,mul.inputs[0]);l.new(mask,mul.inputs[1]);l.new(mul.outputs[0],v.inputs['Density'])
 em=v.inputs['Emission Strength'].links[0].from_node;l.new(mul.outputs[0],em.inputs[0])
 # Reduce excessive luminous fill in the lower support; roof/side envelope retains its illumination.
 if m.name.startswith('MOTHER CLOUD') and em.inputs[1].is_linked:
  fill=em.inputs[1].links[0].from_node
  if fill.type=='MAP_RANGE':fill.inputs['To Min'].default_value=.25;fill.inputs['To Max'].default_value=.58
 modified.append(m.name)
cam=s.camera
curves=[fc for la in cam.animation_data.action.layers for st in la.strips for b in st.channelbags for fc in b.fcurves]
rot=sorted([f for f in curves if f.data_path=='rotation_quaternion'],key=lambda f:f.array_index)
poses=[Quaternion([fc.evaluate(f) for fc in rot]) for f in range(1,1393)]
out=[];prev=None
for f,q in enumerate(poses,1):
 t=(f-1)/24;u=(t-10.8)/(19.8-10.8);dip=math.radians(21)*math.sin(math.pi*u)**4 if 0<u<1 else 0
 q=q@Quaternion((1,0,0),-dip);q.normalize()
 if prev is not None and q.dot(prev)<0:q.negate()
 out.append(list(q));prev=q
for i,fc in enumerate(rot):
 fc.keyframe_points.clear();fc.keyframe_points.add(1392)
 fc.keyframe_points.foreach_set('co',[v for f in range(1,1393) for v in (f,out[f-1][i])])
 for k in fc.keyframe_points:k.interpolation='LINEAR'
 fc.update()
s.frame_set(331);s.render.resolution_x=960;s.render.resolution_y=540
s['revision']='v04: locally opened cloud pockets over lower water courts, unchanged trajectory, smooth 21 degree maximum downward camera glance 10.8-19.8 s.'
path=O/'cloud-city-water-reveal-58s-v04.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path))
stats={'source':str(src.relative_to(R)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'cloud_materials_changed':modified,'openings':openings,'architecture_geometry_and_materials_changed':False,'camera_positions_changed':False,'carrier_animation_changed':False,'camera_glance_interval_s':[10.8,19.8],'max_additional_pitch_deg':21,'fps':24,'frames':1392,'duration_s':58}
(O/'revision.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf8')
print('REVISION_READY',flush=True)

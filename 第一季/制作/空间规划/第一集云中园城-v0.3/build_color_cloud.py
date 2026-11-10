"""Author-requested city color and fixed spatial cloud density hierarchy, v05."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集云中园城-20261024-v0.3';O.mkdir(exist_ok=True)
src=R/'视频制作/第一集云中园城-20261024-v0.2/cloud-city-water-reveal-58s-v04.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
palette={'roof':('#34494b','黛青瓦：屋顶与檐口形成深色轮廓'),'wall':('#e4dbc5','暖粉墙：承接天光，不与冷云混成同一白'),'stone':('#a5aa99','青灰石：园路与台基'),'wood':('#8b5836','熟木色：柱廊、门窗及栏杆'),'redwood':('#a4533c','赭红木：第二月窗及听水亭节点'),'water':('#238c7f','青碧水：水庭、跌水与连续水巷'),'pine':('#355d49','松绿：大部分乔木的稳重底色'),'leaf':('#779550','新叶绿：中层与临水植物'),'gold':('#c9a45a','桂黄：少数庭院树冠节点'),'window':('#354c43','深青窗：玻璃/窗洞的暗部')}
def rgba(h):
 vals=[int(h[i:i+2],16)/255 for i in [1,3,5]]
 return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals)+(1,)
def colored(old,role):
 m=old.copy();m.name='CITY05 '+role+' / '+old.name;n=m.node_tree.nodes;l=m.node_tree.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED');base=rgba(palette[role][0]);m.diffuse_color=base
 # Preserve texture/bump. Replace only the base-color ramp's colors, when present.
 if bs.inputs['Base Color'].is_linked and bs.inputs['Base Color'].links[0].from_node.type=='VALTORGB':
  ramp=bs.inputs['Base Color'].links[0].from_node.color_ramp
  for i,e in enumerate(ramp.elements):e.color=tuple(v*(.82+.18*i/max(1,len(ramp.elements)-1)) for v in base[:3])+(1,)
 else:
  for link in list(bs.inputs['Base Color'].links):l.remove(link)
  bs.inputs['Base Color'].default_value=base
 if role=='water':bs.inputs['Roughness'].default_value=.22
 return m
roles={'V04 roof':'roof','Gray clay roof':'roof','V04 wall':'wall','Warm mineral plaster':'wall','V04 stone':'stone','Warm gray garden stone':'stone','V04 wood':'wood','Warm timber / reference-derived family':'wood','V04 water':'water','Longzhou water':'water','Garden leaves':'pine','Sunlit green leaf':'leaf','V04 window':'window'}
copies={};changed=[];counts={}
for ob in s.objects:
 if ob.type!='MESH':continue
 center=ob.matrix_world@(sum((Vector(v) for v in ob.bound_box),Vector())/8);x,y,z=center
 # Preserve adopted home/workshop interiors and the monochrome school. This is exterior city work.
 if x< -1220 or (x> -35 and y<90):continue
 assignments=[]
 for slot in ob.material_slots:
  old=slot.material
  if not old or old.name not in roles:continue
  role=roles[old.name]
  if role in {'pine','leaf'}:
   if ((x+700)/35)**2+((y-560)/30)**2<1 or ((x+380)/27)**2+((y-320)/24)**2<1:role='gold'
   elif int(math.floor(x/42)+math.floor(y/37))%4==0:role='leaf'
   else:role='pine'
  if role=='wood' and (ob.name.startswith(('Water listening pavilion','Moon window trim.001','Reveal B')) or ((x+655)/55)**2+((y-600)/43)**2<1):role='redwood'
  key=(old.name,role)
  if key not in copies:copies[key]=colored(old,role)
  # Object-level binding avoids recoloring linked geometry in other districts.
  slot.link='OBJECT';slot.material=copies[key];assignments.append({'source':old.name,'role':role,'material':copies[key].name});counts[role]=counts.get(role,0)+1
 if assignments:changed.append({'object':ob.name,'assignments':assignments})
# Fixed cloud gaps are anchored in world space, not a moving camera-clear bubble.
origin=bpy.data.objects['Cloud clearing world coordinate origin'];banks=json.loads((R/'视频制作/第一集浮空园城-20261022-v0.4/route-layout.json').read_text('utf8'))['platforms']
cloudchanges=[]
for m in bpy.data.materials:
 if not m.use_nodes or not m.name.startswith(('ENCLOSING CLOUD','MOTHER CLOUD','Ordinary mist /','Lower ambient')):continue
 n=m.node_tree.nodes;l=m.node_tree.links;v=next(q for q in n if q.type=='PRINCIPLED_VOLUME');density=v.inputs['Density'].links[0].from_socket
 tc=n.new('ShaderNodeTexCoord');tc.object=origin;tc.label='Fixed world cloud structure'
 noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=.012;noise.inputs['Detail'].default_value=2.4;noise.inputs['Roughness'].default_value=.6;l.new(tc.outputs['Object'],noise.inputs['Vector'])
 contrast=n.new('ShaderNodeMapRange');contrast.clamp=True;contrast.interpolation_type='SMOOTHERSTEP';contrast.inputs['From Min'].default_value=.34;contrast.inputs['From Max'].default_value=.68;contrast.inputs['To Min'].default_value=.025;contrast.inputs['To Max'].default_value=1.20;l.new(noise.outputs['Fac'],contrast.inputs['Value'])
 mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(density,mul.inputs[0]);l.new(contrast.outputs[0],mul.inputs[1]);density=mul.outputs[0]
 mask=None
 for b in banks:
  if b['center'][0]<-1220:continue
  x,y,z=b['center'];rx,ry=b['radii']
  sub=n.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';l.new(tc.outputs['Object'],sub.inputs[0]);sub.inputs[1].default_value=(x,y,z+18)
  div=n.new('ShaderNodeVectorMath');div.operation='DIVIDE';l.new(sub.outputs[0],div.inputs[0]);div.inputs[1].default_value=(rx*.95,ry*.95,82)
  length=n.new('ShaderNodeVectorMath');length.operation='LENGTH';l.new(div.outputs[0],length.inputs[0])
  fade=n.new('ShaderNodeMapRange');fade.clamp=True;fade.interpolation_type='SMOOTHERSTEP';fade.inputs['From Min'].default_value=.55;fade.inputs['From Max'].default_value=1.16;fade.inputs['To Min'].default_value=.035;fade.inputs['To Max'].default_value=1;l.new(length.outputs['Value'],fade.inputs['Value'])
  if mask is None:mask=fade.outputs[0]
  else:
   mn=n.new('ShaderNodeMath');mn.operation='MINIMUM';l.new(mask,mn.inputs[0]);l.new(fade.outputs[0],mn.inputs[1]);mask=mn.outputs[0]
 clear=n.new('ShaderNodeMath');clear.operation='MULTIPLY';l.new(density,clear.inputs[0]);l.new(mask,clear.inputs[1]);density=clear.outputs[0];l.new(density,v.inputs['Density'])
 # Luminous warm cloud shoulders and cool denser shade, with less uniform self-emission.
 zsep=n.new('ShaderNodeSeparateXYZ');l.new(tc.outputs['Object'],zsep.inputs[0]);height=n.new('ShaderNodeMapRange');height.clamp=True;height.inputs['From Min'].default_value=-80;height.inputs['From Max'].default_value=240;height.inputs['To Min'].default_value=.32;height.inputs['To Max'].default_value=1.0;l.new(zsep.outputs['Z'],height.inputs['Value'])
 em=n.new('ShaderNodeMath');em.operation='MULTIPLY';l.new(density,em.inputs[0]);l.new(height.outputs[0],em.inputs[1]);l.new(em.outputs[0],v.inputs['Emission Strength'])
 color=n.new('ShaderNodeValToRGB');color.color_ramp.elements[0].position=.30;color.color_ramp.elements[0].color=(.48,.67,.95,1);color.color_ramp.elements[1].position=.68;color.color_ramp.elements[1].color=(.98,.99,1,1);l.new(noise.outputs['Fac'],color.inputs[0]);l.new(color.outputs['Color'],v.inputs['Emission Color']);v.inputs['Color'].default_value=(.90,.95,1,1);v.inputs['Anisotropy'].default_value=.28
 cloudchanges.append(m.name)
sun=bpy.data.objects['Neutral morning sun'];sun.data.energy=3.2;sun.data.color=(1,.96,.88);sun.rotation_euler=(.50,-.48,-.75);sun.data.angle=math.radians(9)
world=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND');world.inputs['Color'].default_value=(.36,.53,.74,1);world.inputs['Strength'].default_value=.55
looks=[i.identifier for i in s.view_settings.bl_rna.properties['look'].enum_items]
try:s.view_settings.look='AgX - Medium High Contrast'
except:pass
s['revision']='v05 city exterior palette and fixed world cloud density/lighting hierarchy. Original camera/carrier action retained.';s.frame_set(600)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'cloud-city-color-58s-v05.blend'))
report={'source':str(src.relative_to(R)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'palette_definition':'author-requested design values, sRGB hex converted to linear shader inputs; not measured colors from an artwork','palette':{k:{'srgb_hex':v[0],'linear_rgba':rgba(v[0]),'role':v[1]} for k,v in palette.items()},'bindings_per_role':counts,'changed_object_bindings':changed,'changed_cloud_materials':cloudchanges,'camera_and_carrier_modified':False,'scope':'city exterior, no original home/workshop interior material or school ink material edits','sun':{'energy':3.2,'color_linear':[1,.96,.88]},'view_look':s.view_settings.look}
(O/'color-cloud-plan.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('COLOR_CLOUD_READY',counts,flush=True)

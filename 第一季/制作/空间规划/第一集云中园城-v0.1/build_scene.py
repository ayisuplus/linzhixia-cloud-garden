"""The city is inside a cloud, not arranged on a cloud pedestal."""
import bpy,sys,ast,json,hashlib,math
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集云中园城-20261024-v0.1';P=R/'视频制作/第一集巨云重构-20261024-v0.1';source=P/'mother-cloud-flight-58s-v01.blend';bpy.ops.wm.open_mainfile(filepath=str(source));S=bpy.context.scene;S.frame_set(1)
helper=R/'第一季/制作/空间规划/第一集巨云与遮露重构-v0.1/build_scene.py';tree=ast.parse(helper.read_text('utf8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='volume'],type_ignores=[]),str(helper),'exec'))
hidden=[]
for o in S.objects:
 if o.name.startswith(('Connected outer cloud fold','Distant ordinary cloud proxy')):
  o.hide_render=True;hidden.append(o.name)
support=bpy.data.objects['One connected giant cloud / stable support'];ref=np.load(O/'refined-support-body.npz');sm=bpy.data.meshes.new('Connected support with clear terrace air');sm.from_pydata(ref['vertices'].tolist(),[],ref['faces'].tolist());sm.update()
for material in support.data.materials:sm.materials.append(material)
support.data=sm
col=bpy.data.collections.new('CITY_WITHIN_CLOUD_ENVELOPE');S.collection.children.link(col);d=np.load(O/'enveloping-cloud.npz');mesh=bpy.data.meshes.new('Cloud around inhabited air pockets');mesh.from_pydata(d['vertices'].tolist(),[],d['faces'].tolist());mesh.update();ob=bpy.data.objects.new('One cloud enclosing the city',mesh);col.objects.link(ob);ob['physical']=False;ob['role']='Surrounding atmospheric cloud, distinct from checked stable support';mat=volume('ENCLOSING CLOUD with open courtyards',.023,False,.018);mesh.materials.append(mat)
for poly in mesh.polygons:poly.use_smooth=True
# Soft side clouds descend from the enclosing upper cloud into the gaps between living areas.
# The retained support body is now inside this enclosure, not the sole image of the city.
episode=R/'第一季/制作/空间规划/第一集场景-v0.1/build_episode.py';et=ast.parse(episode.read_text('utf8'));exec(compile(ast.Module(body=[n for n in et.body if isinstance(n,ast.FunctionDef) and n.name in {'surf','ell'}],type_ignores=[]),str(episode),'exec'));G=col;M={'tongue':volume('ENCLOSING CLOUD local side tongues',.044,True,2.1)}
for name,loc,scale in [('North upper cloud connection',(-650,795,160),(155,135,105)),('North garden cloud tongue',(-655,675,94),(100,100,75)),('West upper cloud connection',(-1005,430,146),(155,100,115)),('West courtyard cloud tongue',(-860,460,68),(145,70,65)),('Water district upper cloud connection',(-510,265,160),(130,120,110)),('Water district side cloud tongue',(-530,385,75),(92,105,78))]:
 o=ell(name,loc,scale,'tongue');o['physical']=False;o['role']='Local ordinary cloud reveal mask, connected visually to enclosing cloud'
# Separate inspectable camera views; the actual 58-second camera and carrier are untouched.
for name,loc,target,lens in [('Cloud exterior / partial city glimpses',(-2100,-900,630),(-680,450,30),42),('Cloud garden interior',(-1020,420,95),(-630,570,48),27),('Cloud shoulder cut through inhabited volume',(-1540,430,180),(-1050,750,60),30)]:
 if name=='Cloud garden interior':
  row=json.loads((P/'flight-checks.json').read_text('utf8'))['records'][599];loc=row['camera'];target=Vector(loc)+Vector(row['forward'])*160
 data=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,data);col.objects.link(cam);cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;data.clip_end=9000
S['author_correction']='The city is enveloped inside one giant cloud. Courtyards, streets and sky openings are spaces within it, not buildings sitting on a white cloud pedestal.'
S['design_status']='Cloud-enclosed city candidate. Spatial timing retained; atmospheric framing awaiting visual review.'
S.frame_set(331);bpy.ops.wm.save_as_mainfile(filepath=str(O/'city-within-cloud-58s-v03.blend'))
# Fast reference lighting approximates the bright diffuse bounce in clouds. It does not alter architecture.
S.render.engine='BLENDER_EEVEE';S.eevee.taa_render_samples=16;S.eevee.volumetric_tile_size='4';S.eevee.volumetric_samples=96;S.eevee.use_volume_custom_range=True;S.eevee.volumetric_start=.3;S.eevee.volumetric_end=5000;S.eevee.use_volumetric_shadows=True
for m in bpy.data.materials:
 if not m.use_nodes or not m.name.startswith(('ENCLOSING CLOUD','MOTHER CLOUD','Lower ambient','Ordinary mist /')):continue
 n=m.node_tree.nodes;l=m.node_tree.links;v=next(x for x in n if x.type=='PRINCIPLED_VOLUME');em=v.inputs['Emission Strength'].links[0].from_node;tc=next(x for x in n if x.type=='TEX_COORD');xyz=n.new('ShaderNodeSeparateXYZ');l.new(tc.outputs['Generated'],xyz.inputs[0]);r=n.new('ShaderNodeMapRange');r.inputs['To Min'].default_value=.38;r.inputs['To Max'].default_value=.82;l.new(xyz.outputs['Z'],r.inputs['Value']);l.new(r.outputs[0],em.inputs[1])
S.render.use_motion_blur=False;S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100
S['reference_lighting']='Height-dependent volume fill approximates cloud multiple scattering; not final cloud rendering.'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'city-within-cloud-reference-v03.blend'))
(O/'construction-audit-v03.json').write_text(json.dumps({'source':str(source.relative_to(R)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'hidden_previous_pedestal_visuals':hidden,'architecture_modified':False,'flight_modified':False,'support_modified':'Only removed volume above terrace floors; see support-refinement.json','duration_s':58,'frame_count':1392,'fps':24,'new_cloud_role':'atmospheric envelope around city, with inhabited air pockets and openings to sky; retained support visible within cloud, six local cloud tongues','previous_collision_reports':str(P.relative_to(R)),'previous_visual_status':'cloud-base-only direction superseded by author correction; no completed 58s preview'},ensure_ascii=False,indent=2),encoding='utf8');print('ENCLOSED_CITY_READY',flush=True)

"""Render-only batching. Editable source is never rewritten; keep local shader coordinates."""
import bpy,sys,json,time
import numpy as np
from pathlib import Path
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集云中园城-20261024-v0.3';bpy.ops.wm.open_mainfile(filepath=str(O/'cloud-city-color-58s-v05.blend'));s=bpy.context.scene;s.frame_set(331)
allobs={o.name:o for o in s.objects};root=allobs['Same carrier ROOT placeholder']
dynamic={root}
for ob in s.objects:
 p=ob
 while p:
  if p==root:dynamic.add(ob);break
  p=p.parent
 if ob.animation_data:dynamic.add(ob)
def volume(ob):return ob.type=='MESH' and any(m and m.use_nodes and any(n.type in {'PRINCIPLED_VOLUME','VOLUME_SCATTER','VOLUME_ABSORPTION'} for n in m.node_tree.nodes) for m in ob.data.materials)
volumes={o for o in s.objects if volume(o)}
dg=bpy.context.evaluated_depsgraph_get();groups={};count=0;cache={};sourceverts=0;sourcefaces=0
def summary(ob):
 key=ob.original.name
 if key in cache:return cache[key]
 me=ob.to_mesh();nv=len(me.vertices);nl=len(me.loops);nf=len(me.polygons)
 co=np.empty(nv*3,np.float32);me.vertices.foreach_get('co',co);co=co.reshape(-1,3)
 lv=np.empty(nl,np.int32);me.loops.foreach_get('vertex_index',lv)
 start=np.empty(nf,np.int32);me.polygons.foreach_get('loop_start',start)
 size=np.empty(nf,np.int32);me.polygons.foreach_get('loop_total',size)
 mats=np.empty(nf,np.int32);me.polygons.foreach_get('material_index',mats)
 smooth=np.empty(nf,np.bool_);me.polygons.foreach_get('use_smooth',smooth)
 bb=np.array(ob.original.bound_box);low=bb.min(0);span=np.maximum(bb.max(0)-low,1e-6);gen=((co-low)/span).astype(np.float32)
 result=(co,lv,start,size,mats,smooth,gen,tuple(slot.material.name if slot.material else '' for slot in ob.material_slots));cache[key]=result;ob.to_mesh_clear();return result
for inst in dg.object_instances:
 ob=inst.object;orig=ob.original
 if ob.type not in {'MESH','CURVE','FONT','SURFACE'} or orig.hide_render or orig in dynamic or orig in volumes:continue
 if inst.parent and inst.parent.original.hide_render:continue
 if not inst.show_self:continue
 co,lv,start,size,mi,smooth,gen,mats=summary(ob)
 if not len(co):continue
 mat=np.array(inst.matrix_world,dtype=np.float32);world=co@mat[:3,:3].T+mat[:3,3]
 key=mats
 g=groups.setdefault(key,{'verts':[],'loops':[],'start':[],'size':[],'mi':[],'smooth':[],'gen':[],'local':[],'nv':0,'nl':0})
 g['verts'].append(world);g['loops'].append(lv+g['nv']);g['start'].append(start+g['nl']);g['size'].append(size);g['mi'].append(mi);g['smooth'].append(smooth);g['gen'].append(gen);g['local'].append(co);g['nv']+=len(co);g['nl']+=len(lv)
 sourceverts+=len(co);sourcefaces+=len(size);count+=1
 if count%5000==0:print('BATCH_SCAN',count,flush=True)
# Link only necessary render objects into a scene copy; building originals stay in the authoring file.
new=s.copy();new.name='RENDER ONLY batched static architecture';new.use_fake_user=True;bpy.context.window.scene=new
# A scene copy shares collections. Detach collections from this scene, never unlink original objects globally.
for col in list(new.collection.children):new.collection.children.unlink(col)
for ob in list(new.collection.objects):new.collection.objects.unlink(ob)
keep=dynamic|volumes|{o for o in s.objects if o.type in {'LIGHT'} or o.name=='Cloud clearing world coordinate origin'}|{s.camera}
for ob in keep:
 if not ob.hide_render:new.collection.objects.link(ob)
new.camera=s.camera
materialcopies={}
for gi,(mats,g) in enumerate(groups.items()):
 me=bpy.data.meshes.new(f'Batch mesh {gi:03}');me.vertices.add(g['nv']);me.vertices.foreach_set('co',np.concatenate(g['verts']).ravel());me.loops.add(g['nl']);me.loops.foreach_set('vertex_index',np.concatenate(g['loops']))
 nface=sum(len(x) for x in g['size']);me.polygons.add(nface);me.polygons.foreach_set('loop_start',np.concatenate(g['start']));me.polygons.foreach_set('loop_total',np.concatenate(g['size']));me.polygons.foreach_set('material_index',np.concatenate(g['mi']));me.polygons.foreach_set('use_smooth',np.concatenate(g['smooth']))
 for attr,data in [('source_generated',g['gen']),('source_object',g['local'])]:
  at=me.attributes.new(attr,'FLOAT_VECTOR','POINT');at.data.foreach_set('vector',np.concatenate(data).ravel())
 for name in mats:
  if not name:continue
  if name not in materialcopies:
   orig=bpy.data.materials[name];m=orig.copy();m.name='BATCH shader '+name
   if m.use_nodes:
    nodes=m.node_tree.nodes;links=m.node_tree.links
    for link in list(links):
     if link.from_node.type=='TEX_COORD' and link.from_socket.name in {'Generated','Object'} and link.from_node.object is None:
      at=nodes.new('ShaderNodeAttribute');at.attribute_name='source_generated' if link.from_socket.name=='Generated' else 'source_object';links.new(at.outputs['Vector'],link.to_socket)
   materialcopies[name]=m
  me.materials.append(materialcopies[name])
 me.update();ob=bpy.data.objects.new(f'RENDER STATIC BATCH {gi:03}',me);new.collection.objects.link(ob)
 print('BATCH_BUILT',gi,g['nv'],nface,flush=True)
new['render_only_proxy']='Static geometry baked at frame331, original local/generated texture coordinates retained as attributes. Editable source and its hierarchy remain separate.'
# Delete the old scene in this derivative only to avoid synchronization of tens of thousands of source objects.
bpy.data.scenes.remove(s)
bpy.context.window.scene=new
bpy.ops.outliner.orphans_purge(do_local_ids=True,do_linked_ids=False,do_recursive=True)
new.frame_set(331);bpy.ops.wm.save_as_mainfile(filepath=str(O/'render-only-batched-v05.blend'))
(O/'render-proxy-audit.json').write_text(json.dumps({'source_instance_count':count,'batched_vertices':sourceverts,'batched_polygons':sourcefaces,'batches':len(groups),'objects_after':len(new.objects),'coordinate_attributes':['source_generated','source_object'],'scope':'render derivative only; authoring source untouched; same-frame image comparison required'},indent=2),encoding='utf8');print('PROXY_READY',flush=True)

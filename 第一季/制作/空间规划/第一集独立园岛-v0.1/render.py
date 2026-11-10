import bpy,sys
from pathlib import Path
from mathutils import Vector
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集独立园岛-20261024-v0.1';bpy.ops.wm.open_mainfile(filepath=str(O/'island-garden-masterplan-v16.blend'));s=bpy.context.scene;c=s.camera
views=[('01-overview',(690,-850,610),(5,65,70),48,False),('02-island-separation',(540,-800,320),(0,60,80),45,True),('03-school-to-lower',(-270,-45,176),(-130,85,88),40,False),('04-below-the-fall',(-123,45,92),(-151,101,106),27,False),('05-home-workshop',(365,0,95),(280,-84,60),36,False)]
for name,pos,target,lens,clear in views:
 if len(sys.argv)>sys.argv.index('--')+2 and sys.argv[sys.argv.index('--')+2]!=name:continue
 bpy.data.collections['06 Optional atmospheric enclosure'].hide_render=clear;c.location=pos;c.rotation_quaternion=(Vector(target)-c.location).to_track_quat('-Z','Y');c.data.lens=lens;s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
print('V16_STILLS_READY',flush=True)

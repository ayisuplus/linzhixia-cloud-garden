import bpy,sys
from pathlib import Path
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集云中园城-20261024-v0.4'
bpy.ops.wm.open_mainfile(filepath=str(R/'视频制作/第一集云中园城-20261024-v0.3/render-only-batched-v05.blend'))
bpy.data.objects['One cloud enclosing the city'].hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(O/'diagnostic-no-envelope.blend'))

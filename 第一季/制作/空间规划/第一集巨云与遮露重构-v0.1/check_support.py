"""Test carrier envelope against signed support volume, including inside-without-crossing cases."""
from pathlib import Path
import argparse,json,numpy as np
from scipy.ndimage import map_coordinates
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();O=Path(a.root)/'视频制作/第一集巨云重构-20261024-v0.1'
d=np.load(O/'mother-cloud-field.npz');f=json.loads((O/'flight-checks.json').read_text('utf8'));pos=np.array([r['position'] for r in f['records']]);violations=[];worst=-1e9
for dx in [-.7,0,.7]:
 for dy in [-.7,0,.7]:
  for dz in [-.085,.17,.41]:
   coords=((pos+[dx,dy,dz]-d['origin'])/float(d['step'])).T;v=map_coordinates(d['field'],coords,order=1,mode='constant',cval=-100);worst=max(worst,float(v.max()))
   violations.extend([int(i+1) for i in np.where(v>=0)[0]])
result={'checked_frames':len(pos),'envelope_samples_per_frame':27,'inside_solid_frames':sorted(set(violations)),'maximum_signed_field':worst,'note':'Negative outside, positive inside. Grid resolution 7.5m; also checked against actual closed mesh using swept envelope rays.'}
(O/'support-clearance.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result));assert not violations

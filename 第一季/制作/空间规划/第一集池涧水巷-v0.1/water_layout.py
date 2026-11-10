"""v13 inferred garden-water dimensions, not surveyed engineering sizes."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).parent.parent/'第一集山水总图白模-v0.1'))
import layout as L
# Entire widths. Three campus ponds, rocky valley runnels, intimate lanes,
# one public pool around the existing ferry, then the workshop landing.
ST=np.array([0,.018,.042,.065,.090,.108,.12,.155,.19,.225,.255,.285,.32,.355,.39,.42,.46,.50,.54,.575,.60,.625,.65,.675,.70,.735,.78,.82,.86,.90,.93,.955,.975,1.])
WW=np.array([7,16,6,22,7,14,6,4.8,7.5,4.5,5.5,7,4.5,6.5,4.5,7,9,7,8,9,20,34,30,12,7,9,6.5,8,7,9,7,12,7,5])
def smooth(x):x=np.clip(x,0,1);return x*x*x*(10+x*(-15+6*x))
def full_width(s):
 s=np.asarray(s);i=np.clip(np.searchsorted(ST,s,side='right')-1,0,len(ST)-2);u=smooth((s-ST[i])/(ST[i+1]-ST[i]));return WW[i]*(1-u)+WW[i+1]*u
def width(s,side):
 a=.48+.035*np.sin(np.asarray(s)*19);return full_width(s)*(a if side>0 else 1-a)
def base_map(xyz):
 a=np.atleast_2d(xyz).copy();s,d,_=L.nearest(a[:,:2]);side=np.where(d>=0,1,-1);old=np.where(side>0,L.width(s,1),L.width(s,-1));new=np.where(side>0,width(s,1),width(s,-1));ad=np.abs(d);nd=np.where(ad<=old,ad*new/old,ad-old+new);n=np.column_stack([-np.interp(s,L.SS,L.TANG[:,1]),np.interp(s,L.SS,L.TANG[:,0])]);n/=np.linalg.norm(n,axis=1)[:,None];a[:,:2]+=n*((nd-ad)*side)[:,None];return a
def mapped(xyz,zones):
 a=np.atleast_2d(xyz).copy();base=base_map(a);acc=np.zeros_like(base[:,:2]);total=np.zeros(len(a));cores=[]
 for z in zones:
  lo=np.array(z['lo']);hi=np.array(z['hi']);dist=np.maximum(np.maximum(lo-a[:,:2],a[:,:2]-hi),0).max(1);weight=1-smooth(dist/12);active=weight>0
  correction=a[:,:2]+z['delta']-base[:,:2];acc+=correction*weight[:,None];total+=weight;cores.append(dist==0)
 base[:,:2]+=acc/np.maximum(1,total)[:,None]
 # Exact rigid footprints take precedence over feathered neighbouring patches.
 for z,mask in zip(zones,cores):base[mask,:2]=a[mask,:2]+z['delta']
 return base
def inverse_base(xyz):
 a=np.atleast_2d(xyz).copy();s,d,_=L.nearest(a[:,:2]);old=np.where(d>=0,L.width(s,1),L.width(s,-1));new=np.where(d>=0,width(s,1),width(s,-1));ad=np.abs(d);od=np.where(ad<=new,ad*old/new,ad-new+old);n=np.column_stack([-np.interp(s,L.SS,L.TANG[:,1]),np.interp(s,L.SS,L.TANG[:,0])]);n/=np.linalg.norm(n,axis=1)[:,None];a[:,:2]+=n*((od-ad)*np.where(d>=0,1,-1))[:,None]
 for _ in range(2):a[:,:2]+=np.atleast_2d(xyz)[:,:2]-base_map(a)[:,:2]
 return a

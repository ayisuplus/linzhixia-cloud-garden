"""Compatibility entry; implementation is maintained in the shared creative toolkit."""
from pathlib import Path
import runpy, sys
_project = Path(__file__).resolve().parents[4]
_shared = _project.parent.parent / 'OpenCut' / 'toolkit' / 'scripts/atlas/build_atlas.py'
if not _shared.is_file():
    raise RuntimeError('缺少创作工具库；请运行故事短片/管理/恢复工具链接.ps1检查公共链接')
sys.path.insert(0, str(_shared.parent))
try:
    _implementation = runpy.run_path(str(_shared), run_name='__main__' if __name__ == '__main__' else 'shared_' + Path(__file__).stem)
finally:
    sys.path.pop(0)
if __name__ != '__main__':
    globals().update({k:v for k,v in _implementation.items() if not k.startswith('__')})

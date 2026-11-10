"""Regression checks for shared shot data and immutable prepared snapshots."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
import generation_execution as execution

ROOT=Path(__file__).resolve().parents[4]
CURRENT=ROOT/'视频制作/第一幕分镜与生成-20261018-v2.0'

class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.atlas=json.loads((CURRENT/'atlas.json').read_text(encoding='utf-8'))
        self.plan=json.loads((CURRENT/'plan.json').read_text(encoding='utf-8'))

    def test_source_change_reaches_prompt_and_duration(self):
        self.atlas['shots'][0]['dialogue']='同步验证台词'
        self.atlas['shots'][0]['seconds']=5
        resolved=execution.resolve(ROOT,self.atlas,self.plan)
        self.assertEqual(resolved['units'][0]['edit_seconds'],5)
        self.assertIn('同步验证台词',execution.prompt(self.atlas,resolved['units'][0]))
        self.assertNotIn('dialogue',self.plan['units'][0])

    def test_missing_or_duplicate_shot_rejected(self):
        for ids in [[],['E01-A-000','E01-A-000'],['unknown']]:
            plan=copy.deepcopy(self.plan);plan['units'][0]['shot_ids']=ids
            with self.assertRaises(ValueError): execution.resolve(ROOT,self.atlas,plan)

    def test_derived_values_rejected_in_source(self):
        self.plan['units'][0]['beats']=[]
        with self.assertRaises(ValueError): execution.resolve(ROOT,self.atlas,self.plan)

    def test_prompt_contains_handoffs_and_frame_limits(self):
        resolved=execution.resolve(ROOT,self.atlas,self.plan)
        byid={s['id']:s for s in self.atlas['shots']}
        for u in resolved['units']:
            text=execution.prompt(self.atlas,u)
            for sid in u['shot_ids']:
                self.assertIn(byid[sid]['next_link'],text)
                self.assertIn(byid[sid]['presentation']['missing'],text)
                for f in byid[sid].get('state_frames',[]): self.assertIn(f['limits'],text)

    def test_snapshot_freezes_files_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory(prefix='.snapshot-test-',dir=CURRENT) as name:
            tmp=Path(name);source=tmp/'reference.png';source.write_bytes(b'fixture-input')
            atlas=copy.deepcopy(self.atlas);atlas['shots']=atlas['shots'][:1]
            s=atlas['shots'][0];s['refs']=[dict(path=source.relative_to(ROOT).as_posix(),role='test fixture')]
            plan=copy.deepcopy(self.plan);plan['units']=plan['units'][:1]
            resolved=execution.resolve(ROOT,atlas,plan)
            snapshot=execution.freeze(ROOT,atlas,resolved,'G00',tmp/'frozen')
            before=snapshot.read_bytes();source.write_bytes(b'changed-later')
            self.assertEqual((tmp/'frozen/inputs/001.png').read_bytes(),b'fixture-input')
            with self.assertRaises(FileExistsError): execution.freeze(ROOT,atlas,resolved,'G00',tmp/'frozen')
            self.assertEqual(snapshot.read_bytes(),before)
            plan['units'][0]['runs']=[dict(status='prepared',snapshot=snapshot.relative_to(ROOT).as_posix())]
            execution.resolve(ROOT,atlas,plan)
            run=plan['units'][0]['runs'][0]
            run.update(status='accepted',task_id='fixture-task',engine='fixture-engine',model_version='fixture-version',output=source.relative_to(ROOT).as_posix(),actual_seconds=6,adoption='fixture-only',in_out=[0,4])
            with self.assertRaises(ValueError): execution.resolve(ROOT,atlas,plan)
            video=tmp/'fixture.mp4';video.write_bytes(b'format-test-only-not-real-video')
            run['output']=video.relative_to(ROOT).as_posix();run['in_out']=[0,7]
            with self.assertRaises(ValueError): execution.resolve(ROOT,atlas,plan)
            run['in_out']=[0,4];execution.resolve(ROOT,atlas,plan)
            (tmp/'frozen/inputs/001.png').write_bytes(b'corrupt')
            with self.assertRaises(ValueError): execution.resolve(ROOT,atlas,plan)

    def test_invalid_snapshot_not_accepted(self):
        self.plan['units'][0]['runs']=[dict(status='accepted',snapshot=self.plan['atlas_source'],task_id='fixture',output=self.atlas['shots'][0]['presentation']['path'],actual_seconds=6,adoption='fixture',in_out='nonsense')]
        with self.assertRaises(ValueError): execution.resolve(ROOT,self.atlas,self.plan)

    def test_four_full_batches_reorder_only_whole_shots(self):
        current=ROOT/'视频制作/第一幕分镜与生成-20261018-v2.1'
        atlas=json.loads((current/'atlas.json').read_text(encoding='utf-8'))
        plan=json.loads((current/'plan.json').read_text(encoding='utf-8'))
        self.assertEqual(atlas['shots'],self.atlas['shots'])
        resolved=execution.resolve(ROOT,atlas,plan)
        ai=[u for u in resolved['units'] if u['requested_seconds'] is not None]
        self.assertEqual([u['requested_seconds'] for u in ai],[30,30,30,30])
        self.assertEqual(sum(u['head_handle']+u['tail_handle'] for u in ai),9)
        batch=next(u for u in ai if u['id']=='B03')
        self.assertIsNone(batch['timeline_start']);self.assertIsNone(batch['timeline_end'])
        beat=batch['beats'][-1]
        self.assertEqual((beat['shot_id'],beat['start'],beat['end'],beat['story_start'],beat['story_end']),('E01-A-016-L',25.5,29.5,111,115))
        text=execution.prompt(atlas,batch)
        self.assertIn('明确硬切到下一独立镜头',text)
        self.assertIn('不继承上一镜声音',text)
        for mutation in ['duplicate','missing','note','order']:
            bad=copy.deepcopy(plan)
            if mutation=='duplicate':bad['units'][-1]['shot_ids']=['E01-A-016-L']
            elif mutation=='missing':bad['units'].pop()
            elif mutation=='note':bad['units'][2].pop('generation_note')
            else:bad.pop('coverage_order')
            with self.assertRaises(ValueError): execution.resolve(ROOT,atlas,bad)

    def test_existing_story_and_media_unchanged(self):
        previous=json.loads((ROOT/'视频制作/第一幕关键帧图册-20261018-v1.9/atlas.json').read_text(encoding='utf-8'))
        self.assertEqual([s['id'] for s in previous['shots']],[s['id'] for s in self.atlas['shots']])
        for old,new in zip(previous['shots'],self.atlas['shots']):
            # Final visual review corrected evidence captions, not media or actions.
            if old['id'] in ['E01-A-003', 'E01-A-016']:
                old, new = copy.deepcopy(old), copy.deepcopy(new)
                for s in (old, new):
                    for key in ['visible', 'missing']:
                        s['presentation'].pop(key)
                    for ref in s['refs']:
                        if ref['path'] == s['presentation']['path']:
                            ref.pop('role')
            for key in ['seconds','action','dialogue','sound','refs','presentation','state_frames','exit_state','next_link']:
                self.assertEqual(old.get(key),new.get(key),(old['id'],key))

if __name__=='__main__': unittest.main()

// Browserless regression for the generated page's routing/filtering logic.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(__dirname+'/分镜与生成.html','utf8');
function el(id,dataset={},cls=''){return {id,dataset,hidden:false,value:'',textContent:'',attrs:{},handlers:{},setAttribute(k,v){this.attrs[k]=v},addEventListener(k,f){this.handlers[k]=f},scrollIntoView(){this.scrolled=true},classList:{contains(k){return cls.split(' ').includes(k)}},closest(){return this.dataset.panel?this:(this.panel||null)}}}
const story=el('storyboard',{panel:'storyboard'}),exec=el('execution',{panel:'execution'});
const tabs=[el('tab-story',{view:'storyboard'}),el('tab-exec',{view:'execution'})];
const shot=el('E01-A-010-W',{},'card shot');shot.panel=story;
const batch=el('G05',{},'card batch');batch.panel=exec;
const tile=el('tile',{shot:shot.id,search:'E01-A-010-W 贴窗',trial:'true',gap:'false'});
const filters=['all','trial','gap'].map(filter=>el(filter,{filter}));
const ids=Object.fromEntries([story,exec,shot,batch,el('search'),el('count'),el('empty'),el('print')].map(x=>[x.id,x]));
const handlers={};let hash='';const location={get hash(){return hash},set hash(v){hash=v.startsWith('#')?v:'#'+v}};
const context={location,requestAnimationFrame:f=>f(),window:{addEventListener:(k,f)=>handlers[k]=f,print(){}},document:{getElementById:id=>ids[id],querySelectorAll:s=>({'[data-panel]':[story,exec],'[data-view]':tabs,'.tile':[tile],'[data-filter]':filters}[s]||[])}};
vm.runInNewContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],context);
assert.equal(story.hidden,false);assert.equal(exec.hidden,true);
ids.search.value='不存在';ids.search.handlers.input();assert.equal(shot.hidden,true);assert.equal(ids.empty.hidden,false);
location.hash='#G05';handlers.hashchange();assert.equal(exec.hidden,false);assert.equal(story.hidden,true);
location.hash='#E01-A-010-W';handlers.hashchange();assert.equal(story.hidden,false);assert.equal(shot.hidden,false);assert.equal(ids.search.value,'');assert.equal(tabs[0].attrs['aria-pressed'],'true');
filters[2].handlers.click();assert.equal(shot.hidden,true);
location.hash='#E01-A-010-W';handlers.hashchange();assert.equal(shot.hidden,false);
tabs[1].handlers.click();assert.equal(location.hash,'#execution');assert.equal(exec.hidden,false);
location.hash='#%invalid';handlers.hashchange();assert.equal(story.hidden,false);
console.log('PASS: two views, search, filters, cross-view deep links, hidden-target restoration, malformed hash. Not browser visual verification.');

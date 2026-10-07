const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const crypto=require('node:crypto');
function store(){const data=new Map();const context={crypto,localStorage:{getItem:k=>data.get(k)||null,setItem:(k,v)=>data.set(k,v)}};vm.createContext(context);vm.runInContext(fs.readFileSync('docs/demo-store.js','utf8')+';globalThis.store=demoStore;',context);return context.store}
test('records persist and retain company',()=>{const s=store();s.save({action:'record',kind:'clients',company:'Company B',name:'Demo customer',amount:0});assert.equal(s.read().records.at(-1).company,'Company B')});
test('stock rejects excess usage without changing data',()=>{const s=store();assert.throws(()=>s.save({action:'stock',company:'Company A',direction:'consume',quantity:201}));assert.equal(s.read().stock[0].litres,200);s.save({action:'stock',company:'Company A',direction:'consume',quantity:22});assert.equal(s.read().stock[0].litres,178);assert.equal(s.read().stock[1].litres,200)});
test('retry creates only one site report',()=>{const s=store(),d={action:'report',company:'Company A',home:1,quantity:25,submission:'abc'};s.save(d);s.save(d);assert.equal(s.read().reports.length,1)});

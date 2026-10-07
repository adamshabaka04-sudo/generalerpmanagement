/* The Pages demo uses only local browser storage. No data is sent to a server. */
const demoStore = (() => {
  const key = 'fitout-manager-demo-v1';
  function seed() {
    return {records:[
      {id:1,kind:'clients',company:'Company A',name:'Palm Residence Development',detail:'Dubai · 20-home fit-out',amount:0,status:'Active'},
      {id:2,kind:'projects',company:'Company A',name:'Palm Residence · 20 homes',detail:'Interior painting and fit-out',amount:200000,status:'Planning'},
      {id:3,kind:'purchasing',company:'Company A',name:'Interior paint · 100 litres',detail:'Confirmed incoming supply',amount:2500,status:'Ordered'},
      {id:4,kind:'clients',company:'Company B',name:'Al Noor Trading',detail:'Sharjah · supply-only customer',amount:0,status:'Active'},
      {id:5,kind:'projects',company:'Company C',name:'Marina Apartment Renovation',detail:'Abu Dhabi · interior finishing',amount:85000,status:'Active'}
    ],stock:['Company A','Company B','Company C'].map(company=>({company,litres:200})),reports:[]};
  }
  function read() {
    const saved=localStorage.getItem(key);
    return saved ? JSON.parse(saved) : seed();
  }
  function number(value,label,min=0) {
    const n=Number(value);
    if(!Number.isFinite(n)||n<min)throw Error(`${label} must be at least ${min}.`);
    return n;
  }
  function save(data) {
    const state=read();
    if(!state.stock.some(x=>x.company===data.company))throw Error('Choose a valid company.');
    if(data.action==='record') {
      const statuses={clients:'Active',projects:'Planning',purchasing:'Requested',estimates:'Draft'};
      if(!statuses[data.kind])throw Error('Unknown record type.');
      const name=String(data.name||'').trim();
      if(!name)throw Error('A name is required.');
      state.records.push({id:crypto.randomUUID(),kind:data.kind,company:data.company,name,detail:String(data.detail||''),amount:number(data.amount,'Amount'),status:statuses[data.kind]});
    } else if(data.action==='stock') {
      const qty=number(data.quantity,'Quantity',0.01);
      if(!['receive','consume'].includes(data.direction))throw Error('Invalid movement.');
      const stock=state.stock.find(x=>x.company===data.company);
      const delta=data.direction==='receive'?qty:-qty;
      if(stock.litres+delta<0)throw Error('Insufficient stock for this consumption.');
      stock.litres+=delta;
      state.records.push({id:crypto.randomUUID(),kind:'movements',company:data.company,name:data.direction,detail:String(data.detail||''),amount:qty,status:'Recorded'});
    } else if(data.action==='report') {
      const home=number(data.home,'Home',1),quantity=number(data.quantity,'Completed area');
      if(!Number.isInteger(home)||home>20)throw Error('Home must be between 1 and 20.');
      if(!data.submission)throw Error('Submission ID required.');
      if(!state.reports.some(x=>x.submission===data.submission))state.reports.push({id:crypto.randomUUID(),company:data.company,home,quantity,note:String(data.note||''),submission:data.submission});
    } else throw Error('Unknown action.');
    localStorage.setItem(key,JSON.stringify(state));
  }
  return {read,save};
})();

"""Animated illustrations (HTML canvas + JS) for the rain-forming steps.

They are qualitative pictures of the mechanisms, not model output: drop sizes and speeds are exaggerated so the
steps can be seen. Rendered with streamlit.components.v1.html (scripts do not run inside st.markdown).
"""
from __future__ import annotations

_SHELL = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;background:transparent;font-family:Inter,"Segoe UI",system-ui,sans-serif;color:#0B1F33;}
.w{border:1px solid #E6E9EE;border-radius:18px;overflow:hidden;background:#fff;}
.bar{display:flex;align-items:center;gap:10px;padding:0 14px;border-bottom:1px solid #E6E9EE;height:58px;box-sizing:border-box;}
.chip{flex:none;font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#fff;
  background:__ACC__;border-radius:999px;padding:4px 10px;}
.lab{flex:1;font-size:13.5px;line-height:1.35;min-width:0;}
.btn{flex:none;font:600 12px Inter,system-ui,sans-serif;color:#334155;background:#F1F3F5;border:0;border-radius:8px;
  padding:6px 10px;cursor:pointer;}
.btn:hover{background:#E5E7EB;}
canvas{display:block;width:100%;height:__H__px;}
.note{font-size:11px;color:#6B7A8C;padding:0 14px;height:28px;line-height:28px;border-top:1px solid #F1F3F5;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
</style></head><body><div class="w"><div class="bar"><span class="chip" id="chip">Step 1/5</span>
<span class="lab" id="lab"></span><button class="btn" id="pp">Pause</button><button class="btn" id="rp">Replay</button></div>
<canvas id="c"></canvas><div class="note">Illustration only: sizes and speeds are exaggerated so each step can be seen.</div></div>
<script>
const cv=document.getElementById('c'),ctx=cv.getContext('2d'),H=__H__;let W=600,DPR=1;
function fit(){DPR=window.devicePixelRatio||1;W=cv.clientWidth||600;cv.width=W*DPR;cv.height=H*DPR;ctx.setTransform(DPR,0,0,DPR,0,0);}
fit();let lastW=W;new ResizeObserver(()=>{fit();if(W>0&&Math.abs(W-lastW)>4){lastW=W;if(typeof reset==='function')reset();}}).observe(cv);
const chip=document.getElementById('chip'),lab=document.getElementById('lab');let curStep=0;
function step(n,txt){if(n!==curStep){curStep=n;chip.textContent='Step '+n+'/5';lab.innerHTML=txt;}}
let running=true,visible=true;const pp=document.getElementById('pp');
pp.onclick=()=>{running=!running;pp.textContent=running?'Pause':'Play';};
document.getElementById('rp').onclick=()=>{reset();if(!running){running=true;pp.textContent='Pause';}};
new IntersectionObserver(e=>{visible=e[0].isIntersecting;}).observe(cv);
const rnd=(a,b)=>a+Math.random()*(b-a);
function drop(x,y,r,fill){ctx.beginPath();ctx.moveTo(x,y-r*1.9);ctx.bezierCurveTo(x+r*0.35,y-r*1.1,x+r,y-r*0.3,x+r,y+r*0.25);
  ctx.arc(x,y+r*0.25,r,0,Math.PI);ctx.bezierCurveTo(x-r,y-r*0.3,x-r*0.35,y-r*1.1,x,y-r*1.9);ctx.fillStyle=fill;ctx.fill();}
function circ(x,y,r,fill,stroke){ctx.beginPath();ctx.arc(x,y,Math.max(r,0.1),0,7);if(fill){ctx.fillStyle=fill;ctx.fill();}
  if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=1;ctx.stroke();}}
function txt(s,x,y,col,al,w){ctx.font=(w||'600')+' 12.5px Inter,system-ui,sans-serif';ctx.fillStyle=col;ctx.textAlign=al||'left';ctx.fillText(s,x,y);}
function plane(x,y){ctx.save();ctx.translate(x,y);ctx.scale(1.35,1.35);ctx.fillStyle='#334155';
  ctx.beginPath();ctx.moveTo(-34,-3);ctx.lineTo(22,-4);ctx.quadraticCurveTo(36,-3,38,1);ctx.quadraticCurveTo(36,5,22,5);ctx.lineTo(-30,4);ctx.closePath();ctx.fill();
  ctx.beginPath();ctx.moveTo(-26,-3);ctx.lineTo(-36,-17);ctx.lineTo(-29,-17);ctx.lineTo(-16,-3);ctx.closePath();ctx.fill();
  ctx.fillStyle='#475569';ctx.beginPath();ctx.moveTo(4,1);ctx.lineTo(-10,15);ctx.lineTo(-3,15);ctx.lineTo(14,1);ctx.closePath();ctx.fill();
  ctx.fillStyle='#BFDBFE';for(let i=0;i<5;i++){ctx.beginPath();ctx.arc(16-i*7,-0.5,1.6,0,7);ctx.fill();}
  ctx.beginPath();ctx.moveTo(28,-2.5);ctx.lineTo(34,-0.5);ctx.lineTo(28,0.5);ctx.closePath();ctx.fill();ctx.restore();}
let puffs=[];
function puff(x,y,col){for(let i=0;i<5;i++)puffs.push({x:x+rnd(-4,4),y:y+rnd(-3,3),vx:rnd(-0.6,-0.1),vy:rnd(-0.2,0.4),t:0,col});}
function drawPuffs(){puffs=puffs.filter(q=>q.t<45);for(const q of puffs){q.t++;q.x+=q.vx;q.y+=q.vy;
  circ(q.x,q.y,1.8+q.t*0.04,'rgba('+q.col+','+(0.7*(1-q.t/45))+')');}}
let splashes=[];
function splash(x,y){for(let i=0;i<7;i++)splashes.push({x,y,vx:rnd(-1.4,1.4),vy:rnd(-2.2,-0.8),t:0});}
function drawSplashes(){splashes=splashes.filter(s=>s.t<40);for(const s of splashes){s.t++;s.x+=s.vx;s.y+=s.vy;s.vy+=0.12;
  circ(s.x,s.y,2.4,'rgba(37,99,235,'+(1-s.t/40)+')');}}
__BODY__
reset();
function loop(){if(running&&visible){update();draw();}requestAnimationFrame(loop);}
draw();requestAnimationFrame(loop);
</script></body></html>"""


_WARM = r"""
let cloudTop,base,ground,small,agents,flashes,clock,nextPass,pl;
const MAXA=4,GAP=150;
function geom(){cloudTop=18;base=Math.round(H*0.62);ground=H-16;}
function newSmall(fade){return {x:rnd(12,W-12),y:rnd(cloudTop+18,base-10),r:rnd(3.6,5.6),ph:rnd(0,6.28),a:fade?0:1};}
function target(){return Math.round(W/11);}
function freeX(){for(let k=0;k<20;k++){const x=rnd(W*0.12,W*0.88);if(agents.every(a=>Math.abs(a.x-x)>90))return x;}return rnd(W*0.12,W*0.88);}
function spawn(x){agents.push({x,y:base+40,r:4.5,phase:'rise',t:0,merges:0});
  for(let i=0;i<6;i++)small.push({x:x+rnd(-14,14),y:rnd(cloudTop+70,base-12),r:rnd(3.8,5.4),ph:rnd(0,6.28),a:0});}
function reset(){geom();small=[];for(let i=0;i<target();i++)small.push(newSmall(false));agents=[];flashes=[];splashes=[];
  clock=0;nextPass=0;pl={on:false,x:-60,drops:[]};puffs=[];}
function update(){clock++;
  if(!pl.on&&clock>=nextPass&&agents.length<MAXA){const n=Math.min(MAXA-agents.length,3),xs=[];
    for(let k=0;k<40&&xs.length<n;k++){const x=rnd(W*0.12,W*0.88);if(xs.every(v=>Math.abs(v-x)>150)&&agents.every(a=>Math.abs(a.x-x)>90))xs.push(x);}
    pl={on:true,x:-60,drops:xs.sort((a,b)=>a-b)};}
  if(pl.on){pl.x+=2.4;if(pl.drops.length&&pl.x>=pl.drops[0]){pl.drops.shift();const x=pl.x-40;spawn(x);puff(x,base+40,'148,163,184');}
    if(pl.x>W+70){pl.on=false;nextPass=clock+GAP;}}
  if(small.length<target()&&clock%12===0)small.push(newSmall(true));
  for(const d of small){d.ph+=0.03;d.x+=Math.sin(d.ph)*0.15;d.y+=Math.cos(d.ph*0.7)*0.08;if(d.a<1)d.a=Math.min(1,d.a+0.02);}
  for(const a of agents){a.t++;
    if(a.phase==='rise'){a.y-=1.3;if(a.y<cloudTop+55+rnd(0,25)){a.phase='dissolve';a.t=0;}}
    else if(a.phase==='dissolve'){a.r=4.5+Math.min(a.t/80,1)*7;if(a.t>110){a.phase='fall';a.t=0;}}
    else if(a.phase==='fall'||a.phase==='rain'){a.y+=(0.12+0.0017*a.r*a.r)*(a.y>base?2.2:1);
      for(let i=small.length-1;i>=0;i--){const d=small[i];if(d.a>0.5&&Math.hypot(d.x-a.x,d.y-a.y)<a.r+d.r){
        a.r=Math.min(Math.cbrt(a.r**3+d.r**3*2),24);small.splice(i,1);a.merges++;flashes.push({x:a.x,y:a.y,r:a.r,t:0});}}
      if(a.y>base)a.phase='rain';
      if(a.y>ground-a.r){splash(a.x,ground);a.done=1;}}}
  agents=agents.filter(a=>!a.done);
  const L=agents[0];const s1='An aircraft releases salt particles (NaCl, CaCl<sub>2</sub>) below the cloud; the updraft carries them up.';
  if(!L){if(pl.on)step(1,s1);return;}
  if(L.phase==='rise')step(1,s1);
  else if(L.phase==='dissolve')step(2,'The salt absorbs water and dissolves into a large <b>solution droplet</b> (Raoult &amp; Köhler).');
  else if(L.phase==='fall')step(L.merges?4:3,L.merges?'<b>Collision–coalescence:</b> the drops merge, so the big drop keeps growing.':
      'The large drop falls <b>faster</b> than the small droplets and sweeps them up in its path.');
  else step(5,'Once heavy enough, it falls out of the cloud base as <b>rain</b>.');}
function draw(){ctx.clearRect(0,0,W,H);
  ctx.fillStyle='#F8FAFC';ctx.fillRect(0,0,W,H);
  ctx.fillStyle='#EEF2F7';ctx.beginPath();ctx.roundRect(6,cloudTop-8,W-12,base-cloudTop+8,14);ctx.fill();
  ctx.strokeStyle='#94A3B8';ctx.setLineDash([5,4]);ctx.beginPath();ctx.moveTo(10,base);ctx.lineTo(W-10,base);ctx.stroke();ctx.setLineDash([]);
  txt('WARM CLOUD · above 0 °C',14,cloudTop+8,'#B45309');txt('cloud base',W-14,base-6,'#64748B','right','500');
  ctx.fillStyle='#E2E8F0';ctx.fillRect(0,ground,W,H-ground);txt('ground',W-14,H-4,'#64748B','right','500');
  for(const d of small)circ(d.x,d.y,d.r,'rgba(191,219,254,'+d.a+')','rgba(147,197,253,'+d.a+')');
  flashes=flashes.filter(f=>f.t<22);for(const f of flashes){f.t++;ctx.beginPath();ctx.arc(f.x,f.y,f.r+f.t*0.6,0,7);
    ctx.strokeStyle='rgba(37,99,235,'+(1-f.t/22)*0.6+')';ctx.lineWidth=1.5;ctx.stroke();}
  let labelled=false;
  for(const a of agents){
    if(a.phase==='rise'||a.phase==='dissolve'){const k=a.phase==='dissolve'?Math.min(a.t/80,1):0;
      if(a.phase==='rise'){ctx.strokeStyle='rgba(234,88,12,.5)';ctx.lineWidth=2;for(const dx of [-30,30]){const yy=Math.min(a.y+30,base+40)-((a.t*1.3)%36);
        if(yy<base+4)continue;ctx.beginPath();ctx.moveTo(a.x+dx,yy+14);ctx.lineTo(a.x+dx,yy);ctx.moveTo(a.x+dx-4,yy+5);ctx.lineTo(a.x+dx,yy);
        ctx.lineTo(a.x+dx+4,yy+5);ctx.stroke();}}
      if(k>0)circ(a.x,a.y,a.r,'rgba(37,99,235,'+(0.25+0.6*k)+')');
      ctx.fillStyle='rgba(255,255,255,'+(1-k)+')';ctx.strokeStyle='rgba(71,85,105,'+(1-k*0.7)+')';ctx.lineWidth=1.2;
      ctx.beginPath();ctx.rect(a.x-5,a.y-5,10,10);ctx.fill();ctx.stroke();
      if(a.phase==='rise'&&!labelled){txt('NaCl',a.x+11,a.y+5,'#475569');labelled=true;}}
    else{if(a.y>base)drop(a.x,a.y,a.r,'#2563EB');else circ(a.x,a.y,a.r,'#1D4ED8');
      if(a.phase==='fall'){ctx.strokeStyle='rgba(29,78,216,.35)';ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(a.x,a.y+a.r+5);
        ctx.lineTo(a.x,a.y+a.r+24);ctx.stroke();}}}
  if(agents.some(a=>a.phase==='rise'))txt('updraft',W-14,base+22,'#C2410C','right','500');
  drawPuffs();if(pl.on)plane(pl.x,base+40);
  drawSplashes();}
"""


_COLD = r"""
let zero,ground,drops,vap,agents,clock,nextPass,pl;
const MAXA=4,GAP=170;
function geom(){zero=Math.round(H*0.66);ground=H-16;}
function newDrop(fade){return {x:rnd(12,W-12),y:rnd(30,zero-14),r:rnd(4.6,7),r0:0,ph:rnd(0,6.28),a:fade?0:1};}
function target(){return Math.round(W/13);}
function freeX(){for(let k=0;k<20;k++){const x=rnd(W*0.1,W*0.9);if(agents.every(a=>Math.abs(a.x-x)>140))return x;}return rnd(W*0.1,W*0.9);}
function reset(){geom();drops=[];for(let i=0;i<target();i++)drops.push(newDrop(false));vap=[];agents=[];splashes=[];clock=0;nextPass=0;pl={on:false,x:-60,drops:[]};puffs=[];}
function snow(x,y,s,a){ctx.save();ctx.translate(x,y);ctx.strokeStyle='rgba(30,58,138,'+a+')';ctx.lineCap='round';
  ctx.lineWidth=Math.max(2,s/7);for(let k=0;k<6;k++){ctx.rotate(Math.PI/3);ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(0,-s);
  ctx.moveTo(0,-s*0.55);ctx.lineTo(-s*0.25,-s*0.8);ctx.moveTo(0,-s*0.55);ctx.lineTo(s*0.25,-s*0.8);ctx.stroke();}ctx.restore();}
function update(){clock++;
  if(!pl.on&&clock>=nextPass&&agents.length<MAXA){const n=Math.min(MAXA-agents.length,3),xs=[];
    for(let k=0;k<40&&xs.length<n;k++){const x=rnd(W*0.1,W*0.9);if(xs.every(v=>Math.abs(v-x)>200)&&agents.every(a=>Math.abs(a.x-x)>140))xs.push(x);}
    pl={on:true,x:-60,drops:xs.sort((a,b)=>a-b)};}
  if(pl.on){pl.x+=2.4;if(pl.drops.length&&pl.x>=pl.drops[0]){pl.drops.shift();const x=pl.x-40;
      agents.push({x,y:44,stop:rnd(H*0.2,H*0.38),phase:'seed',t:0,s:0,v:0});puff(x,44,'71,85,105');}
    if(pl.x>W+70){pl.on=false;nextPass=clock+GAP;}}
  if(drops.length<target()&&clock%10===0)drops.push(newDrop(true));
  for(const d of drops){d.ph+=0.03;d.x+=Math.sin(d.ph)*0.15;d.y+=Math.cos(d.ph*0.7)*0.08;if(d.a<1)d.a=Math.min(1,d.a+0.02);}
  for(const c of agents){c.t++;
    if(c.phase==='seed'){c.y+=0.9;if(c.y>c.stop){c.phase='freeze';c.t=0;}}
    else if(c.phase==='freeze'){if(c.t>80){c.phase='berg';c.t=0;c.s=11;}}
    else if(c.phase==='berg'){for(const d of drops){const dist=Math.hypot(d.x-c.x,d.y-c.y);if(dist<200&&d.r>0.8&&d.a>0.5){
        d.r-=0.026*(1-dist/200);if(Math.random()<0.06*(1-dist/200))vap.push({x:d.x,y:d.y,c});}}
      c.s=Math.min(c.s+0.06,28);if(c.t>320){c.phase='fall';c.t=0;}}
    else{c.v=Math.min(c.v+0.01,0.35+c.s*0.025);c.y+=c.v;c.x+=Math.sin(c.t*0.05)*0.35;
      for(let i=drops.length-1;i>=0;i--){const d=drops[i];if(d.r>0.8&&d.a>0.5&&Math.hypot(d.x-c.x,d.y-c.y)<c.s+d.r){
        drops.splice(i,1);c.s=Math.min(c.s+0.8,34);}}
      c.phase=c.y<zero?'fall':'melt';if(c.y>ground-10){splash(c.x,ground);c.done=1;}}}
  drops=drops.filter(d=>d.r>0.8);agents=agents.filter(c=>!c.done);
  vap=vap.filter(p=>!p.gone);for(const p of vap){const c=p.c;if(c.done||c.phase!=='berg'&&c.phase!=='fall'){p.gone=1;continue;}
    const dx=c.x-p.x,dy=c.y-p.y,d=Math.hypot(dx,dy);if(d<c.s){p.gone=1;continue;}p.x+=dx/d*1.8;p.y+=dy/d*1.8;}
  const L=agents[0];const s1='An aircraft releases <b>AgI</b> into a supercooled cloud (below 0 °C, but the droplets are still liquid).';
  if(!L){if(pl.on)step(1,s1);return;}
  if(L.phase==='seed')step(1,s1);
  else if(L.phase==='freeze')step(2,'Water freezes on the ice-like AgI surface: the first <b>ice crystals</b> form.');
  else if(L.phase==='berg')step(3,'Ice takes vapour from the droplets around it (p*<sub>ice</sub> &lt; p*<sub>liq</sub>): droplets shrink, the crystals grow.');
  else if(L.phase==='fall')step(4,'Heavy enough: the crystals fall as <b>snow</b> and collect supercooled droplets on the way (riming).');
  else step(5,'Below the 0 °C level they <b>melt</b> and reach the ground as <b>rain</b>.');}
function draw(){ctx.clearRect(0,0,W,H);ctx.fillStyle='#FFF7ED';ctx.fillRect(0,0,W,H);
  ctx.fillStyle='#EFF6FF';ctx.fillRect(0,0,W,zero);
  ctx.strokeStyle='#0369A1';ctx.setLineDash([6,5]);ctx.beginPath();ctx.moveTo(10,zero);ctx.lineTo(W-10,zero);ctx.stroke();ctx.setLineDash([]);
  txt('CLOUD BELOW 0 °C',14,zero-8,'#0369A1');txt('0 °C level',W-14,zero-6,'#0369A1','right');txt('AIR ABOVE 0 °C',14,zero+16,'#B45309');
  ctx.fillStyle='#E2E8F0';ctx.fillRect(0,ground,W,H-ground);txt('ground',W-14,H-4,'#64748B','right','500');
  for(const d of drops)circ(d.x,d.y,d.r,'rgba(191,219,254,'+d.a+')','rgba(147,197,253,'+d.a+')');
  for(const p of vap)circ(p.x,p.y,2,'rgba(96,165,250,.9)');
  let labelled=false;
  for(const c of agents){
    if(c.phase==='seed'||c.phase==='freeze'){circ(c.x,c.y,5,'#475569');
      if(c.phase==='seed'){if(!labelled){txt('AgI',c.x+10,c.y+5,'#475569');labelled=true;}}
      else{const a=Math.min(c.t/60,1);ctx.beginPath();ctx.arc(c.x,c.y,8+a*14,0,7);ctx.strokeStyle='rgba(56,189,248,'+(0.6*(1-a)+0.2)+')';
        ctx.lineWidth=2;ctx.stroke();snow(c.x,c.y,11*a,a);}}
    else if(c.phase==='melt'){const m=Math.min((c.y-zero)/40,1);snow(c.x,c.y,c.s*(1-m),1-m);drop(c.x,c.y,6+7*m,'rgba(37,99,235,'+m+')');}
    else{ctx.beginPath();ctx.arc(c.x,c.y,c.s+7,0,7);ctx.fillStyle='rgba(186,230,253,.35)';ctx.fill();snow(c.x,c.y,c.s,1);}}
  drawPuffs();if(pl.on)plane(pl.x,40);
  drawSplashes();}
"""


def _page(body: str, height: int, accent: str) -> str:
    return _SHELL.replace("__BODY__", body).replace("__H__", str(height)).replace("__ACC__", accent)


WARM_CANVAS_H = 400
COLD_CANVAS_H = 420


def warm_rain_html() -> str:
    return _page(_WARM, WARM_CANVAS_H, "#EA580C")


def cold_rain_html() -> str:
    return _page(_COLD, COLD_CANVAS_H, "#1D4ED8")


# total iframe heights: canvas + header bar (58 px) + note (29 px) + borders and a little slack
WARM_FRAME_H = WARM_CANVAS_H + 92
COLD_FRAME_H = COLD_CANVAS_H + 92

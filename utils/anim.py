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
let cloudTop,base,ground,small,big,t,phase,salt,flashes;
function geom(){cloudTop=18;base=Math.round(H*0.62);ground=H-16;}
function mkSmall(){small=[];const n=Math.round(W/11);
  for(let i=0;i<n;i++)small.push({x:rnd(12,W-12),y:rnd(cloudTop+18,base-10),r:rnd(3.6,5.6),ph:rnd(0,6.28)});
  for(let i=0;i<12;i++)small.push({x:W*0.5+rnd(-14,14),y:rnd(cloudTop+70,base-12),r:rnd(3.8,5.4),ph:rnd(0,6.28)});}
function reset(){geom();mkSmall();t=0;phase='rise';flashes=[];splashes=[];
  salt={x:W*0.5,y:base+58,r:4.5};big=null;}
function update(){t++;
  for(const d of small){d.ph+=0.03;d.x+=Math.sin(d.ph)*0.15;d.y+=Math.cos(d.ph*0.7)*0.08;}
  if(phase==='rise'){salt.y-=1.3;step(1,'Salt particles (NaCl, CaCl<sub>2</sub>) are carried up into the cloud by the updraft.');
    if(salt.y<cloudTop+55){phase='dissolve';t=0;}}
  else if(phase==='dissolve'){step(2,'The salt absorbs water and dissolves into a large <b>solution droplet</b> (Raoult &amp; Köhler).');
    salt.r=4.5+Math.min(t/80,1)*7;if(t>110){phase='fall';big={x:salt.x,y:salt.y,r:salt.r,merges:0};t=0;}}
  else if(phase==='fall'||phase==='rain'){
    const v=(0.12+0.0017*big.r*big.r)*(big.y>base?2.2:1);big.y+=v;
    for(let i=small.length-1;i>=0;i--){const d=small[i];if(Math.hypot(d.x-big.x,d.y-big.y)<big.r+d.r){
      big.r=Math.min(Math.cbrt(big.r**3+d.r**3*2),24);small.splice(i,1);big.merges++;flashes.push({x:big.x,y:big.y,r:big.r,t:0});}}
    if(big.y<base){step(big.merges?4:3,big.merges?'<b>Collision–coalescence:</b> the drops merge, so the big drop keeps growing.':
      'The large drop falls <b>faster</b> than the small droplets and sweeps them up in its path.');}
    else{phase='rain';step(5,'Once heavy enough, it falls out of the cloud base as <b>rain</b>.');}
    if(big.y>ground-big.r){splash(big.x,ground);phase='done';t=0;}}
  else if(phase==='done'){if(t>70)reset();}}
function draw(){ctx.clearRect(0,0,W,H);
  ctx.fillStyle='#F8FAFC';ctx.fillRect(0,0,W,H);
  ctx.fillStyle='#EEF2F7';ctx.beginPath();ctx.roundRect(6,cloudTop-8,W-12,base-cloudTop+8,14);ctx.fill();
  ctx.strokeStyle='#94A3B8';ctx.setLineDash([5,4]);ctx.beginPath();ctx.moveTo(10,base);ctx.lineTo(W-10,base);ctx.stroke();ctx.setLineDash([]);
  txt('WARM CLOUD · above 0 °C',14,cloudTop+8,'#B45309');txt('cloud base',W-14,base-6,'#64748B','right','500');
  ctx.fillStyle='#E2E8F0';ctx.fillRect(0,ground,W,H-ground);txt('ground',W-14,H-4,'#64748B','right','500');
  for(const d of small)circ(d.x,d.y,d.r,'#BFDBFE','#93C5FD');
  if(phase==='rise'){ctx.strokeStyle='rgba(234,88,12,.55)';ctx.lineWidth=2;for(const dx of [-34,34]){const yy=base+30-((t*1.3)%40);
    ctx.beginPath();ctx.moveTo(salt.x+dx,yy+14);ctx.lineTo(salt.x+dx,yy);ctx.moveTo(salt.x+dx-4,yy+5);ctx.lineTo(salt.x+dx,yy);
    ctx.lineTo(salt.x+dx+4,yy+5);ctx.stroke();}txt('updraft',salt.x+44,base+44,'#C2410C','left','500');}
  if(phase==='rise'||phase==='dissolve'){const a=phase==='dissolve'?Math.min(t/80,1):0;
    if(a>0)circ(salt.x,salt.y,salt.r,'rgba(37,99,235,'+(0.25+0.6*a)+')');
    ctx.fillStyle='rgba(255,255,255,'+(1-a)+')';ctx.strokeStyle='rgba(71,85,105,'+(1-a*0.7)+')';ctx.lineWidth=1.2;
    ctx.beginPath();ctx.rect(salt.x-5,salt.y-5,10,10);ctx.fill();ctx.stroke();
    if(phase==='rise')txt('NaCl',salt.x+11,salt.y+5,'#475569','left','600');}
  flashes=flashes.filter(f=>f.t<22);for(const f of flashes){f.t++;ctx.beginPath();ctx.arc(f.x,f.y,f.r+f.t*0.6,0,7);
    ctx.strokeStyle='rgba(37,99,235,'+(1-f.t/22)*0.6+')';ctx.lineWidth=1.5;ctx.stroke();}
  if(big&&phase!=='done'){if(big.y>base)drop(big.x,big.y,big.r,'#2563EB');else circ(big.x,big.y,big.r,'#1D4ED8');
    if(phase==='fall'){ctx.strokeStyle='rgba(29,78,216,.35)';ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(big.x,big.y+big.r+5);
      ctx.lineTo(big.x,big.y+big.r+24);ctx.stroke();}}
  drawSplashes();}
"""


_COLD = r"""
let zero,ground,drops,vap,cry,t,phase,agi;
function geom(){zero=Math.round(H*0.66);ground=H-16;}
function reset(){geom();t=0;phase='seed';vap=[];splashes=[];drops=[];const n=Math.round(W/13);
  for(let i=0;i<n;i++)drops.push({x:rnd(12,W-12),y:rnd(30,zero-14),r:rnd(4.6,7),ph:rnd(0,6.28)});
  agi={x:W*0.42,y:-6};cry=null;}
function snow(x,y,s,a){ctx.save();ctx.translate(x,y);ctx.strokeStyle='rgba(30,58,138,'+a+')';ctx.lineCap='round';
  ctx.lineWidth=Math.max(2,s/7);for(let k=0;k<6;k++){ctx.rotate(Math.PI/3);ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(0,-s);
  ctx.moveTo(0,-s*0.55);ctx.lineTo(-s*0.25,-s*0.8);ctx.moveTo(0,-s*0.55);ctx.lineTo(s*0.25,-s*0.8);ctx.stroke();}ctx.restore();}
function update(){t++;
  for(const d of drops){d.ph+=0.03;d.x+=Math.sin(d.ph)*0.15;d.y+=Math.cos(d.ph*0.7)*0.08;}
  if(phase==='seed'){agi.y+=1.1;step(1,'An <b>AgI</b> particle enters a supercooled cloud (below 0 °C, but the droplets are still liquid).');
    if(agi.y>H*0.28){phase='freeze';t=0;}}
  else if(phase==='freeze'){step(2,'Water freezes on the ice-like AgI surface: the first <b>ice crystal</b> forms.');
    if(t>80){phase='berg';t=0;cry={x:agi.x,y:agi.y,s:11,v:0};}}
  else if(phase==='berg'){step(3,'Ice takes vapour from the droplets around it (p*<sub>ice</sub> &lt; p*<sub>liq</sub>): droplets shrink, the crystal grows.');
    for(const d of drops){const dist=Math.hypot(d.x-cry.x,d.y-cry.y);if(dist<200&&d.r>0.8){d.r-=0.026*(1-dist/200);
      if(Math.random()<0.06*(1-dist/200))vap.push({x:d.x,y:d.y});}}
    cry.s=Math.min(cry.s+0.06,28);if(t>320){phase='fall';t=0;}}
  else if(phase==='fall'||phase==='melt'){cry.v=Math.min(cry.v+0.01,0.35+cry.s*0.025);cry.y+=cry.v;cry.x+=Math.sin(t*0.05)*0.35;
    for(let i=drops.length-1;i>=0;i--){const d=drops[i];if(d.r>0.8&&Math.hypot(d.x-cry.x,d.y-cry.y)<cry.s+d.r){
      drops.splice(i,1);cry.s=Math.min(cry.s+0.8,34);}}
    if(cry.y<zero){step(4,'Heavy enough: it falls as <b>snow</b> and collects supercooled droplets on the way (riming).');}
    else{phase='melt';step(5,'Below the 0 °C level it <b>melts</b> and reaches the ground as <b>rain</b>.');}
    if(cry.y>ground-10){splash(cry.x,ground);phase='done';t=0;}}
  else if(phase==='done'){if(t>70)reset();}
  vap=vap.filter(p=>!p.gone);for(const p of vap){if(!cry){p.gone=1;continue;}const dx=cry.x-p.x,dy=cry.y-p.y,d=Math.hypot(dx,dy);
    if(d<cry.s){p.gone=1;continue;}p.x+=dx/d*1.6;p.y+=dy/d*1.6;}}
function draw(){ctx.clearRect(0,0,W,H);ctx.fillStyle='#FFF7ED';ctx.fillRect(0,0,W,H);
  ctx.fillStyle='#EFF6FF';ctx.fillRect(0,0,W,zero);
  ctx.strokeStyle='#0369A1';ctx.setLineDash([6,5]);ctx.beginPath();ctx.moveTo(10,zero);ctx.lineTo(W-10,zero);ctx.stroke();ctx.setLineDash([]);
  txt('CLOUD BELOW 0 °C',14,18,'#0369A1');txt('0 °C level',W-14,zero-6,'#0369A1','right');txt('AIR ABOVE 0 °C',14,zero+16,'#B45309');
  ctx.fillStyle='#E2E8F0';ctx.fillRect(0,ground,W,H-ground);txt('ground',W-14,H-4,'#64748B','right','500');
  for(const d of drops)if(d.r>0.8)circ(d.x,d.y,d.r,'#BFDBFE','#93C5FD');
  for(const p of vap)circ(p.x,p.y,2,'rgba(96,165,250,.9)');
  if(phase==='seed'||phase==='freeze'){circ(agi.x,agi.y,5,'#475569');
    if(phase==='seed')txt('AgI',agi.x+10,agi.y+5,'#475569');
    else{const a=Math.min(t/60,1);ctx.beginPath();ctx.arc(agi.x,agi.y,8+a*14,0,7);ctx.strokeStyle='rgba(56,189,248,'+(0.6*(1-a)+0.2)+')';
      ctx.lineWidth=2;ctx.stroke();snow(agi.x,agi.y,11*a,a);}}
  if(cry&&phase!=='done'){if(phase==='melt'){const m=Math.min((cry.y-zero)/40,1);snow(cry.x,cry.y,cry.s*(1-m),1-m);
      drop(cry.x,cry.y,6+7*m,'rgba(37,99,235,'+m+')');}
    else{ctx.beginPath();ctx.arc(cry.x,cry.y,cry.s+7,0,7);ctx.fillStyle='rgba(186,230,253,.35)';ctx.fill();snow(cry.x,cry.y,cry.s,1);}}
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

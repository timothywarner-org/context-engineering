const c="/api";let g=[],w=[],I=[];const u=document.getElementById("schematics-grid"),h=document.getElementById("loading-state"),l=document.getElementById("empty-state"),B=document.getElementById("search-input"),r=document.getElementById("search-btn"),a=document.getElementById("category-filter"),o=document.getElementById("model-filter"),y=document.getElementById("status-filter"),S=document.getElementById("refresh-btn"),s=document.getElementById("index-all-btn"),d=document.getElementById("search-results-panel"),i=document.getElementById("search-reasoning"),v=document.getElementById("search-results-list"),C=document.getElementById("close-search-btn"),x=document.getElementById("total-count"),E=document.getElementById("active-count"),$=document.getElementById("indexed-count"),b=document.getElementById("categories-count");async function k(){const e=new URLSearchParams;return a?.value&&e.set("category",a.value),o?.value&&e.set("model",o.value),y?.value&&e.set("status",y.value),await(await fetch(`${c}/robots?${e}`)).json()}async function L(){return await(await fetch(`${c}/memory/stats`)).json()}async function j(){return await(await fetch(`${c}/categories`)).json()}async function T(){return await(await fetch(`${c}/models`)).json()}async function A(e){return await(await fetch(`${c}/search`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:e,filters:{},top_k:10})})).json()}async function P(e){return await(await fetch(`${c}/robots/${e}/index`,{method:"POST"})).json()}async function F(){return await(await fetch(`${c}/robots/index-all`,{method:"POST"})).json()}function M(e){if(u){if(e.length===0){u.innerHTML="",l.style.display="block";return}l.style.display="none",u.innerHTML=e.map(t=>`
      <div class="card schematic-card" data-id="${t.id}">
        <div class="card-header">
          <div class="flex gap-md" style="align-items: center;">
            <img src="/assets/robot-${t.status==="active"?"active":t.status==="deprecated"?"offline":"maintenance"}.svg" alt="${t.status}" width="32" height="32" />
            <div>
              <h3 class="card-title" style="font-size: 1rem;">${t.model} - ${t.name}</h3>
              <p class="text-muted" style="margin: 0; font-size: 0.75rem;">${t.id}</p>
            </div>
          </div>
          <span class="badge badge-${t.status==="active"?"active":t.status==="deprecated"?"deprecated":"draft"}">${t.status}</span>
        </div>
        <div style="margin-bottom: var(--space-sm);">
          <strong>${t.component}</strong>
          <span class="text-muted">(${t.version})</span>
        </div>
        <p class="text-muted" style="font-size: 0.875rem; margin-bottom: var(--space-md);">
          ${t.summary.length>100?t.summary.slice(0,100)+"...":t.summary}
        </p>
        <div class="flex flex-between">
          <span class="badge" style="background: var(--bg-secondary); color: var(--text-secondary);">${t.category}</span>
          <button class="btn btn-outline index-btn" style="padding: 4px 12px; font-size: 0.75rem;" data-id="${t.id}">Index</button>
        </div>
      </div>
    `).join(""),document.querySelectorAll(".index-btn").forEach(t=>{t.addEventListener("click",async n=>{n.stopPropagation();const f=t.dataset.id;f&&(t.textContent="...",await P(f),t.textContent="Done",setTimeout(()=>{t.textContent="Index"},1500),await m())})})}}function z(e){x&&(x.textContent=e.total_schematics||"-"),E&&(E.textContent=e.status_counts?.active||"-"),$&&($.textContent=e.indexed_count||"-"),b&&(b.textContent=Object.keys(e.categories||{}).length.toString())}function D(){if(a){const e=a.value;a.innerHTML='<option value="">All Categories</option>'+w.map(t=>`<option value="${t}">${t}</option>`).join(""),a.value=e}if(o){const e=o.value;o.innerHTML='<option value="">All Models</option>'+I.map(t=>`<option value="${t}">${t}</option>`).join(""),o.value=e}}async function p(){h.style.display="flex",l.style.display="none";try{const[e,t,n]=await Promise.all([k(),j(),T()]);g=e.items,w=t,I=n,D(),M(g)}catch(e){console.error("Failed to load data:",e),l.style.display="block"}finally{h.style.display="none"}}async function m(){try{const e=await L();z(e)}catch(e){console.error("Failed to load stats:",e)}}r?.addEventListener("click",async()=>{const e=B?.value?.trim();if(e){r.textContent="Searching...";try{const t=await A(e);d&&i&&v&&(d.style.display="block",t.reasoning?(i.style.display="block",i.textContent=t.reasoning):i.style.display="none",v.innerHTML=t.results.map(n=>`
          <div class="flex flex-between" style="padding: var(--space-md); border-bottom: 1px solid #E0E0E0;">
            <div>
              <strong>${n.schematic.model} - ${n.schematic.name}</strong>
              <span class="text-muted">(${n.schematic.id})</span>
              <p class="text-muted" style="margin: var(--space-xs) 0 0; font-size: 0.875rem;">
                ${n.schematic.component} - ${n.schematic.summary.slice(0,80)}...
              </p>
            </div>
            <div class="text-right">
              <div style="font-weight: 600; color: var(--warnerco-blue);">${(n.score*100).toFixed(0)}%</div>
              <div class="text-muted" style="font-size: 0.75rem;">relevance</div>
            </div>
          </div>
        `).join("")||'<p class="text-muted text-center">No results found.</p>')}catch(t){console.error("Search failed:",t)}finally{r.textContent="Search"}}});B?.addEventListener("keypress",e=>{e.key==="Enter"&&r?.click()});C?.addEventListener("click",()=>{d&&(d.style.display="none")});[a,o,y].forEach(e=>{e?.addEventListener("change",p)});S?.addEventListener("click",()=>{p(),m()});s?.addEventListener("click",async()=>{s&&(s.textContent="Indexing...",s.disabled=!0);try{await F(),await m()}catch(e){console.error("Index all failed:",e)}finally{s&&(s.textContent="Index All",s.disabled=!1)}});p();m();

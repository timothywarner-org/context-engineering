const E="/api";let m=!1,r=null;const p=document.getElementById("backend-name"),v=document.getElementById("total-schematics"),h=document.getElementById("indexed-count"),x=document.getElementById("chunk-count"),u=document.getElementById("category-chart"),f=document.getElementById("status-chart"),b=document.getElementById("coverage-percent"),w=document.getElementById("coverage-bar"),$=document.getElementById("indexed-of-total"),y=document.getElementById("hits-tbody"),I=document.getElementById("hits-count"),C=document.getElementById("refresh-btn"),B=document.getElementById("auto-refresh");async function k(){return await(await fetch(`${E}/memory/stats`)).json()}async function _(){return await(await fetch(`${E}/memory/hits?limit=20`)).json()}function L(e){p&&(p.textContent=e.backend||"-"),v&&(v.textContent=e.total_schematics||"0"),h&&(h.textContent=e.indexed_count||"0"),x&&(x.textContent=e.chunk_count||"0");const t=e.total_schematics||1,d=e.indexed_count||0,i=Math.round(d/t*100);if(b&&(b.textContent=`${i}%`),w&&(w.style.width=`${i}%`),$&&($.textContent=`${d} of ${t}`),u){const l=e.categories||{},o=Object.entries(l).sort((n,s)=>s[1]-n[1]);if(o.length===0)u.innerHTML='<p class="text-muted text-center">No data available</p>';else{const n=Math.max(...o.map(s=>s[1]));u.innerHTML=o.map(([s,a])=>`
          <div style="margin-bottom: var(--space-sm);">
            <div class="flex flex-between" style="margin-bottom: 4px;">
              <span style="font-size: 0.875rem;">${s}</span>
              <span class="text-muted" style="font-size: 0.875rem;">${a}</span>
            </div>
            <div class="progress" style="height: 8px;">
              <div class="progress-bar" style="width: ${a/n*100}%;"></div>
            </div>
          </div>
        `).join("")}}if(f){const l=e.status_counts||{},o={active:"var(--success-green)",deprecated:"var(--neutral-gray)",draft:"var(--warnerco-blue)",maintenance:"var(--warning-orange)"},n=Object.entries(l),s=n.reduce((a,[,c])=>a+c,0)||1;n.length===0?f.innerHTML='<p class="text-muted text-center">No data available</p>':f.innerHTML=`
          <div style="display: flex; gap: var(--space-lg); justify-content: center; flex-wrap: wrap;">
            ${n.map(([a,c])=>`
              <div style="text-align: center;">
                <div style="font-size: 2rem; font-weight: 700; color: ${o[a]||"var(--text-primary)"};">
                  ${c}
                </div>
                <div class="text-muted" style="font-size: 0.75rem; text-transform: uppercase;">
                  ${a}
                </div>
                <div class="text-muted" style="font-size: 0.75rem;">
                  ${Math.round(c/s*100)}%
                </div>
              </div>
            `).join("")}
          </div>
        `}}function M(e){if(I&&(I.textContent=`${e.length} queries`),!!y){if(e.length===0){y.innerHTML=`
        <tr>
          <td colspan="5" class="text-center text-muted">No recent queries</td>
        </tr>
      `;return}y.innerHTML=e.map(t=>`
        <tr>
          <td style="white-space: nowrap; font-size: 0.875rem;">${new Date(t.timestamp).toLocaleTimeString()}</td>
          <td>
            <div style="max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
              ${t.query}
            </div>
          </td>
          <td>
            <span class="badge badge-${t.robot_ids.length>0?"active":"deprecated"}">
              ${t.robot_ids.length} results
            </span>
          </td>
          <td style="font-family: monospace; font-size: 0.875rem;">
            ${t.duration_ms.toFixed(1)}ms
          </td>
          <td>
            <span class="badge" style="background: var(--bg-secondary); color: var(--text-secondary);">
              ${t.backend}
            </span>
          </td>
        </tr>
      `).join("")}}async function g(){try{const[e,t]=await Promise.all([k(),_()]);L(e),M(t)}catch(e){console.error("Failed to load memory data:",e)}}C?.addEventListener("click",g);B?.addEventListener("change",()=>{m=B.checked,m&&!r?r=window.setInterval(g,5e3):!m&&r&&(clearInterval(r),r=null)});g();

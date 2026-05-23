const state = {
  tab: "queue",
  action: "All actions",
  region: "All regions",
};

const data = PRICING_DATA;
const app = document.querySelector("#app");
const focusTitle = document.querySelector("#reviewFocus");
const focusSummary = document.querySelector("#reviewSummary");

const money = (value) => {
  const sign = value < 0 ? "-" : "";
  return `${sign}$${Math.abs(value).toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
};

const pct = (value, signed = false) => {
  const sign = signed && value > 0 ? "+" : "";
  return `${sign}${Number(value).toFixed(1)}%`;
};

const avg = (rows, key) => rows.reduce((sum, row) => sum + Number(row[key]), 0) / Math.max(rows.length, 1);

const byStore = new Map(data.stores.map((store) => [store.store_id, store]));
const topQueue = data.pricingRecommendations.slice(0, 30);

function unique(values) {
  return [...new Set(values)].sort();
}

function setTab(nextTab) {
  state.tab = nextTab;
  document.querySelectorAll(".tab").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.tab === nextTab);
  });
  render();
}

function renderKpis() {
  const totalImpact = topQueue.reduce((sum, row) => sum + Number(row.expected_annual_revenue_delta), 0);
  const actionable = data.pricingRecommendations.filter((row) => row.recommended_action !== "Hold with watchlist").length;
  const avgConfidence = avg(topQueue, "confidence_score");
  const avgOccupancy = avg(data.stores, "current_occupancy_pct");

  document.querySelector("#kpiStrip").innerHTML = [
    ["Top queue impact", money(totalImpact), "modeled annual movement"],
    ["Actionable items", actionable, "store and unit-type reviews"],
    ["Avg confidence", pct(avgConfidence), "top 30 recommendations"],
    ["Network occupancy", pct(avgOccupancy), "synthetic store-market base"],
  ]
    .map(([label, value, note]) => `
      <article class="kpi">
        <span>${label}</span>
        <strong>${value}</strong>
        <em>${note}</em>
      </article>
    `)
    .join("");
}

function pillClass(action) {
  if (action.includes("Raise") || action.includes("Narrow")) return "good";
  if (action.includes("Protect") || action.includes("promo")) return "watch";
  if (action.includes("Fix")) return "block";
  return "neutral";
}

function bar(value, max = 100) {
  const width = Math.max(4, Math.min(100, (Number(value) / max) * 100));
  return `<span class="bar"><i style="width:${width}%"></i></span>`;
}

function controls() {
  const actions = ["All actions", ...unique(data.pricingRecommendations.map((row) => row.recommended_action))];
  const regions = ["All regions", ...unique(data.stores.map((store) => store.region))];
  return `
    <div class="controls">
      <label>
        <span>Action</span>
        <select id="actionFilter">${actions.map((item) => `<option ${item === state.action ? "selected" : ""}>${item}</option>`).join("")}</select>
      </label>
      <label>
        <span>Region</span>
        <select id="regionFilter">${regions.map((item) => `<option ${item === state.region ? "selected" : ""}>${item}</option>`).join("")}</select>
      </label>
    </div>
  `;
}

function filteredRecommendations() {
  return data.pricingRecommendations.filter((row) => {
    const store = byStore.get(row.store_id);
    return (state.action === "All actions" || row.recommended_action === state.action)
      && (state.region === "All regions" || store.region === state.region);
  });
}

function renderQueue() {
  const rows = filteredRecommendations().slice(0, 14);
  const top = rows[0] || data.pricingRecommendations[0];
  focusTitle.textContent = "Pricing queue";
  focusSummary.textContent = `${top.market} ${top.unit_type}: ${top.recommended_action.toLowerCase()} at ${pct(top.rate_change_pct, true)} with ${money(top.expected_annual_revenue_delta)} modeled annual impact.`;

  app.innerHTML = `
    <section class="surface-grid queue-grid">
      <article class="panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">Recommendation queue</p>
            <h2>Ranked pricing actions</h2>
          </div>
          ${controls()}
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Market</th>
                <th>Unit type</th>
                <th>Action</th>
                <th>Rate move</th>
                <th>Impact</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              ${rows.map((row) => `
                <tr>
                  <td><strong>${row.market}</strong><small>${byStore.get(row.store_id).market_type}</small></td>
                  <td>${row.unit_type}</td>
                  <td><span class="pill ${pillClass(row.recommended_action)}">${row.recommended_action}</span></td>
                  <td>${money(row.current_rate)} to ${money(row.recommended_rate)}<small>${pct(row.rate_change_pct, true)}</small></td>
                  <td>${money(row.expected_annual_revenue_delta)}</td>
                  <td>${bar(row.confidence_score)}<small>${pct(row.confidence_score)}</small></td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
      </article>

      <article class="panel decision-card">
        <p class="eyebrow">Top decision packet</p>
        <h2>${top.market}</h2>
        <div class="decision-rate">
          <span>${top.unit_type}</span>
          <strong>${money(top.current_rate)} to ${money(top.recommended_rate)}</strong>
          <em>${top.recommended_action}</em>
        </div>
        <dl class="metrics-list">
          <div><dt>Occupancy</dt><dd>${pct(top.occupancy_pct)}</dd></div>
          <div><dt>Competitor gap</dt><dd>${pct(top.competitor_gap_pct, true)}</dd></div>
          <div><dt>Lead pace</dt><dd>${top.lead_pace_index}</dd></div>
          <div><dt>Elasticity</dt><dd>${top.elasticity}</dd></div>
        </dl>
      </article>
    </section>
  `;

  bindFilters();
}

function renderSignals() {
  focusTitle.textContent = "Market signals";
  focusSummary.textContent = "This view checks whether demand pace, occupancy, promotions, competitor movement, and supply pressure support the price queue.";

  const storeScores = data.stores
    .map((store) => {
      const storeRows = data.pricingRecommendations.filter((row) => row.store_id === store.store_id);
      const storeSignals = data.weeklySignals.filter((row) => row.store_id === store.store_id);
      return {
        ...store,
        queueImpact: storeRows.reduce((sum, row) => sum + Number(row.expected_annual_revenue_delta), 0),
        avgLead: avg(storeSignals, "lead_count"),
        avgPromo: avg(storeSignals, "promo_depth_pct"),
        netRentals: storeSignals.reduce((sum, row) => sum + Number(row.net_rentals), 0),
      };
    })
    .sort((a, b) => b.queueImpact - a.queueImpact)
    .slice(0, 12);

  const regionRows = unique(data.stores.map((store) => store.region)).map((region) => {
    const stores = data.stores.filter((store) => store.region === region);
    const ids = new Set(stores.map((store) => store.store_id));
    const recs = data.pricingRecommendations.filter((row) => ids.has(row.store_id));
    return {
      region,
      occupancy: avg(stores, "current_occupancy_pct"),
      demand: avg(stores, "demand_index"),
      compGap: avg(stores, "competitor_price_gap_pct"),
      supply: avg(stores, "supply_pressure_index"),
      impact: recs.reduce((sum, row) => sum + Number(row.expected_annual_revenue_delta), 0),
    };
  });

  app.innerHTML = `
    <section class="surface-grid">
      <article class="panel">
        <p class="eyebrow">Market watchlist</p>
        <h2>Demand and competitor support</h2>
        <div class="market-list">
          ${storeScores.map((store) => `
            <div class="market-row">
              <div>
                <strong>${store.market}</strong>
                <small>${store.region} / ${store.market_type}</small>
              </div>
              <div><span>Occupancy</span>${bar(store.current_occupancy_pct)}<em>${pct(store.current_occupancy_pct)}</em></div>
              <div><span>Demand</span>${bar(store.demand_index, 140)}<em>${store.demand_index}</em></div>
              <div><span>Comp gap</span>${bar(Math.abs(store.competitor_price_gap_pct), 24)}<em>${pct(store.competitor_price_gap_pct, true)}</em></div>
              <div><span>Queue impact</span><strong>${money(store.queueImpact)}</strong></div>
            </div>
          `).join("")}
        </div>
      </article>
      <article class="panel">
        <p class="eyebrow">Regional readout</p>
        <h2>Pricing posture</h2>
        <div class="region-stack">
          ${regionRows.map((row) => `
            <section>
              <div>
                <strong>${row.region}</strong>
                <span>${money(row.impact)}</span>
              </div>
              <p>Occupancy ${pct(row.occupancy)}, demand ${row.demand.toFixed(1)}, competitor gap ${pct(row.compGap, true)}, supply pressure ${row.supply.toFixed(1)}.</p>
            </section>
          `).join("")}
        </div>
      </article>
    </section>
  `;
}

function renderGuardrails() {
  focusTitle.textContent = "Guardrails";
  focusSummary.textContent = "The model separates ready recommendations from field-review items and source-quality blockers before any rate change is actioned.";

  const blockers = data.qualityChecks.filter((row) => row.result !== "Pass").slice(0, 10);
  const feedback = data.fieldFeedback.slice(0, 8);
  const actionMix = unique(data.pricingRecommendations.map((row) => row.recommended_action)).map((action) => {
    const rows = data.pricingRecommendations.filter((row) => row.recommended_action === action);
    return {
      action,
      count: rows.length,
      confidence: avg(rows, "confidence_score"),
      impact: rows.reduce((sum, row) => sum + Number(row.expected_annual_revenue_delta), 0),
    };
  });

  app.innerHTML = `
    <section class="surface-grid guardrail-grid">
      <article class="panel">
        <p class="eyebrow">Model guardrails</p>
        <h2>Action mix</h2>
        <div class="action-stack">
          ${actionMix.map((row) => `
            <div>
              <span class="pill ${pillClass(row.action)}">${row.action}</span>
              <strong>${row.count} items</strong>
              <small>${pct(row.confidence)} confidence / ${money(row.impact)}</small>
            </div>
          `).join("")}
        </div>
      </article>
      <article class="panel">
        <p class="eyebrow">Source controls</p>
        <h2>Quality checks</h2>
        <div class="quality-list">
          ${blockers.map((row) => `
            <section>
              <div><strong>${row.market}</strong><span class="pill ${row.result === "Blocker" ? "block" : "watch"}">${row.result}</span></div>
              <p>${row.business_impact}</p>
              ${bar(row.score)}
            </section>
          `).join("")}
        </div>
      </article>
      <article class="panel full-row">
        <p class="eyebrow">Field alignment</p>
        <h2>Local context before implementation</h2>
        <div class="feedback-grid">
          ${feedback.map((row) => `
            <section>
              <span>${row.signal}</span>
              <strong>${row.market} / ${row.unit_type}</strong>
              <p>${row.field_note}</p>
              <em>${row.status}</em>
            </section>
          `).join("")}
        </div>
      </article>
    </section>
  `;
}

function bindFilters() {
  const actionFilter = document.querySelector("#actionFilter");
  const regionFilter = document.querySelector("#regionFilter");
  if (actionFilter) {
    actionFilter.addEventListener("change", (event) => {
      state.action = event.target.value;
      renderQueue();
    });
  }
  if (regionFilter) {
    regionFilter.addEventListener("change", (event) => {
      state.region = event.target.value;
      renderQueue();
    });
  }
}

function render() {
  if (state.tab === "signals") renderSignals();
  else if (state.tab === "guardrails") renderGuardrails();
  else renderQueue();
}

document.querySelectorAll(".tab").forEach((button) => {
  button.addEventListener("click", () => setTab(button.dataset.tab));
});

renderKpis();
render();

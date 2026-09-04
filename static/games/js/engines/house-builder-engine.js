/**
 * HouseBuilderEngine — Interactive Game Engine for "Dream House Builder".
 * Provides rich gameplay mechanics:
 *   - Level 1: Land Deed Inspector & Broker Negotiation
 *   - Level 2: Concrete Mixer Chute with Draggable Digit Blocks
 *   - Level 3: Material Place-Value Laser Scanner Machine
 *   - Level 4: Supplier Market Conveyor Belt Ordering & Price Balancer
 *   - Level 5: Master Architect Expense Audit & Official Approval Stamp
 */
class HouseBuilderEngine extends BaseGameEngine {
  constructor(player) {
    super(player);
    this.name = "HouseBuilderEngine";
    this.currentContent = null;
    this.selectedAnswer = null;
    this.placedDigits = [];
    this.orderedItems = [];
    this.scannedPlace = null;
  }

  renderLevel(level, content, container) {
    this.currentContent = content;
    this.selectedAnswer = null;
    this.placedDigits = [];
    this.orderedItems = [];
    this.scannedPlace = null;

    const contentType = content.content_type;
    const data = content.data || {};

    let html = `
      <div class="house-mission-panel">
        <div class="mission-header-bar">
          <div class="mission-step-tag">
            <i class="bi bi-tools"></i> STAGE ${level.level_number}: ${level.title}
          </div>
          <span class="hud-chip score" style="font-size:0.75rem;padding:4px 10px;">+${content.points || 100} PTS</span>
        </div>

        <h2 class="mission-prompt-text">${content.question}</h2>
    `;

    // Render interactive workstation by content type
    if (contentType === 'read_number') {
      html += this.renderLevel1DeedInspector(data);
    } else if (contentType === 'build_number') {
      html += this.renderLevel2ConcreteMixer(data);
    } else if (contentType === 'place_value') {
      html += this.renderLevel3LaserScanner(data);
    } else if (contentType === 'compare_order') {
      html += this.renderLevel4SupplierMarket(data);
    } else if (contentType === 'budget_verification') {
      html += this.renderLevel5ArchitectLedger(data);
    } else {
      html += this.renderGenericWorkstation(data);
    }

    html += `
        <!-- Action Buttons -->
        <div class="workstation-action-bar">
          <button type="button" class="btn-hint" onclick="window.player.requestHint()">
            <i class="bi bi-lightbulb-fill"></i> Hint
          </button>
          <button type="button" class="btn-submit-stage" id="btn-submit-answer" onclick="window.player.submitActiveAnswer()">
            <i class="bi bi-hammer"></i> Confirm &amp; Build Stage
          </button>
        </div>
      </div>
    `;

    container.innerHTML = html;

    // Post-render initialization
    if (contentType === 'build_number') {
      this.initBuildNumberSlots(data);
    } else if (contentType === 'compare_order' && data.type === 'ordering') {
      this.initOrderingItems(data);
    }
  }

  // ── LEVEL 1: LAND DEED INSPECTOR & BROKER NEGOTIATION ─────────────────────
  renderLevel1DeedInspector(data) {
    const formatted = data.formatted_price || "₹2,50,000";
    const property = data.property_name || "Prime Residential Plot";
    const options = data.options || [
      "Two Lakh Fifty Thousand",
      "Twenty-Five Thousand",
      "Two Thousand Five Hundred",
      "Twenty-Five Lakh"
    ];

    let optsHtml = options.map((opt, idx) => `
      <div class="deed-option-tile" onclick="window.player.engine.selectOption('${opt.replace(/'/g, "\\'")}', this)">
        <div class="tile-check-radio"></div>
        <div style="flex:1;">
          <span class="tile-number-word">${opt}</span>
        </div>
        <button type="button" class="btn-tile-audio" onclick="event.stopPropagation(); window.player.engine.speakPrice('${opt.replace(/'/g, "\\'")}')">
          <i class="bi bi-volume-up-fill"></i>
        </button>
      </div>
    `).join('');

    return `
      <!-- Land Deed Document Card -->
      <div class="land-deed-document">
        <div class="deed-header">
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:1.3rem;">📜</span>
            <div>
              <div style="font-size:0.75rem;font-weight:900;color:#FDE047;letter-spacing:1px;">OFFICIAL PROPERTY CONTRACT</div>
              <div style="font-size:0.95rem;font-weight:900;color:#FFFFFF;">${property}</div>
            </div>
          </div>
          <button type="button" class="btn-voice-listen" onclick="window.player.engine.speakPrice('${formatted.replace('₹', '')}')">
            <i class="bi bi-volume-up-fill"></i> Read Price
          </button>
        </div>

        <div class="deed-price-box">
          <span style="font-size:0.75rem;font-weight:800;color:#94A3B8;text-transform:uppercase;">Registration Amount in Digits:</span>
          <div class="deed-big-price">${formatted}</div>
        </div>
      </div>

      <div class="deed-instruction-label">
        <i class="bi bi-pen-fill" style="color:#6366F1;"></i> Verify the official title wording to purchase the land:
      </div>
      <div class="deed-options-container">
        ${optsHtml}
      </div>
    `;
  }

  // ── LEVEL 2: CONCRETE MIXER CHUTE & DRAGGABLE DIGIT BLOCKS ────────────────
  renderLevel2ConcreteMixer(data) {
    const targetWords = data.target_words || "Three Lakh Twenty-Five Thousand";
    const digits = data.digits_pool || [3, 2, 5, 0, 0, 0, 7, 1];

    let digitsHtml = digits.map((d, idx) => `
      <div class="digit-block-draggable" id="digit-btn-${idx}" onclick="window.player.engine.pickDigit(${d}, ${idx})">
        <span class="block-num">${d}</span>
      </div>
    `).join('');

    return `
      <!-- Concrete Mixer Specification -->
      <div class="concrete-mixer-banner">
        <div class="mixer-icon-spin">⚙️</div>
        <div>
          <div style="font-size:0.7rem;font-weight:900;color:#FDE047;letter-spacing:0.8px;">FOUNDATION ENGINEER SPECIFICATION</div>
          <div style="font-size:1.1rem;font-weight:900;color:#FFFFFF;margin-top:2px;">"${targetWords}"</div>
        </div>
      </div>

      <!-- Chute Place-Value Slots -->
      <div class="foundation-chute-rack">
        <div class="chute-top-bar">
          <span>🏗️ PLACE-VALUE CHUTES (INDIAN NUMBER SYSTEM)</span>
          <button type="button" class="btn-clear-slots" onclick="window.player.engine.clearAllSlots()">Clear Chutes</button>
        </div>

        <div class="chutes-grid">
          <div class="chute-slot" id="slot-0" onclick="window.player.engine.clearSlot(0)">
            <span class="chute-lbl">Lakhs (L)</span>
            <div class="chute-digit" id="slot-val-0">_</div>
          </div>
          <div class="chute-comma">,</div>
          <div class="chute-slot" id="slot-1" onclick="window.player.engine.clearSlot(1)">
            <span class="chute-lbl">T-Th</span>
            <div class="chute-digit" id="slot-val-1">_</div>
          </div>
          <div class="chute-slot" id="slot-2" onclick="window.player.engine.clearSlot(2)">
            <span class="chute-lbl">Thousands</span>
            <div class="chute-digit" id="slot-val-2">_</div>
          </div>
          <div class="chute-comma">,</div>
          <div class="chute-slot" id="slot-3" onclick="window.player.engine.clearSlot(3)">
            <span class="chute-lbl">Hundreds</span>
            <div class="chute-digit" id="slot-val-3">_</div>
          </div>
          <div class="chute-slot" id="slot-4" onclick="window.player.engine.clearSlot(4)">
            <span class="chute-lbl">Tens</span>
            <div class="chute-digit" id="slot-val-4">_</div>
          </div>
          <div class="chute-slot" id="slot-5" onclick="window.player.engine.clearSlot(5)">
            <span class="chute-lbl">Ones</span>
            <div class="chute-digit" id="slot-val-5">_</div>
          </div>
        </div>

        <div class="live-chute-readout">
          Constructed Foundation Budget: <strong id="live-built-number">₹ _ , _ _ , _ _ _</strong>
        </div>
      </div>

      <div style="font-size:0.78rem;font-weight:800;color:#94A3B8;text-transform:uppercase;margin-bottom:8px;text-align:center;">
        Tap Available Digit Blocks into the Chutes:
      </div>
      <div class="digit-blocks-depot">
        ${digitsHtml}
      </div>
    `;
  }

  // ── LEVEL 3: PLACE VALUE LASER SCANNER MACHINE ────────────────────────────
  renderLevel3LaserScanner(data) {
    const material = data.material || "Structural Steel";
    const price = data.price || 250000;
    const targetDigit = data.target_digit || 5;
    const options = data.options || [
      "50,000 (Ten-Thousands)",
      "5,000 (Thousands)",
      "500 (Hundreds)",
      "5 Lakhs"
    ];

    const formattedPrice = "₹" + (window.IndianNumberSystem ? window.IndianNumberSystem.format(price) : "2,50,000");

    let optsHtml = options.map((opt, idx) => `
      <div class="scanner-card-opt" onclick="window.player.engine.selectOption('${opt.replace(/'/g, "\\'")}', this)">
        <div class="tile-check-radio"></div>
        <span style="font-weight:900;font-size:0.95rem;">${opt}</span>
      </div>
    `).join('');

    return `
      <!-- Scanner Console -->
      <div class="laser-scanner-console">
        <div class="scanner-header">
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="color:#38BDF8;font-size:1.2rem;">🔬</span>
            <span style="font-weight:900;color:#FFFFFF;font-size:0.95rem;">MATERIAL INVOICE: ${material}</span>
          </div>
          <span style="background:rgba(56, 189, 248, 0.2);color:#38BDF8;padding:3px 10px;border-radius:100px;font-weight:900;font-size:0.85rem;">
            Total: ${formattedPrice}
          </span>
        </div>

        <div style="font-size:0.75rem;font-weight:800;color:#94A3B8;margin-bottom:8px;">
          INDIAN PLACE-VALUE MATRIX SCANNER:
        </div>

        <!-- 6-Period Place Value Visualizer -->
        <div class="pv-matrix-grid">
          <div class="pv-col lakhs">
            <span class="pv-col-lbl">Lakhs</span>
            <div class="pv-col-val">2</div>
          </div>
          <div class="pv-col tth active-laser">
            <span class="pv-col-lbl">T-Th</span>
            <div class="pv-col-val">${targetDigit}</div>
            <div class="laser-beam-indicator">SCANNING</div>
          </div>
          <div class="pv-col th">
            <span class="pv-col-lbl">Th</span>
            <div class="pv-col-val">0</div>
          </div>
          <div class="pv-col h">
            <span class="pv-col-lbl">H</span>
            <div class="pv-col-val">0</div>
          </div>
          <div class="pv-col t">
            <span class="pv-col-lbl">T</span>
            <div class="pv-col-val">0</div>
          </div>
          <div class="pv-col o">
            <span class="pv-col-lbl">O</span>
            <div class="pv-col-val">0</div>
          </div>
        </div>
      </div>

      <div style="font-size:0.85rem;font-weight:800;color:#FDE047;margin:16px 0 10px;display:flex;align-items:center;gap:6px;">
        <i class="bi bi-crosshair"></i> Calibrate the exact PLACE VALUE of highlighted digit <strong>${targetDigit}</strong>:
      </div>
      <div class="scanner-options-grid">
        ${optsHtml}
      </div>
    `;
  }

  // ── LEVEL 4: SUPPLIER MARKETPLACE & CONVEYOR BELT ─────────────────────────
  renderLevel4SupplierMarket(data) {
    if (data.type === 'ordering') {
      return `
        <!-- Conveyor Belt Dock -->
        <div class="conveyor-market-bay">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
            <i class="bi bi-boxes" style="color:#F59E0B;font-size:1.2rem;"></i>
            <span style="font-weight:900;color:#FFFFFF;font-size:0.92rem;">ROOFING MATERIALS CONVEYOR DOCK</span>
          </div>
          <div style="font-size:0.8rem;color:#CBD5E1;margin-bottom:12px;">
            Tap supplier crates below in order from <strong>LOWEST (Cheapest)</strong> to <strong>HIGHEST (Most Expensive)</strong>:
          </div>

          <!-- Destination Conveyor Belt -->
          <div class="conveyor-belt-track" id="ordered-destination-tray">
            <span style="color:#64748B;font-size:0.82rem;font-weight:700;">(Conveyor empty. Tap supplier crates below to load...)</span>
          </div>
        </div>

        <div style="font-size:0.75rem;font-weight:900;color:#94A3B8;text-transform:uppercase;margin:14px 0 8px;">
          Available Supplier Crates:
        </div>
        <div class="supplier-crates-grid" id="ordering-sources-grid">
          <!-- Populated by initOrderingItems -->
        </div>
      `;
    }

    // Comparison Scale (> < =)
    const itemA = data.item_a || { name: "Italian Marble", formatted: "₹3,12,000" };
    const itemB = data.item_b || { name: "Ceramic Tiles", formatted: "₹2,45,000" };

    return `
      <!-- Comparison Marketplace Scale -->
      <div class="market-scale-arena">
        <div class="quote-pan pan-left">
          <div class="quote-pan-tag">SUPPLIER A</div>
          <div class="quote-material-name">${itemA.name}</div>
          <div class="quote-price-tag">${itemA.formatted}</div>
        </div>

        <div class="scale-fulcrum-pivot" id="comparison-selected-slot">
          ?
        </div>

        <div class="quote-pan pan-right">
          <div class="quote-pan-tag">SUPPLIER B</div>
          <div class="quote-material-name">${itemB.name}</div>
          <div class="quote-price-tag">${itemB.formatted}</div>
        </div>
      </div>

      <div style="font-size:0.85rem;font-weight:800;color:#94A3B8;text-transform:uppercase;margin:16px 0 10px;text-align:center;">
        Select the comparison relationship:
      </div>
      <div class="scale-symbol-buttons">
        <button type="button" class="scale-token-btn" onclick="window.player.engine.selectOperator('>', '> (Greater than)', this)">
          <span style="font-size:1.4rem;font-weight:900;">&gt;</span>
          <span>Supplier A is More Expensive</span>
        </button>
        <button type="button" class="scale-token-btn" onclick="window.player.engine.selectOperator('<', '< (Less than)', this)">
          <span style="font-size:1.4rem;font-weight:900;">&lt;</span>
          <span>Supplier A is Cheaper</span>
        </button>
        <button type="button" class="scale-token-btn" onclick="window.player.engine.selectOperator('=', '= (Equal to)', this)">
          <span style="font-size:1.4rem;font-weight:900;">=</span>
          <span>Both Costs are Equal</span>
        </button>
      </div>
    `;
  }

  // ── LEVEL 5: MASTER ARCHITECT EXPENSE AUDIT LEDGER ────────────────────────
  renderLevel5ArchitectLedger(data) {
    const targetWords = data.target_total_words || "Eight Lakh Thirty-Five Thousand";
    const targetNum = data.target_total_number || 835000;
    const expenses = data.expenses || [
      { item: "1. Prime Residential Land", formatted: "₹2,50,000" },
      { item: "2. Foundation & Rebar", formatted: "₹1,25,000" },
      { item: "3. Brick Walls, Doors & Roof", formatted: "₹3,10,000" },
      { item: "4. Interior Finishing & Lights", formatted: "₹1,50,000" }
    ];
    const options = data.options || [
      "Yes, the budget total is EXACTLY ₹8,35,000 ✓",
      "No, the total is ₹7,35,000",
      "No, the total is ₹9,35,000"
    ];

    let expensesHtml = expenses.map(e => `
      <div class="audit-row">
        <span>${e.item}</span>
        <strong>${e.formatted}</strong>
      </div>
    `).join('');

    let optsHtml = options.map((opt, idx) => `
      <div class="audit-decision-tile" onclick="window.player.engine.selectOption('${opt.replace(/'/g, "\\'")}', this)">
        <div class="tile-check-radio"></div>
        <span style="font-weight:900;font-size:0.95rem;">${opt}</span>
      </div>
    `).join('');

    return `
      <!-- Master Architect Audit Sheet -->
      <div class="architect-audit-sheet">
        <div class="audit-header">
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:1.2rem;">🏛️</span>
            <div>
              <div style="font-size:0.72rem;font-weight:900;color:#FDE047;">FINAL CONSTRUCTION LEDGER</div>
              <div style="font-size:0.95rem;font-weight:900;color:#FFFFFF;">Villa Royale Master Budget</div>
            </div>
          </div>
          <span style="background:rgba(251, 191, 36, 0.2);color:#FDE047;border:1px solid #FBBF24;padding:3px 10px;border-radius:100px;font-weight:900;font-size:0.78rem;">
            Claim: "${targetWords}"
          </span>
        </div>

        <div class="audit-breakdown-table">
          ${expensesHtml}
          <div class="audit-total-line">
            <span>EXPANDED SUM TOTAL:</span>
            <strong style="color:#A5B4FC;">2,50,000 + 1,25,000 + 3,10,000 + 1,50,000</strong>
          </div>
        </div>
      </div>

      <div style="font-size:0.85rem;font-weight:800;color:#38BDF8;margin:14px 0 8px;display:flex;align-items:center;gap:6px;">
        <i class="bi bi-shield-check"></i> Audit the calculation and approve the Dream House:
      </div>
      <div class="audit-decisions-grid">
        ${optsHtml}
      </div>
    `;
  }

  // ── ENGINE INTERACTION HELPERS ────────────────────────────────────────────
  selectOption(val, element) {
    if (window.GameAudio) window.GameAudio.playClick();
    document.querySelectorAll('.deed-option-tile, .scanner-card-opt, .audit-decision-tile').forEach(b => b.classList.remove('selected'));
    element.classList.add('selected');
    this.selectedAnswer = { value: val };
  }

  selectOperator(op, label, btn) {
    if (window.GameAudio) window.GameAudio.playClick();
    document.querySelectorAll('.scale-token-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    const slot = document.getElementById('comparison-selected-slot');
    if (slot) slot.textContent = op;
    this.selectedAnswer = { operator: op, value: label };
  }

  // Level 2 Chute Logic
  initBuildNumberSlots(data) {
    this.placedDigits = [null, null, null, null, null, null];
    this.digitRefs = [];
    this.updateBuildSlotsUI();
  }

  pickDigit(digit, btnIdx) {
    if (window.GameAudio) window.GameAudio.playDrop();
    const emptyIdx = this.placedDigits.findIndex(d => d === null);
    if (emptyIdx === -1) {
      alert("All place-value chutes are full! Tap a chute to remove a digit block.");
      return;
    }
    const btn = document.getElementById('digit-btn-' + btnIdx);
    this.placedDigits[emptyIdx] = digit;
    this.digitRefs[emptyIdx] = btn;
    if (btn) btn.classList.add('used');
    this.updateBuildSlotsUI();
  }

  clearSlot(idx) {
    if (window.GameAudio) window.GameAudio.playClick();
    if (this.placedDigits[idx] !== null) {
      if (this.digitRefs[idx]) this.digitRefs[idx].classList.remove('used');
      this.placedDigits[idx] = null;
      this.digitRefs[idx] = null;
      this.updateBuildSlotsUI();
    }
  }

  clearAllSlots() {
    if (window.GameAudio) window.GameAudio.playClick();
    for (let i = 0; i < 6; i++) {
      this.clearSlot(i);
    }
  }

  updateBuildSlotsUI() {
    for (let i = 0; i < 6; i++) {
      const slot = document.getElementById('slot-' + i);
      const val = document.getElementById('slot-val-' + i);
      if (!slot) continue;
      if (this.placedDigits[i] !== null) {
        slot.classList.add('filled');
        val.textContent = this.placedDigits[i];
      } else {
        slot.classList.remove('filled');
        val.textContent = '_';
      }
    }

    const d0 = this.placedDigits[0] !== null ? this.placedDigits[0] : '_';
    const d1 = this.placedDigits[1] !== null ? this.placedDigits[1] : '_';
    const d2 = this.placedDigits[2] !== null ? this.placedDigits[2] : '_';
    const d3 = this.placedDigits[3] !== null ? this.placedDigits[3] : '_';
    const d4 = this.placedDigits[4] !== null ? this.placedDigits[4] : '_';
    const d5 = this.placedDigits[5] !== null ? this.placedDigits[5] : '_';

    const numStr = `${d0}${d1}${d2}${d3}${d4}${d5}`;
    const liveEl = document.getElementById('live-built-number');
    if (liveEl) {
      liveEl.textContent = `₹ ${d0} , ${d1}${d2} , ${d3}${d4}${d5}`;
    }

    this.selectedAnswer = {
      number: numStr.includes('_') ? 0 : parseInt(numStr, 10),
      value: numStr
    };
  }

  // Level 4 Ordering Logic
  initOrderingItems(data) {
    this.orderedItems = [];
    const container = document.getElementById('ordering-sources-grid');
    if (!container) return;

    container.innerHTML = (data.items || []).map(item => `
      <div class="supplier-crate-card" id="order-item-${item.id}" onclick="window.player.engine.addItemToOrder(${JSON.stringify(item).replace(/"/g, '&quot;')})">
        <div style="font-size:1.3rem;">📦</div>
        <div style="flex:1;">
          <div style="font-weight:900;font-size:0.88rem;color:#FFFFFF;">${item.name}</div>
          <div style="font-weight:900;color:#FDE047;font-size:0.95rem;">${item.formatted}</div>
        </div>
        <span style="font-size:0.75rem;background:rgba(255,255,255,0.1);padding:4px 8px;border-radius:6px;color:#94A3B8;">Load ➔</span>
      </div>
    `).join('');
  }

  addItemToOrder(item) {
    if (this.orderedItems.find(i => i.id === item.id)) return;
    if (window.GameAudio) window.GameAudio.playDrop();
    this.orderedItems.push(item);
    const sourceEl = document.getElementById('order-item-' + item.id);
    if (sourceEl) {
      sourceEl.style.opacity = '0.3';
      sourceEl.style.pointerEvents = 'none';
    }

    this.renderOrderedTray();
    this.selectedAnswer = {
      order: this.orderedItems.map(i => i.price)
    };
  }

  renderOrderedTray() {
    const tray = document.getElementById('ordered-destination-tray');
    if (!tray) return;

    if (this.orderedItems.length === 0) {
      tray.innerHTML = '<span style="color:#64748B;font-size:0.82rem;font-weight:700;">(Conveyor empty. Tap supplier crates below to load...)</span>';
      return;
    }

    tray.innerHTML = this.orderedItems.map((item, idx) => `
      <div class="conveyor-loaded-crate">
        <span class="crate-step-badge">${idx + 1}</span>
        <span>${item.name} (<strong>${item.formatted}</strong>)</span>
        <button type="button" onclick="window.player.engine.removeItemFromOrder(${item.id})">✕</button>
      </div>
    `).join(' <i class="bi bi-arrow-right" style="color:#6366F1;font-size:0.9rem;"></i> ');
  }

  removeItemFromOrder(itemId) {
    if (window.GameAudio) window.GameAudio.playClick();
    this.orderedItems = this.orderedItems.filter(i => i.id !== itemId);
    const source = document.getElementById('order-item-' + itemId);
    if (source) {
      source.style.opacity = '1';
      source.style.pointerEvents = 'auto';
    }
    this.renderOrderedTray();
    this.selectedAnswer = {
      order: this.orderedItems.map(i => i.price)
    };
  }

  speakPrice(text) {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text);
      u.rate = 0.9;
      u.pitch = 1.05;
      window.speechSynthesis.speak(u);
    }
  }

  collectAnswer() {
    return this.selectedAnswer || {};
  }
}

window.HouseBuilderEngine = HouseBuilderEngine;

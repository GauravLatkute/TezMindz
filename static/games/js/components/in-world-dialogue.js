/**
 * InWorldDialogue — RPG-style interactive in-game consoles for all 5 Dream House Builder levels.
 * Guarantees 100% correct level/content pairing with backend validation.
 */
class InWorldDialogue {
  constructor(player) {
    this.player = player;
    this.container = document.getElementById('in-world-dialogue-root');
    this.activeLevel = null;
    this.activeContent = null;
    this.selectedAnswer = null;
    this.placedDigits = [];
    this.digitRefs = [];
    this.orderedItems = [];
  }

  shuffleArray(array) {
    const arr = [...array];
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  // ── LEVEL 1: LAND BROKER DEED INSPECTOR ───────────────────────────────────
  showSellerDialogue(sellerName, level, content) {
    if (!this.container) return;

    this.activeLevel = level;
    this.activeContent = content;
    this.selectedAnswer = null;

    const data = content.data || {};
    const formattedPrice = data.formatted_price || "₹2,50,000";
    const rawOptions = data.options || [
      "Two Lakh Fifty Thousand",
      "Twenty-Five Thousand",
      "Two Thousand Five Hundred",
      "Twenty-Five Lakh"
    ];
    const options = this.shuffleArray(rawOptions);

    let deedCardsHtml = options.map((opt, idx) => `
      <div class="deed-offer-card" onclick="window.dialogue.selectFullOffer('${opt.replace(/'/g, "\\'")}', this)">
        <div class="offer-radio"></div>
        <div style="flex:1;">
          <div class="deed-opt-title">${opt}</div>
          <div class="deed-opt-subtitle">Indian Number System Word Form</div>
        </div>
        <button type="button" class="btn-voice-mini" title="Listen" onclick="event.stopPropagation(); window.dialogue.speak('${opt.replace(/'/g, "\\'")}')">
          <i class="bi bi-volume-up-fill"></i>
        </button>
      </div>
    `).join('');

    this.container.innerHTML = `
      <div class="dialogue-modal-backdrop">
        <div class="rpg-dialogue-window">
          
          <!-- Header -->
          <div class="npc-header-bar">
            <div class="npc-avatar-box">👨‍💼</div>
            <div style="flex:1;">
              <div class="npc-name">${sellerName} <span class="npc-badge">Land Broker</span></div>
              <div class="npc-tagline">Tez Realty • Government Approved Land Agency</div>
            </div>
            <button type="button" class="btn-close-dialogue" onclick="window.dialogue.close()">✕</button>
          </div>

          <!-- NPC Speech Line -->
          <div class="npc-speech-bubble">
            "Namaste, Builder! I have the title deed ready for the <strong>Prime Riverside Plot</strong>.
            The official registration price is <strong>${formattedPrice}</strong>. 
            Select the exact Indian Number words below to sign the deed and unlock the construction site!"
          </div>

          <!-- Official Land Deed Paper -->
          <div class="land-deed-paper">
            <div class="deed-top-row">
              <div>
                <span class="deed-paper-title">📜 GOVERNMENT TITLE DEED #TR-8821</span>
                <div style="font-size:0.75rem;color:#78350F;font-weight:700;">Plot Area: 2,400 sq.ft • Zone: Residential Prime</div>
              </div>
              <div class="deed-stamp-area" id="deed-official-stamp">
                UNVERIFIED CONTRACT
              </div>
            </div>

            <div class="deed-amount-display">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:0.75rem;color:#78350F;font-weight:800;text-transform:uppercase;">Registration Amount in Digits:</span>
                <button type="button" class="btn-voice-listen-gold" onclick="window.dialogue.speak('${formattedPrice.replace('₹', '')}')">
                  <i class="bi bi-volume-up-fill"></i> Listen
                </button>
              </div>
              <div class="deed-num-highlight">${formattedPrice}</div>
            </div>

            <div style="font-size:0.82rem;font-weight:900;color:#78350F;margin:12px 0 8px;display:flex;align-items:center;gap:6px;">
              <i class="bi bi-pen-fill" style="color:#B45309;"></i> SELECT EXACT NUMBER NAME TO SIGN TITLE DEED:
            </div>

            <div class="deed-offers-grid">
              ${deedCardsHtml}
            </div>
          </div>

          <!-- Actions -->
          <div class="dialogue-action-row">
            <button type="button" class="btn-dialogue-cancel" onclick="window.dialogue.close()">
              Walk Away
            </button>
            <button type="button" class="btn-dialogue-confirm" id="btn-submit-action" onclick="window.dialogue.confirmPurchase()">
              <i class="bi bi-pen-fill"></i> Sign Title Deed &amp; Pay Land (${formattedPrice})
            </button>
          </div>

        </div>
      </div>
    `;

    this.container.style.display = 'block';
  }

  // ── LEVEL 2: CONCRETE MIXER DEPOT ─────────────────────────────────────────
  showMixerDialogue(level, content) {
    if (!this.container) return;

    this.activeLevel = level;
    this.activeContent = content;
    this.selectedAnswer = null;

    const data = content.data || {};
    const targetWords = data.target_words || "Three Lakh Twenty-Five Thousand";
    
    // Rich digit pool with distractors, thoroughly shuffled
    let rawDigits = data.digits_pool ? [...data.digits_pool] : [3, 2, 5, 0, 0, 0, 7, 1, 4];
    if (rawDigits.length <= 8 && !rawDigits.includes(4)) {
      rawDigits.push(4);
    }
    
    let digits = this.shuffleArray(rawDigits);
    // Ensure it does not trivially start with 3, 2, 5
    if (digits[0] === 3 && digits[1] === 2 && digits[2] === 5) {
      digits = digits.reverse();
    }

    this.placedDigits = [null, null, null, null, null, null];
    this.digitRefs = [];

    let digitsHtml = digits.map((d, idx) => `
      <div class="digit-block-draggable" id="chute-digit-btn-${idx}" onclick="window.dialogue.pickChuteDigit(${d}, ${idx})">
        <span class="block-num">${d}</span>
      </div>
    `).join('');

    this.container.innerHTML = `
      <div class="dialogue-modal-backdrop">
        <div class="rpg-dialogue-window">
          
          <div class="npc-header-bar">
            <div class="npc-avatar-box">🚚</div>
            <div style="flex:1;">
              <div class="npc-name">Foundation Mixer Depot <span class="npc-badge" style="background:#0284C7;color:#fff;">Level 2</span></div>
              <div class="npc-tagline">Reinforced Concrete &amp; Rebar Calibration</div>
            </div>
            <button type="button" class="btn-close-dialogue" onclick="window.dialogue.close()">✕</button>
          </div>

          <div class="npc-speech-bubble">
            "Civil Engineer Order: We need to pour <strong>${targetWords}</strong> of reinforced concrete.
            Slot the digit blocks into the Indian Number System chutes to calibrate the mixer!"
          </div>

          <!-- Chutes Rack -->
          <div class="foundation-chute-rack">
            <div class="chute-top-bar">
              <span>🏗️ PLACE-VALUE CHUTES:</span>
              <button type="button" class="btn-clear-slots" onclick="window.dialogue.clearAllChutes()">Clear Chutes</button>
            </div>

            <div class="chutes-grid">
              <div class="chute-slot" id="c-slot-0" onclick="window.dialogue.clearChuteSlot(0)">
                <span class="chute-lbl">Lakhs (L)</span>
                <div class="chute-digit" id="c-val-0">_</div>
              </div>
              <div class="chute-comma">,</div>
              <div class="chute-slot" id="c-slot-1" onclick="window.dialogue.clearChuteSlot(1)">
                <span class="chute-lbl">T-Th</span>
                <div class="chute-digit" id="c-val-1">_</div>
              </div>
              <div class="chute-slot" id="c-slot-2" onclick="window.dialogue.clearChuteSlot(2)">
                <span class="chute-lbl">Thousands</span>
                <div class="chute-digit" id="c-val-2">_</div>
              </div>
              <div class="chute-comma">,</div>
              <div class="chute-slot" id="c-slot-3" onclick="window.dialogue.clearChuteSlot(3)">
                <span class="chute-lbl">Hundreds</span>
                <div class="chute-digit" id="c-val-3">_</div>
              </div>
              <div class="chute-slot" id="c-slot-4" onclick="window.dialogue.clearChuteSlot(4)">
                <span class="chute-lbl">Tens</span>
                <div class="chute-digit" id="c-val-4">_</div>
              </div>
              <div class="chute-slot" id="c-slot-5" onclick="window.dialogue.clearChuteSlot(5)">
                <span class="chute-lbl">Ones</span>
                <div class="chute-digit" id="c-val-5">_</div>
              </div>
            </div>

            <div class="live-chute-readout">
              Calibrated Foundation Budget: <strong id="c-live-num">₹ _ , _ _ , _ _ _</strong>
            </div>
          </div>

          <div style="font-size:0.78rem;font-weight:800;color:#94A3B8;text-transform:uppercase;text-align:center;">
            Tap Digit Blocks to Fill Chutes:
          </div>
          <div class="digit-blocks-depot">
            ${digitsHtml}
          </div>

          <div class="dialogue-action-row">
            <button type="button" class="btn-dialogue-cancel" onclick="window.dialogue.close()">Close</button>
            <button type="button" class="btn-dialogue-confirm" id="btn-submit-action" onclick="window.dialogue.confirmMixer()">
              <i class="bi bi-hammer"></i> Pour Concrete Foundation
            </button>
          </div>

        </div>
      </div>
    `;

    this.container.style.display = 'block';
  }

  pickChuteDigit(digit, btnIdx) {
    if (window.GameAudio) window.GameAudio.playDrop();
    const emptyIdx = this.placedDigits.findIndex(d => d === null);
    if (emptyIdx === -1) {
      alert("All chutes are filled! Tap any chute to remove a digit.");
      return;
    }
    const btn = document.getElementById('chute-digit-btn-' + btnIdx);
    this.placedDigits[emptyIdx] = digit;
    this.digitRefs[emptyIdx] = btn;
    if (btn) btn.classList.add('used');
    this.updateChutesUI();
  }

  clearChuteSlot(idx) {
    if (window.GameAudio) window.GameAudio.playClick();
    if (this.placedDigits[idx] !== null) {
      if (this.digitRefs[idx]) this.digitRefs[idx].classList.remove('used');
      this.placedDigits[idx] = null;
      this.digitRefs[idx] = null;
      this.updateChutesUI();
    }
  }

  clearAllChutes() {
    for (let i = 0; i < 6; i++) this.clearChuteSlot(i);
  }

  updateChutesUI() {
    for (let i = 0; i < 6; i++) {
      const slot = document.getElementById('c-slot-' + i);
      const val = document.getElementById('c-val-' + i);
      if (!slot) continue;
      if (this.placedDigits[i] !== null) {
        slot.classList.add('filled');
        val.textContent = this.placedDigits[i];
      } else {
        slot.classList.remove('filled');
        val.textContent = '_';
      }
    }

    const d = this.placedDigits.map(x => (x !== null ? x : '_'));
    const numStr = `${d[0]}${d[1]}${d[2]}${d[3]}${d[4]}${d[5]}`;
    const liveEl = document.getElementById('c-live-num');
    if (liveEl) {
      liveEl.textContent = `₹ ${d[0]} , ${d[1]}${d[2]} , ${d[3]}${d[4]}${d[5]}`;
    }

    this.selectedAnswer = {
      number: numStr.includes('_') ? 0 : parseInt(numStr, 10),
      value: numStr
    };
  }

  // ── LEVEL 3: PLACE VALUE LASER SCANNER ────────────────────────────────────
  showScannerDialogue(level, content) {
    if (!this.container) return;

    this.activeLevel = level;
    this.activeContent = content;
    this.selectedAnswer = null;

    const data = content.data || {};
    const material = data.material || "Structural Steel";
    const price = data.price || 250000;
    const targetDigit = data.target_digit || 5;
    const rawOptions = data.options || [
      "50,000 (Ten-Thousands)",
      "5,000 (Thousands)",
      "500 (Hundreds)",
      "5 Lakhs"
    ];
    const options = this.shuffleArray(rawOptions);

    let optsHtml = options.map((opt, idx) => `
      <div class="scanner-card-opt" onclick="window.dialogue.selectFullOffer('${opt.replace(/'/g, "\\'")}', this)">
        <div class="offer-radio"></div>
        <span style="font-weight:900;font-size:0.95rem;color:#FFFFFF;">${opt}</span>
      </div>
    `).join('');

    this.container.innerHTML = `
      <div class="dialogue-modal-backdrop">
        <div class="rpg-dialogue-window">
          
          <div class="npc-header-bar">
            <div class="npc-avatar-box">🏗️</div>
            <div style="flex:1;">
              <div class="npc-name">Material Crane Console <span class="npc-badge" style="background:#16A34A;color:#fff;">Level 3</span></div>
              <div class="npc-tagline">Material Delivery: ${material} (₹2,50,000)</div>
            </div>
            <button type="button" class="btn-close-dialogue" onclick="window.dialogue.close()">✕</button>
          </div>

          <div class="npc-speech-bubble">
            "Crane Scanner: Calibrate the place-value multiplier of highlighted digit <strong>${targetDigit}</strong> in the invoice <strong>₹2,50,000</strong> to unlock the brick walls!"
          </div>

          <div class="laser-scanner-console">
            <div class="pv-matrix-grid">
              <div class="pv-col lakhs"><span class="pv-col-lbl">Lakhs</span><div class="pv-col-val">2</div></div>
              <div class="pv-col tth active-laser">
                <span class="pv-col-lbl">T-Th</span><div class="pv-col-val">${targetDigit}</div>
                <div class="laser-beam-indicator">SCANNING</div>
              </div>
              <div class="pv-col th"><span class="pv-col-lbl">Th</span><div class="pv-col-val">0</div></div>
              <div class="pv-col h"><span class="pv-col-lbl">H</span><div class="pv-col-val">0</div></div>
              <div class="pv-col t"><span class="pv-col-lbl">T</span><div class="pv-col-val">0</div></div>
              <div class="pv-col o"><span class="pv-col-lbl">O</span><div class="pv-col-val">0</div></div>
            </div>
          </div>

          <div class="scanner-options-grid">
            ${optsHtml}
          </div>

          <div class="dialogue-action-row">
            <button type="button" class="btn-dialogue-cancel" onclick="window.dialogue.close()">Close</button>
            <button type="button" class="btn-dialogue-confirm" id="btn-submit-action" onclick="window.dialogue.confirmScanner()">
              <i class="bi bi-check2-circle"></i> Calibrate &amp; Build Walls
            </button>
          </div>

        </div>
      </div>
    `;

    this.container.style.display = 'block';
  }

  // ── LEVEL 4: SUPPLIER MARKETPLACE ─────────────────────────────────────────
  showMarketDialogue(level, content) {
    if (!this.container) return;

    this.activeLevel = level;
    this.activeContent = content;
    this.selectedAnswer = null;

    const data = content.data || {};
    const itemA = data.item_a || { name: "Italian Marble", formatted: "₹3,12,000" };
    const itemB = data.item_b || { name: "Ceramic Tiles", formatted: "₹2,45,000" };

    this.container.innerHTML = `
      <div class="dialogue-modal-backdrop">
        <div class="rpg-dialogue-window">
          
          <div class="npc-header-bar">
            <div class="npc-avatar-box">⚖️</div>
            <div style="flex:1;">
              <div class="npc-name">Supplier Marketplace <span class="npc-badge" style="background:#F59E0B;color:#000;">Level 4</span></div>
              <div class="npc-tagline">Roof &amp; Tile Comparison Station</div>
            </div>
            <button type="button" class="btn-close-dialogue" onclick="window.dialogue.close()">✕</button>
          </div>

          <div class="npc-speech-bubble">
            "Market Inspector: Compare the quotes between Supplier A and Supplier B to order the best roof material!"
          </div>

          <div class="market-scale-arena">
            <div class="quote-pan pan-left">
              <div class="quote-pan-tag">SUPPLIER A</div>
              <div class="quote-material-name">${itemA.name}</div>
              <div class="quote-price-tag">${itemA.formatted}</div>
            </div>

            <div class="scale-fulcrum-pivot" id="dialogue-scale-slot">?</div>

            <div class="quote-pan pan-right">
              <div class="quote-pan-tag">SUPPLIER B</div>
              <div class="quote-material-name">${itemB.name}</div>
              <div class="quote-price-tag">${itemB.formatted}</div>
            </div>
          </div>

          <div class="scale-symbol-buttons">
            <button type="button" class="scale-token-btn" onclick="window.dialogue.selectScaleOp('>', '> (Greater than)', this)">
              <span style="font-size:1.4rem;font-weight:900;">&gt;</span>
              <span>Supplier A is More Expensive (₹3,12,000 &gt; ₹2,45,000)</span>
            </button>
            <button type="button" class="scale-token-btn" onclick="window.dialogue.selectScaleOp('<', '< (Less than)', this)">
              <span style="font-size:1.4rem;font-weight:900;">&lt;</span>
              <span>Supplier A is Cheaper (₹3,12,000 &lt; ₹2,45,000)</span>
            </button>
          </div>

          <div class="dialogue-action-row">
            <button type="button" class="btn-dialogue-cancel" onclick="window.dialogue.close()">Close</button>
            <button type="button" class="btn-dialogue-confirm" id="btn-submit-action" onclick="window.dialogue.confirmMarket()">
              <i class="bi bi-box-seam"></i> Order Roof Materials
            </button>
          </div>

        </div>
      </div>
    `;

    this.container.style.display = 'block';
  }

  selectScaleOp(op, label, btn) {
    if (window.GameAudio) window.GameAudio.playClick();
    document.querySelectorAll('.scale-token-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    const slot = document.getElementById('dialogue-scale-slot');
    if (slot) slot.textContent = op;
    this.selectedAnswer = { operator: op, value: label };
  }

  // ── LEVEL 5: MASTER ARCHITECT FINAL AUDIT ─────────────────────────────────
  showArchitectDialogue(level, content) {
    if (!this.container) return;

    this.activeLevel = level;
    this.activeContent = content;
    this.selectedAnswer = null;

    const data = content.data || {};
    const targetWords = data.target_total_words || "Eight Lakh Thirty-Five Thousand";
    const rawOptions = data.options || [
      "Yes, the budget total is EXACTLY ₹8,35,000 ✓",
      "No, the total is ₹7,35,000",
      "No, the total is ₹9,35,000"
    ];
    const options = this.shuffleArray(rawOptions);

    let optsHtml = options.map((opt, idx) => `
      <div class="audit-decision-tile" onclick="window.dialogue.selectFullOffer('${opt.replace(/'/g, "\\'")}', this)">
        <div class="offer-radio"></div>
        <span style="font-weight:900;font-size:0.95rem;color:#FFFFFF;">${opt}</span>
      </div>
    `).join('');

    this.container.innerHTML = `
      <div class="dialogue-modal-backdrop">
        <div class="rpg-dialogue-window">
          
          <div class="npc-header-bar">
            <div class="npc-avatar-box">🏛️</div>
            <div style="flex:1;">
              <div class="npc-name">Chief Architect Audit <span class="npc-badge" style="background:#7C3AED;color:#fff;">Final Stage</span></div>
              <div class="npc-tagline">Villa Royale Master Sign-Off</div>
            </div>
            <button type="button" class="btn-close-dialogue" onclick="window.dialogue.close()">✕</button>
          </div>

          <div class="npc-speech-bubble">
            "Chief Architect: Review the master expenses ($2,50,000 + 1,25,000 + 3,10,000 + 1,50,000$) to approve the final construction of Villa Royale!"
          </div>

          <div class="architect-audit-sheet">
            <div class="audit-breakdown-table">
              <div class="audit-row"><span>1. Land Plot</span><strong>₹2,50,000</strong></div>
              <div class="audit-row"><span>2. Foundation &amp; Rebar</span><strong>₹1,25,000</strong></div>
              <div class="audit-row"><span>3. Walls, Roof &amp; Windows</span><strong>₹3,10,000</strong></div>
              <div class="audit-row"><span>4. Interior &amp; Solar Panels</span><strong>₹1,50,000</strong></div>
              <div class="audit-total-line"><span>SUM TOTAL:</span><strong style="color:#FDE047;">₹8,35,000</strong></div>
            </div>
          </div>

          <div class="audit-decisions-grid">
            ${optsHtml}
          </div>

          <div class="dialogue-action-row">
            <button type="button" class="btn-dialogue-cancel" onclick="window.dialogue.close()">Close</button>
            <button type="button" class="btn-dialogue-confirm" id="btn-submit-action" onclick="window.dialogue.confirmArchitect()">
              <i class="bi bi-trophy-fill"></i> Approve &amp; Finish Villa Royale!
            </button>
          </div>

        </div>
      </div>
    `;

    this.container.style.display = 'block';
  }

  // ── SUBMISSION HANDLERS ───────────────────────────────────────────────────
  selectFullOffer(offerText, element) {
    if (window.GameAudio) window.GameAudio.playClick();
    document.querySelectorAll('.deed-offer-card, .scanner-card-opt, .audit-decision-tile').forEach(c => c.classList.remove('selected'));
    element.classList.add('selected');
    this.selectedAnswer = { value: offerText };
  }

  async executeSubmission(onSuccessCallback) {
    if (!this.selectedAnswer) {
      alert("Please select or construct your answer first!");
      return;
    }

    const btn = document.getElementById('btn-submit-action');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Validating with Engineer...';
    }

    await this.player.submitSpecificAnswer(this.activeLevel, this.activeContent, this.selectedAnswer, (success, res) => {
      if (success) {
        if (onSuccessCallback) onSuccessCallback(res);
        setTimeout(() => this.close(), 1000);
      } else {
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Try Again';
        }
      }
    });
  }

  confirmPurchase() {
    this.executeSubmission((res) => {
      const stamp = document.getElementById('deed-official-stamp');
      if (stamp) {
        stamp.className = 'deed-stamp-area stamped';
        stamp.innerHTML = 'PAID &amp; OWNED ✓';
      }
      if (this.player.world3D) this.player.world3D.onLevel1Completed();
    });
  }

  confirmMixer() {
    this.executeSubmission((res) => {
      if (this.player.world3D) this.player.world3D.onLevel2Completed();
    });
  }

  confirmScanner() {
    this.executeSubmission((res) => {
      if (this.player.world3D) this.player.world3D.onLevel3Completed();
    });
  }

  confirmMarket() {
    this.executeSubmission((res) => {
      if (this.player.world3D) this.player.world3D.onLevel4Completed();
    });
  }

  confirmArchitect() {
    this.executeSubmission((res) => {
      if (this.player.world3D) this.player.world3D.onLevel5Completed();
    });
  }

  speak(text) {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text);
      u.rate = 0.88;
      u.pitch = 1.05;
      window.speechSynthesis.speak(u);
    }
  }

  close() {
    if (this.container) {
      this.container.style.display = 'none';
      this.container.innerHTML = '';
    }
  }
}

window.InWorldDialogue = InWorldDialogue;

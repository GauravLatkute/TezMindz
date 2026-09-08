/**
 * ConstructionAnimation Component — Renders dynamic SVG Dream House progression.
 * Reliably toggles stages using inline display styles and CSS transitions.
 */
class ConstructionAnimation {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.currentStage = 0;
  }

  setStage(stageNumber, animate = true) {
    this.currentStage = Math.max(0, Math.min(5, stageNumber));
    this.render(animate);
  }

  render(animate = true) {
    if (!this.container) return;

    const s = this.currentStage;
    const animClass = animate ? 'animate-build' : '';

    this.container.innerHTML = `
      <div class="house-canvas-wrapper ${animClass}">
        <svg viewBox="0 0 500 320" class="house-svg" preserveAspectRatio="xMidYMid meet">
          <!-- Sky / Background -->
          <defs>
            <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#E0F2FE" />
              <stop offset="100%" stop-color="#BAE6FD" />
            </linearGradient>
            <linearGradient id="grassGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#86EFAC" />
              <stop offset="100%" stop-color="#22C55E" />
            </linearGradient>
            <linearGradient id="wallGrad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stop-color="#FFFBEB" />
              <stop offset="100%" stop-color="#FEF3C7" />
            </linearGradient>
            <linearGradient id="roofGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#EA580C" />
              <stop offset="100%" stop-color="#C2410C" />
            </linearGradient>
          </defs>

          <!-- Sky & Sun -->
          <rect x="0" y="0" width="500" height="230" fill="url(#skyGrad)" />
          <circle cx="430" cy="50" r="28" fill="#FDE047" opacity="0.9" />

          <!-- Clouds -->
          <path d="M 60,60 Q 75,40 95,50 Q 115,40 130,55 Q 145,65 135,80 L 55,80 Z" fill="#FFFFFF" opacity="0.8" />
          <path d="M 300,75 Q 315,55 335,65 Q 355,55 370,70 Q 385,80 375,95 L 295,95 Z" fill="#FFFFFF" opacity="0.8" />

          <!-- Ground / Green Plot -->
          <rect x="0" y="230" width="500" height="90" fill="url(#grassGrad)" />
          <line x1="0" y1="230" x2="500" y2="230" stroke="#15803D" stroke-width="3" />

          <!-- STAGE 0: Empty Land with Boundary Markers -->
          <g id="stage-0">
            <line x1="30" y1="210" x2="30" y2="260" stroke="#92400E" stroke-width="5" stroke-linecap="round" />
            <line x1="470" y1="210" x2="470" y2="260" stroke="#92400E" stroke-width="5" stroke-linecap="round" />
            <line x1="30" y1="230" x2="470" y2="230" stroke="#F59E0B" stroke-dasharray="8,8" stroke-width="3" />
            
            ${s === 0 ? `
              <!-- Empty Land Info Sign -->
              <rect x="180" y="160" width="140" height="60" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2" />
              <text x="250" y="186" fill="#0F172A" font-size="12" font-weight="bold" text-anchor="middle">PLOT FOR SALE</text>
              <text x="250" y="206" fill="#64748B" font-size="10" font-weight="bold" text-anchor="middle">Awaiting Purchase</text>
              <line x1="250" y1="220" x2="250" y2="265" stroke="#94A3B8" stroke-width="4" />
            ` : ''}
          </g>

          <!-- STAGE 1: Land Purchased Sign & Cleared Site -->
          <g id="stage-1" style="display: ${s >= 1 ? 'inline' : 'none'};">
            <rect x="50" y="180" width="85" height="50" rx="8" fill="#4F46E5" stroke="#3730A3" stroke-width="2" />
            <text x="92" y="202" fill="#FFFFFF" font-size="11" font-weight="900" text-anchor="middle">OWNED</text>
            <text x="92" y="218" fill="#FDE047" font-size="10" font-weight="900" text-anchor="middle">PLOT ✓</text>
            <line x1="92" y1="230" x2="92" y2="270" stroke="#312E81" stroke-width="5" stroke-linecap="round" />
          </g>

          <!-- STAGE 2: Concrete Foundation & Steel Mesh -->
          <g id="stage-2" style="display: ${s >= 2 ? 'inline' : 'none'};">
            <rect x="150" y="218" width="200" height="24" rx="4" fill="#94A3B8" stroke="#475569" stroke-width="2.5" />
            <line x1="155" y1="224" x2="345" y2="224" stroke="#CBD5E1" stroke-dasharray="8,4" stroke-width="2" />
            <line x1="155" y1="234" x2="345" y2="234" stroke="#CBD5E1" stroke-dasharray="8,4" stroke-width="2" />
            <text x="250" y="234" fill="#1E293B" font-size="9" font-weight="900" text-anchor="middle">CONCRETE FOUNDATION</text>
          </g>

          <!-- STAGE 3: Brick Walls, Oak Door, & Windows -->
          <g id="stage-3" style="display: ${s >= 3 ? 'inline' : 'none'};">
            <!-- Main House Wall Body -->
            <rect x="165" y="130" width="170" height="90" rx="4" fill="url(#wallGrad)" stroke="#D97706" stroke-width="2.5" />
            
            <!-- Front Door -->
            <rect x="230" y="165" width="40" height="55" rx="3" fill="#9A3412" stroke="#78350F" stroke-width="2" />
            <circle cx="262" cy="195" r="3" fill="#FACC15" />
            
            <!-- Left Window -->
            <rect x="180" y="148" width="34" height="34" rx="3" fill="#38BDF8" stroke="#0284C7" stroke-width="2" />
            <line x1="197" y1="148" x2="197" y2="182" stroke="#FFFFFF" stroke-width="2" />
            <line x1="180" y1="165" x2="214" y2="165" stroke="#FFFFFF" stroke-width="2" />

            <!-- Right Window -->
            <rect x="286" y="148" width="34" height="34" rx="3" fill="#38BDF8" stroke="#0284C7" stroke-width="2" />
            <line x1="303" y1="148" x2="303" y2="182" stroke="#FFFFFF" stroke-width="2" />
            <line x1="286" y1="165" x2="320" y2="165" stroke="#FFFFFF" stroke-width="2" />
          </g>

          <!-- STAGE 4: Roof, Chimney & Structure -->
          <g id="stage-4" style="display: ${s >= 4 ? 'inline' : 'none'};">
            <!-- Chimney -->
            <rect x="300" y="65" width="22" height="40" fill="#78350F" stroke="#451A03" stroke-width="2" />
            
            <!-- Roof Triangle -->
            <polygon points="148,132 250,55 352,132" fill="url(#roofGrad)" stroke="#9A3412" stroke-width="3" />
            <polygon points="250,55 250,132 352,132" fill="#7C2D12" opacity="0.2" />
          </g>

          <!-- STAGE 5: Complete Dream House Royale (Lights, Smoke, Flowers, Solar Panels, Nameplate) -->
          <g id="stage-5" style="display: ${s >= 5 ? 'inline' : 'none'};">
            <!-- Chimney Smoke Puffs -->
            <circle cx="311" cy="50" r="6" fill="#CBD5E1" opacity="0.8" class="smoke-puff" />
            <circle cx="316" cy="36" r="8" fill="#E2E8F0" opacity="0.7" class="smoke-puff" />
            <circle cx="324" cy="20" r="10" fill="#F1F5F9" opacity="0.6" class="smoke-puff" />

            <!-- Glowing Window Warmth -->
            <rect x="182" y="150" width="30" height="30" fill="#FEF08A" opacity="0.85" />
            <rect x="288" y="150" width="30" height="30" fill="#FEF08A" opacity="0.85" />

            <!-- Solar Panel on Roof -->
            <polygon points="175,115 210,85 240,115" fill="#1E3A8A" stroke="#3B82F6" stroke-width="1.5" />
            <line x1="192" y1="100" x2="225" y2="100" stroke="#60A5FA" stroke-width="1" />

            <!-- Garden Bushes & Flowers -->
            <circle cx="150" cy="225" r="14" fill="#15803D" />
            <circle cx="140" cy="227" r="10" fill="#16A34A" />
            <circle cx="160" cy="227" r="10" fill="#16A34A" />
            <circle cx="145" cy="220" r="3" fill="#EC4899" />
            <circle cx="155" cy="222" r="3" fill="#F43F5E" />

            <circle cx="350" cy="225" r="14" fill="#15803D" />
            <circle cx="340" cy="227" r="10" fill="#16A34A" />
            <circle cx="360" cy="227" r="10" fill="#16A34A" />
            <circle cx="348" cy="220" r="3" fill="#F59E0B" />
            <circle cx="358" cy="222" r="3" fill="#EC4899" />

            <!-- Villa Nameplate -->
            <rect x="220" y="140" width="60" height="16" rx="3" fill="#FDE047" stroke="#CA8A04" stroke-width="1.5" />
            <text x="250" y="152" fill="#713F12" font-size="8" font-weight="900" text-anchor="middle">VILLA ROYALE</text>
          </g>
        </svg>

        <!-- Stage Progress Caption -->
        <div class="construction-status-bar">
          <span class="stage-tag">Stage ${s}/5</span>
          <strong class="stage-title">${this.getStageTitle(s)}</strong>
        </div>
      </div>
    `;
  }

  getStageTitle(stage) {
    switch (stage) {
      case 0: return "Empty Plot — Ready for Construction";
      case 1: return "Plot Purchased & Cleared 🏞️";
      case 2: return "Concrete Foundation Poured 🧱";
      case 3: return "Brick Walls & Windows Installed 🚪🪟";
      case 4: return "Roof & Structure Completed 🏠";
      case 5: return "Dream House Royale Fully Complete! 🎉✨";
      default: return "Construction in Progress";
    }
  }
}

window.ConstructionAnimation = ConstructionAnimation;

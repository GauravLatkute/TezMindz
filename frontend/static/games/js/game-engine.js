/**
 * Base GameEngine Interface for Tezz-Mindz.
 * All domain-specific engines (HouseBuilderEngine, ShoppingEngine, etc.) inherit from this.
 */
class BaseGameEngine {
  constructor(player) {
    this.player = player;
    this.name = "BaseGameEngine";
  }

  /**
   * Called when a level is loaded into the workstation.
   * @param {Object} level - GameLevel safe data
   * @param {Object} content - Active GameContent
   * @param {HTMLElement} container - DOM container element
   */
  renderLevel(level, content, container) {
    throw new Error("renderLevel() must be implemented by subclass");
  }

  /**
   * Collects current student input from the workstation.
   * @returns {Object} Student answer payload
   */
  collectAnswer() {
    throw new Error("collectAnswer() must be implemented by subclass");
  }

  /**
   * Called after server returns validation result.
   * @param {Object} result - Server validation and scoring response
   */
  handleValidationResult(result) {
    // Override in subclass for custom sound/visual effects
  }

  /**
   * Cleans up listeners, intervals, and memory when leaving level.
   */
  destroy() {}
}

window.BaseGameEngine = BaseGameEngine;

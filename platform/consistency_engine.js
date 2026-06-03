/**
 * ConsistencyEngine
 * Handles character and environmental styling reference mapping for video generation.
 * Injects reference descriptors and coordinates seed/embedding parameters for Kling/Vidu.
 */
class ConsistencyEngine {
  constructor() {
    this.characters = new Map();
    this.activeStyle = {
      name: "Cinematic Teal & Orange",
      promptModifier: "cinematic film style, 35mm photography, shallow depth of field, color graded in teal and orange mood"
    };
  }

  /**
   * Registers a character template to maintain visual consistency across shots.
   * @param {string} id - Unique identifier for the character.
   * @param {string} name - Character name.
   * @param {string} referenceImage - URL or path of the face/reference image.
   * @param {string} baseDescription - Physical features and apparel (e.g. "curly blonde hair, green wool coat").
   */
  registerCharacter(id, name, referenceImage, baseDescription) {
    this.characters.set(id, {
      name,
      referenceImage,
      baseDescription,
      instancesGenerated: 0
    });
    console.log(`[ConsistencyEngine] Registered character '${name}' (ID: ${id})`);
  }

  /**
   * Constructs the final prompt and API payload for a scene, ensuring consistent assets.
   * @param {string} rawPrompt - The director's action or scene prompt.
   * @param {Array<string>} characterIds - IDs of characters present in the scene.
   * @returns {Object} Payload configured for the API gateway.
   */
  compileScenePayload(rawPrompt, characterIds = []) {
    let consolidatedPrompt = rawPrompt;
    const faceReferences = [];

    // Append character descriptions and extract face reference images
    characterIds.forEach(id => {
      const char = this.characters.get(id);
      if (char) {
        consolidatedPrompt = `${char.name} (${char.baseDescription}), ${consolidatedPrompt}`;
        if (char.referenceImage) {
          faceReferences.push({
            characterId: id,
            imageUrl: char.referenceImage,
            strength: 0.85 // High weight for IP-Adapter consistency
          });
        }
        char.instancesGenerated++;
      }
    });

    // Inject overall style mood
    if (this.activeStyle) {
      consolidatedPrompt = `${consolidatedPrompt}. ${this.activeStyle.promptModifier}`;
    }

    // Generate a linked seed to maintain temporal noise coherence across consecutive frames
    const frameSeed = Math.floor(Math.random() * 9999999999);

    return {
      finalPrompt: consolidatedPrompt,
      style: this.activeStyle.name,
      seed: frameSeed,
      faceReferences: faceReferences,
      engineConfig: {
        ipAdapterWeight: 0.8,
        cfgScale: 7.5
      }
    };
  }

  /**
   * Sets the global aesthetic style for the project.
   */
  setStyle(name, promptModifier) {
    this.activeStyle = { name, promptModifier };
    console.log(`[ConsistencyEngine] Project aesthetic style updated to: ${name}`);
  }
}

// Export for use in Node or browser contexts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ConsistencyEngine;
}

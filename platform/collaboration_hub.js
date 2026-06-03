/**
 * CollaborationHub
 * Manages co-production reviews, feedback directives, and workflow approvals
 * between young directors and European post-production partners.
 */
class CollaborationHub {
  constructor() {
    this.reviews = [];
    this.collaborators = new Set([
      { id: "collab-1", name: "Tina Jia", role: "Wing Sight CEO", region: "Beijing/Cannes" },
      { id: "collab-2", name: "Jean-Pierre", role: "French Editor", region: "Paris" },
      { id: "collab-3", name: "Alessandra", role: "Italian Sound Designer", region: "Rome" }
    ]);
  }

  /**
   * Adds a review comment on a specific shot from a collaborator.
   * @param {string} collaboratorId - ID of the collaborator.
   * @param {number} shotIndex - Index of the shot in the timeline.
   * @param {string} message - Content of the feedback.
   * @param {Object} suggestedSettings - Optional suggested model or camera adjustments.
   */
  addFeedback(collaboratorId, shotIndex, message, suggestedSettings = null) {
    const collaborator = Array.from(this.collaborators).find(c => c.id === collaboratorId);
    if (!collaborator) {
        throw new Error(`Collaborator with ID ${collaboratorId} not found.`);
    }

    const review = {
      id: `rev-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
      collaborator,
      shotIndex,
      message,
      suggestedSettings,
      status: "pending", // pending, applied, rejected
      timestamp: new Date().toISOString()
    };

    this.reviews.push(review);
    console.log(`[CollaborationHub] New feedback added by ${collaborator.name} on Shot #${shotIndex + 1}`);
    return review;
  }

  /**
   * Approves and applies a specific feedback's parameters to the active project payload.
   * @param {string} reviewId - ID of the review to apply.
   * @returns {Object} The suggested settings to adjust in the composer UI.
   */
  applyDirective(reviewId) {
    const review = this.reviews.find(r => r.id === reviewId);
    if (!review) {
        throw new Error(`Review with ID ${reviewId} not found.`);
    }

    review.status = "applied";
    console.log(`[CollaborationHub] Feedback directive applied: ${review.id}`);
    
    return {
      shotIndex: review.shotIndex,
      message: review.message,
      settings: review.suggestedSettings
    };
  }

  /**
   * Returns all active/pending review comments.
   */
  getPendingReviews() {
    return this.reviews.filter(r => r.status === "pending");
  }
}

// Export for Node or browser contexts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CollaborationHub;
}

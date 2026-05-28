/**
 * state.js — Application state, DOM references, and shared constants.
 */

// ── Shared constants (mirrors engine/config.py values) ─────────────────
export const CARD_MARGIN = 80;
export const STORY_TOP_SAFE = 220;
export const STORY_BOTTOM_SAFE = 250;

// ── Application State ──────────────────────────────────────────────────
export const state = {
  template: "quote",
  ratio: "1:1",
  width: 1080,
  height: 1080,
  bgType: "gradient",
  bgImage: null,
  bgStart: "#1a1c29",
  bgEnd: "#0c0d14",
  bgOverlay: 30,
  useCard: true,
  cardOpacity: 15,
  cardColor: "#ffffff",
  aiType: "image",
  offsetX: 0,
  offsetY: 0,
};

// ── DOM References ─────────────────────────────────────────────────────
export const dom = {};

export function initDom() {
  // Canvas
  dom.canvas = document.getElementById("studio-canvas");
  dom.ctx = dom.canvas.getContext("2d");
  dom.canvasContainer = document.getElementById("canvas-container");

  // Tabs
  dom.tabButtons = document.querySelectorAll(".tab-btn");
  dom.tabContents = document.querySelectorAll(".tab-content");

  // Editor inputs
  dom.titleInput = document.getElementById("post-title");
  dom.bodyInput = document.getElementById("post-body");
  dom.watermarkInput = document.getElementById("post-watermark");
  dom.templateButtons = document.querySelectorAll(".tmpl-btn");
  dom.ratioButtons = document.querySelectorAll(".size-btn");
  dom.useCardCheckbox = document.getElementById("use-card");
  dom.cardOpacityInput = document.getElementById("card-opacity");
  dom.cardColorInput = document.getElementById("card-color");

  // Background
  dom.bgPresets = document.querySelectorAll(".grad-preset");
  dom.bgStartInput = document.getElementById("bg-start");
  dom.bgEndInput = document.getElementById("bg-end");
  dom.bgOverlayInput = document.getElementById("bg-overlay");
  dom.bgUpload = document.getElementById("bg-upload");

  // AI Generator
  dom.aiPrompt = document.getElementById("ai-prompt");
  dom.aiProvider = document.getElementById("ai-provider");
  dom.aiTypeButtons = document.querySelectorAll(".ai-type-btn");
  dom.generateAiBtn = document.getElementById("generate-ai-btn");
  dom.cliCmdDisplay = document.getElementById("cli-cmd-display");
  dom.cliPostDisplay = document.getElementById("cli-post-display");
  dom.aiSubject = document.getElementById("ai-subject");
  dom.aiStyle = document.getElementById("ai-style");
  dom.aiLighting = document.getElementById("ai-lighting");
  dom.aiAngle = document.getElementById("ai-angle");
  dom.aiAction = document.getElementById("ai-action");
  dom.aiAudio = document.getElementById("ai-audio");
  dom.aiActionContainer = document.getElementById("ai-action-container");
  dom.aiAudioContainer = document.getElementById("ai-audio-container");
  dom.aiDescription = document.querySelector("#ai-hub-tab .description-p");

  // Actions & modal
  dom.downloadBtn = document.getElementById("download-png-btn");
  dom.modal = document.getElementById("alert-modal");
  dom.modalTitle = document.getElementById("modal-title");
  dom.modalBody = document.getElementById("modal-body");
  dom.modalClose = document.getElementById("modal-close");
  dom.fixFfmpegBtn = document.getElementById("fix-ffmpeg-btn");
  dom.renderBadge = document.getElementById("render-badge");
}

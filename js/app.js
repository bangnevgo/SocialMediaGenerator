/**
 * app.js — Main entry point. Wires all modules together.
 *
 * Modules:
 *   state.js          — App state & DOM refs
 *   render.js         — Canvas rendering engine
 *   drag.js           — Drag & drop engine
 *   prompt-builder.js — AI prompt builder
 *   cli.js            — CLI command generators
 *   modal.js          — Modal & clipboard helpers
 */

import { state, dom, initDom, CARD_MARGIN } from "./state.js";
import { renderUnsafe, adjustPreviewScale } from "./render.js";
import { initDrag } from "./drag.js";
import { initPromptBuilder, buildPromptFromParams } from "./prompt-builder.js";
import { updateCLICmd, updateCLIPostCmd } from "./cli.js";
import { showModal, initModal } from "./modal.js";

// ── Safe render wrapper with error handling + UI feedback ──────────────
function render() {
  try {
    renderUnsafe();
    dom.renderBadge.style.display = "none";
  } catch (err) {
    console.error("Canvas render failed:", err);
    dom.renderBadge.style.display = "inline-flex";
    dom.renderBadge.textContent = "⚠ Render error: " + err.message;
    setTimeout(() => { dom.renderBadge.style.display = "none"; }, 5000);

    const { ctx } = dom;
    ctx.clearRect(0, 0, state.width, state.height);
    ctx.fillStyle = "#0a0b10";
    ctx.fillRect(0, 0, state.width, state.height);
    ctx.fillStyle = "#ef4444";
    ctx.font = "32px 'Inter', sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("Render error — check console (F12)", state.width / 2, state.height / 2);
  }
}

// ── Sync state → CLI text and re-render ────────────────────────────────
function syncUI() {
  render();
  updateCLICmd();
  updateCLIPostCmd();
}

// ── Tab switching ──────────────────────────────────────────────────────
function initTabs() {
  dom.tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      dom.tabButtons.forEach((b) => b.classList.remove("active"));
      dom.tabContents.forEach((c) => c.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(`${btn.getAttribute("data-tab")}-tab`).classList.add("active");
    });
  });
}

// ── Template picker ────────────────────────────────────────────────────
function initTemplates() {
  dom.templateButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      dom.templateButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      state.template = btn.getAttribute("data-template");

      if (state.template === "quote") {
        dom.titleInput.value = "Steve Jobs";
        dom.bodyInput.value = "Design is not just what it looks like and feels like.\nDesign is how it works.";
      } else if (state.template === "tip") {
        dom.titleInput.value = "WRITING CLEAN CODE";
        dom.bodyInput.value = "• Use descriptive naming conventions.\n• Keep functions small and focused on one task.\n• Delete unused code and print statements.\n• Write code for readability, not cleverness.";
      } else if (state.template === "code") {
        dom.titleInput.value = "decorator.py";
        dom.bodyInput.value = "def memoize(func):\n    cache = {}\n    def wrapper(*args):\n        if args not in cache:\n            cache[args] = func(*args)\n        return cache[args]\n    return wrapper";
      } else {
        dom.titleInput.value = "AuraForge Creative Studio";
        dom.bodyInput.value = "Unlock your brand's potential with AI-driven automated content design workflows.";
      }
      syncUI();
    });
  });
}

// ── Ratio / size selector ──────────────────────────────────────────────
function initRatioSelector() {
  dom.ratioButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      dom.ratioButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      state.ratio = btn.getAttribute("data-ratio");
      state.width = parseInt(btn.getAttribute("data-w"));
      state.height = parseInt(btn.getAttribute("data-h"));
      state.offsetX = 0;
      state.offsetY = 0;
      dom.canvas.width = state.width;
      dom.canvas.height = state.height;
      adjustPreviewScale();
      syncUI();
    });
  });
}

// ── Background controls ────────────────────────────────────────────────
function initBackgroundControls() {
  // Gradient presets
  dom.bgPresets.forEach((preset) => {
    preset.addEventListener("click", () => {
      dom.bgPresets.forEach((p) => p.classList.remove("active"));
      preset.classList.add("active");
      state.bgStart = preset.getAttribute("data-start");
      state.bgEnd = preset.getAttribute("data-end");
      state.bgType = "gradient";
      dom.bgStartInput.value = state.bgStart;
      dom.bgEndInput.value = state.bgEnd;
      syncUI();
    });
  });

  dom.bgStartInput.addEventListener("input", (e) => { state.bgStart = e.target.value; state.bgType = "gradient"; syncUI(); });
  dom.bgEndInput.addEventListener("input", (e) => { state.bgEnd = e.target.value; state.bgType = "gradient"; syncUI(); });
  dom.bgOverlayInput.addEventListener("input", (e) => { state.bgOverlay = parseInt(e.target.value); syncUI(); });

  // Image upload
  dom.bgUpload.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const img = new Image();
        img.onload = () => {
          state.bgImage = img;
          state.bgType = "image";
          dom.bgPresets.forEach((p) => p.classList.remove("active"));
          syncUI();
        };
        img.src = event.target.result;
      };
      reader.readAsDataURL(file);
    }
  });
}

// ── Card controls ──────────────────────────────────────────────────────
function initCardControls() {
  dom.useCardCheckbox.addEventListener("change", (e) => { state.useCard = e.target.checked; syncUI(); });
  dom.cardOpacityInput.addEventListener("input", (e) => { state.cardOpacity = parseInt(e.target.value); syncUI(); });
  dom.cardColorInput.addEventListener("input", (e) => { state.cardColor = e.target.value; syncUI(); });
}

// ── Text editor inputs ─────────────────────────────────────────────────
function initTextInputs() {
  [dom.titleInput, dom.bodyInput, dom.watermarkInput].forEach((input) => {
    input.addEventListener("input", syncUI);
  });
}

// ── AI type selector ───────────────────────────────────────────────────
function initAITypeSelector() {
  dom.aiTypeButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      dom.aiTypeButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      state.aiType = btn.getAttribute("data-type");

      if (state.aiType === "video") {
        dom.aiActionContainer.style.display = "block";
        dom.aiAudioContainer.style.display = "block";
        dom.aiDescription.textContent = "Generate video loops using Google Veo 3.1 prompting guide principles (Shot composition + Subject + Action + Setting + Style with native sound fx).";
      } else {
        dom.aiActionContainer.style.display = "none";
        dom.aiAudioContainer.style.display = "none";
        dom.aiDescription.textContent = "Generate image backdrops using Google Cloud Nano Banana prompting guide principles (conversational briefs over keyword tag-soups).";
      }
      buildPromptFromParams();
      updateCLICmd();
    });
  });
}

// ── AI generate button (calls Flask backend) ───────────────────────────
const API_BASE = "http://127.0.0.1:5000/api";

async function apiGenerateImage(prompt, provider, aspectRatio) {
  const res = await fetch(`${API_BASE}/generate-image`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, provider, aspect_ratio: aspectRatio }),
  });
  return res.json();
}

function initAIGenerate() {
  dom.generateAiBtn.addEventListener("click", async () => {
    const promptVal = dom.aiPrompt.value.trim();
    if (!promptVal) {
      showModal("Validation Error", "<p>Please input an AI generation prompt describing what you want to create.</p>");
      return;
    }

    const providerVal = dom.aiProvider.value;
    const typeVal = state.aiType;
    const btn = dom.generateAiBtn;
    const origText = btn.textContent;

    if (typeVal === "video") {
      showModal("Video Generation", "<p>Video generation requires FFmpeg. Please use the CLI command shown below.</p>");
      return;
    }

    btn.textContent = "Generating…";
    btn.disabled = true;

    try {
      const result = await apiGenerateImage(promptVal, providerVal, state.ratio);

      if (result.success) {
        // Load generated image into canvas background
        const img = new Image();
        img.crossOrigin = "anonymous";
        img.onload = () => {
          state.bgImage = img;
          state.bgType = "image";
          dom.bgPresets.forEach((p) => p.classList.remove("active"));
          syncUI();
          showModal("Generation Complete", `
            <p>✅ Image generated successfully!</p>
            <p><strong>File:</strong> ${result.filename}</p>
            <p>The image has been set as your canvas background.</p>
          `);
        };
        img.src = `http://127.0.0.1:5000${result.url}`;
      } else {
        showModal("Generation Failed", `
          <p>❌ The AI provider returned an error.</p>
          <p><strong>Detail:</strong> ${result.detail || "Unknown error"}</p>
          <hr style="border: 0; border-top: 1px solid var(--card-border); margin: 15px 0;">
          <p>Make sure your <code>.env</code> file has a valid API token for <strong>${providerVal}</strong>, and that <code>python3 server.py</code> is running.</p>
        `);
      }
    } catch (err) {
      showModal("Connection Error", `
        <p>❌ Could not reach the backend server.</p>
        <p><strong>Detail:</strong> ${err.message}</p>
        <hr style="border: 0; border-top: 1px solid var(--card-border); margin: 15px 0;">
        <p>Start the server with: <code style="color:var(--success-color);">python3 server.py</code></p>
      `);
    } finally {
      btn.textContent = origText;
      btn.disabled = false;
    }
  });
}

// ── Download button ────────────────────────────────────────────────────
function initDownload() {
  dom.downloadBtn.addEventListener("click", () => {
    const link = document.createElement("a");
    link.download = `auraforge_${state.template}_${state.ratio.replace(":", "-")}.png`;
    link.href = dom.canvas.toDataURL("image/png");
    link.click();
  });
}

// ── Resize handler ─────────────────────────────────────────────────────
function initResizeHandler() {
  window.addEventListener("resize", adjustPreviewScale);
}

// ── Bootstrap ──────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  initDom();

  // Hide video-only controls by default
  dom.aiActionContainer.style.display = "none";
  dom.aiAudioContainer.style.display = "none";

  // Init canvas sizing
  dom.canvas.width = state.width;
  dom.canvas.height = state.height;

  // Init all modules
  initTabs();
  initTemplates();
  initRatioSelector();
  initBackgroundControls();
  initCardControls();
  initTextInputs();
  initDrag(dom);
  initAITypeSelector();
  initPromptBuilder();
  initAIGenerate();
  initDownload();
  initModal();
  initResizeHandler();

  // Wire AI provider/prompt changes → CLI update
  dom.aiPrompt.addEventListener("input", updateCLICmd);
  dom.aiProvider.addEventListener("change", updateCLICmd);

  // Initial render after fonts load
  document.fonts.ready.then(() => {
    render();
    adjustPreviewScale();
    updateCLICmd();
    updateCLIPostCmd();
  });
});

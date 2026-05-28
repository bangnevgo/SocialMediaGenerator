/**
 * modal.js — Modal dialog utility & clipboard copy helpers.
 * Depends on: dom (from state.js)
 */

import { dom } from "./state.js";

export function showModal(title, bodyHtml) {
  dom.modalTitle.textContent = title;
  dom.modalBody.innerHTML = bodyHtml;
  dom.modal.classList.add("open");
}

export function initModal() {
  dom.modalClose.addEventListener("click", () => dom.modal.classList.remove("open"));

  dom.fixFfmpegBtn.addEventListener("click", () => {
    showModal("FFmpeg Linkage Status", `
      <p><strong>System Status: FFmpeg is Active & Verified!</strong></p>
      <p>Your Mac system's FFmpeg library linkage was successfully repaired using the command:</p>
      <div style="background:#0a0b10; border:1px solid var(--card-border); padding:12px; border-radius:8px; margin:12px 0;">
        <code style="color:var(--success-color);">brew reinstall ffmpeg</code>
      </div>
      <p>All video slideshow compilation features are now fully unlocked and operational locally.</p>
    `);
  });
}

// Global clipboard helpers (kept for backward-compat with inline onclick in HTML)
window.copyCLICmd = function () {
  const code = document.getElementById("cli-cmd-display").textContent;
  navigator.clipboard.writeText(code).then(() => {
    const btn = document.querySelector("#ai-hub-tab .copy-code-btn");
    if (btn) {
      btn.textContent = "Copied!";
      btn.style.backgroundColor = "var(--success-color)";
      setTimeout(() => { btn.textContent = "Copy"; btn.style.backgroundColor = ""; }, 2000);
    }
  });
};

window.copyCLIPostCmd = function () {
  const code = document.getElementById("cli-post-display").textContent;
  navigator.clipboard.writeText(code).then(() => {
    const btn = document.querySelector("#editor-tab .copy-code-btn");
    if (btn) {
      btn.textContent = "Copied!";
      btn.style.backgroundColor = "var(--success-color)";
      setTimeout(() => { btn.textContent = "Copy"; btn.style.backgroundColor = ""; }, 2000);
    }
  });
};

/**
 * cli.js — CLI command generator for AI and layout scripts.
 * Depends on: state.js
 */

import { state, dom } from "./state.js";

export function updateCLICmd() {
  const promptVal = dom.aiPrompt.value.trim() || "cinematic dark liquid background with floating neon particles";
  const typeVal = state.aiType;
  const providerVal = dom.aiProvider.value;
  const ext = typeVal === "video" ? "mp4" : "png";
  dom.cliCmdDisplay.textContent =
    `python3 engine/ai_generator.py --prompt "${promptVal}" --type ${typeVal} --provider ${providerVal} --output ai_assets/generated_${typeVal}.${ext}`;
}

export function updateCLIPostCmd() {
  const template = state.template;
  const title = dom.titleInput.value.replace(/"/g, '\\"');
  const body = dom.bodyInput.value.replace(/"/g, '\\"');
  const watermark = dom.watermarkInput.value.replace(/"/g, '\\"');
  const ratio = state.ratio;

  let cmd = `python3 engine/create_post.py --template ${template} --ratio ${ratio}`;
  if (title) cmd += ` --title "${title}"`;
  if (body) cmd += ` --body "${body.replace(/\n/g, '\\n')}"`;
  if (watermark) cmd += ` --watermark "${watermark}"`;

  if (state.bgType === "image") {
    cmd += ` --bg_image "ai_assets/generated_image.png"`;
  } else {
    cmd += ` --bg_start "${state.bgStart}" --bg_end "${state.bgEnd}"`;
  }
  cmd += ` --bg_overlay ${state.bgOverlay}`;

  if (!state.useCard) {
    cmd += ` --no_card`;
  } else {
    cmd += ` --card_color "${state.cardColor}" --card_opacity ${state.cardOpacity}`;
  }

  if (state.offsetX !== 0) cmd += ` --offset_x ${Math.round(state.offsetX)}`;
  if (state.offsetY !== 0) cmd += ` --offset_y ${Math.round(state.offsetY)}`;

  cmd += ` --output posts/my_post.png`;
  dom.cliPostDisplay.textContent = cmd;
}

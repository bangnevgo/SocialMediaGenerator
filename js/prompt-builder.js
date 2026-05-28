/**
 * prompt-builder.js — AI prompt builder (Nano Banana & Veo 3.1 formulas).
 * Depends on: state.js
 */

import { state, dom } from "./state.js";

export function buildPromptFromParams() {
  const subject = dom.aiSubject.value.trim();
  if (!subject) {
    dom.aiPrompt.value = "";
    return;
  }

  let prompt = "";

  if (state.aiType === "video") {
    // Google Veo 3.1 structured prompt (Core 5 formula)
    const composition = dom.aiAngle.value
      ? `A ${dom.aiAngle.value.replace("shot", "").trim()}`
      : "A cinematic vertical video shot";
    prompt = `${composition} of ${subject}.`;

    const action = dom.aiAction.value.trim();
    if (action) prompt += ` The subject is ${action}.`;

    const style = dom.aiStyle.value;
    const lighting = dom.aiLighting.value;
    const parts = [];
    if (style) parts.push(`designed in ${style}`);
    if (lighting) parts.push(`illuminated by ${lighting}`);
    if (parts.length > 0) prompt += ` The setting is a detailed environment, ${parts.join(" and ")}.`;

    const audio = dom.aiAudio.value.trim();
    if (audio) {
      prompt += audio.toUpperCase().startsWith("SFX:") ? ` ${audio}` : ` SFX: ${audio}`;
    }

    if (dom.aiAngle.value) {
      if (dom.aiAngle.value.includes("panning")) prompt += " The camera pans slowly.";
      else if (dom.aiAngle.value.includes("zoom-in")) prompt += " The camera pulls in slowly.";
      else if (dom.aiAngle.value.includes("zoom-out")) prompt += " The camera pulls back slowly.";
      else if (dom.aiAngle.value.includes("orbit")) prompt += " The camera orbits in a full rotation.";
    }
  } else {
    // Google Nano Banana (conversational style)
    prompt = `A premium high-resolution background graphic depicting ${subject}.`;

    const style = dom.aiStyle.value;
    if (style) prompt += ` The visual style is ${style}.`;

    const angle = dom.aiAngle.value;
    if (angle) prompt += ` The camera perspective features a ${angle}.`;

    const lighting = dom.aiLighting.value;
    if (lighting) prompt += ` The scene is illuminated by ${lighting}.`;

    const watermarkText = dom.watermarkInput.value.trim();
    if (watermarkText) {
      prompt += ` The image composition leaves an uncluttered centered card area suitable for text overlay of "${watermarkText}" in post-processing.`;
    }
  }

  dom.aiPrompt.value = prompt;
}

export function initPromptBuilder() {
  dom.aiSubject.addEventListener("input", buildPromptFromParams);
  dom.aiStyle.addEventListener("change", buildPromptFromParams);
  dom.aiLighting.addEventListener("change", buildPromptFromParams);
  dom.aiAngle.addEventListener("change", buildPromptFromParams);
  dom.aiAction.addEventListener("input", buildPromptFromParams);
  dom.aiAudio.addEventListener("input", buildPromptFromParams);
}

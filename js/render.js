/**
 * render.js — Canvas rendering engine, text helpers, and background drawing.
 * Depends on: state.js
 */

import { state, dom, CARD_MARGIN, STORY_TOP_SAFE, STORY_BOTTOM_SAFE } from "./state.js";

// ── Hex → RGBA helper ──────────────────────────────────────────────────
export function hexToRgba(hex, alpha) {
  hex = hex.replace("#", "");
  if (hex.length === 3) hex = hex.split("").map((c) => c + c).join("");
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

// ── Text wrapping (mirrors Python engine logic) ────────────────────────
function wrapText(context, text, x, y, maxWidth, lineHeight, align = "center") {
  const paragraphs = text.split("\n");
  let currentY = y;

  paragraphs.forEach((para) => {
    const words = para.split(" ");
    let line = "";

    for (let n = 0; n < words.length; n++) {
      const testLine = line + words[n] + " ";
      const metrics = context.measureText(testLine);
      if (metrics.width > maxWidth && n > 0) {
        drawTextLine(context, line, x, currentY, align);
        line = words[n] + " ";
        currentY += lineHeight;
      } else {
        line = testLine;
      }
    }
    drawTextLine(context, line, x, currentY, align);
    currentY += lineHeight;
  });

  return currentY;
}

function drawTextLine(context, line, x, y, align) {
  if (align === "center") context.textAlign = "center";
  else if (align === "right") context.textAlign = "right";
  else context.textAlign = "left";
  context.fillText(line.trim(), x, y);
}

// ── Preview scaling ────────────────────────────────────────────────────
export function adjustPreviewScale() {
  const parentW = dom.canvasContainer.clientWidth;
  const parentH = dom.canvasContainer.clientHeight;
  const scale = Math.min((parentW - 20) / state.width, (parentH - 20) / state.height, 1);
  dom.canvas.style.width = `${state.width * scale}px`;
  dom.canvas.style.height = `${state.height * scale}px`;
}

// ── Main render (called through wrapper in app.js) ─────────────────────
export function renderUnsafe() {
  const { ctx, canvas } = dom;
  ctx.clearRect(0, 0, state.width, state.height);

  // A. Background
  if (state.bgType === "image" && state.bgImage) {
    const canvasRatio = state.width / state.height;
    const imgRatio = state.bgImage.width / state.bgImage.height;
    let drawW, drawH, drawX, drawY;
    if (imgRatio > canvasRatio) {
      drawH = state.height;
      drawW = state.height * imgRatio;
      drawX = (state.width - drawW) / 2;
      drawY = 0;
    } else {
      drawW = state.width;
      drawH = state.width / imgRatio;
      drawX = 0;
      drawY = (state.height - drawH) / 2;
    }
    ctx.drawImage(state.bgImage, drawX, drawY, drawW, drawH);
  } else {
    const gradient = ctx.createLinearGradient(0, 0, 0, state.height);
    gradient.addColorStop(0, state.bgStart);
    gradient.addColorStop(1, state.bgEnd);
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, state.width, state.height);
  }

  // Overlay for readability
  if (state.bgOverlay > 0) {
    ctx.fillStyle = `rgba(0, 0, 0, ${state.bgOverlay / 100})`;
    ctx.fillRect(0, 0, state.width, state.height);
  }

  // B. Card geometry
  const margin = CARD_MARGIN;
  const cardW = state.width - margin * 2;
  let cardYStart = (state.ratio === "9:16" ? STORY_TOP_SAFE : margin) + state.offsetY;
  let cardYEnd = (state.ratio === "9:16" ? state.height - STORY_BOTTOM_SAFE : state.height - margin) + state.offsetY;
  const cardH = cardYEnd - cardYStart;
  const cardX = margin + state.offsetX;

  // C. Glassmorphism card
  if (state.useCard) {
    ctx.save();
    ctx.beginPath();
    ctx.roundRect(cardX, cardYStart, cardW, cardH, 24);
    ctx.clip();

    if (state.bgType === "image" && state.bgImage) {
      ctx.filter = "blur(20px)";
      ctx.drawImage(canvas, 0, 0);
      ctx.filter = "none";
    } else {
      ctx.filter = "blur(15px)";
      const gradient = ctx.createLinearGradient(0, 0, 0, state.height);
      gradient.addColorStop(0, state.bgStart);
      gradient.addColorStop(1, state.bgEnd);
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, state.width, state.height);
      ctx.filter = "none";
    }
    ctx.restore();

    ctx.fillStyle = hexToRgba(state.cardColor, state.cardOpacity / 100);
    ctx.beginPath();
    ctx.roundRect(cardX, cardYStart, cardW, cardH, 24);
    ctx.fill();

    ctx.strokeStyle = "rgba(255,255,255,0.15)";
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.shadowColor = "rgba(0,0,0,0.4)";
    ctx.shadowBlur = 40;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 15;
    ctx.strokeStyle = "rgba(255,255,255,0.01)";
    ctx.stroke();
    ctx.shadowColor = "transparent";
    ctx.shadowBlur = 0;
  }

  // D. Watermark
  const handleText = dom.watermarkInput.value.trim();
  if (handleText) {
    ctx.font = "300 24px 'Inter', sans-serif";
    ctx.fillStyle = "rgba(255,255,255,0.6)";
    ctx.textAlign = "center";
    const waterY = state.useCard ? cardYEnd - 60 : state.height - 70 + state.offsetY;
    ctx.fillText(handleText, state.width / 2 + state.offsetX, waterY);
  }

  // E. Template text layouts
  const textWidth = cardW - 120;
  const cx = state.width / 2 + state.offsetX;
  const titleVal = dom.titleInput.value.trim();
  const bodyVal = dom.bodyInput.value.trim();

  if (state.template === "quote") {
    ctx.font = "italic 160px 'Playfair Display', serif";
    ctx.fillStyle = "rgba(255,255,255,0.15)";
    ctx.textAlign = "center";
    ctx.fillText("“", cx, cardYStart + 160);

    ctx.font = "italic 40px 'Playfair Display', Georgia, serif";
    ctx.fillStyle = "#ffffff";
    const wrapH = 52;
    const endY = wrapText(ctx, bodyVal, cx, cardYStart + 220, textWidth, wrapH, "center");

    if (titleVal) {
      ctx.font = "500 32px 'Outfit', 'Inter', sans-serif";
      ctx.fillStyle = "#e0e0e0";
      ctx.fillText(`— ${titleVal}`, cx, endY + 30);
    }
  } else if (state.template === "tip") {
    ctx.font = "800 48px 'Montserrat', sans-serif";
    ctx.fillStyle = "#64ffda";
    const endY = wrapText(ctx, titleVal.toUpperCase(), cx, cardYStart + 80, textWidth, 58, "center");

    ctx.strokeStyle = "rgba(100,255,218,0.3)";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(cx - 100, endY + 15);
    ctx.lineTo(cx + 100, endY + 15);
    ctx.stroke();

    ctx.font = "400 32px 'Inter', sans-serif";
    ctx.fillStyle = "#ffffff";
    const align = bodyVal.includes("\n") || bodyVal.includes("•") ? "left" : "center";
    wrapText(ctx, bodyVal, cx, endY + 80, textWidth, 48, align);
  } else if (state.template === "code") {
    const btnY = cardYStart + 40;
    ctx.fillStyle = "#FF5F56";
    ctx.beginPath(); ctx.arc(cardX + 50, btnY + 10, 9, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#FFBD2E";
    ctx.beginPath(); ctx.arc(cardX + 80, btnY + 10, 9, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#27C93F";
    ctx.beginPath(); ctx.arc(cardX + 110, btnY + 10, 9, 0, Math.PI * 2); ctx.fill();

    ctx.font = "600 24px 'Inter', sans-serif";
    ctx.fillStyle = "#888888";
    ctx.textAlign = "center";
    ctx.fillText(titleVal || "main.py", cx, btnY + 18);

    ctx.strokeStyle = "rgba(255,255,255,0.08)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(cardX + 20, btnY + 45);
    ctx.lineTo(cardX + cardW - 20, btnY + 45);
    ctx.stroke();

    ctx.font = "400 28px 'Courier New', monospace";
    ctx.fillStyle = "#d4d4d4";
    wrapText(ctx, bodyVal, cx, btnY + 90, textWidth, 38, "left");
  } else {
    ctx.font = "800 44px 'Outfit', 'Montserrat', sans-serif";
    ctx.fillStyle = "#ffffff";
    const endY = wrapText(ctx, titleVal, cx, cardYStart + 100, textWidth, 54, "center");

    ctx.font = "400 30px 'Inter', sans-serif";
    ctx.fillStyle = "rgba(255,255,255,0.85)";
    wrapText(ctx, bodyVal, cx, endY + 40, textWidth, 44, "center");
  }
}

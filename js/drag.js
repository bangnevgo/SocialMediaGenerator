/**
 * drag.js — Drag & drop re-composition engine for the glass card.
 * Depends on: state.js, render.js, cli.js
 */

import { state, dom, CARD_MARGIN, STORY_TOP_SAFE, STORY_BOTTOM_SAFE } from "./state.js";
import { render as safeRender } from "./render.js";
import { updateCLIPostCmd } from "./cli.js";

let isDragging = false;
let dragStartX = 0;
let dragStartY = 0;
let initialOffsetX = 0;
let initialOffsetY = 0;

function canvasCoords(e) {
  const rect = dom.canvas.getBoundingClientRect();
  const clientX = (e.touches && e.touches.length > 0) ? e.touches[0].clientX : e.clientX;
  const clientY = (e.touches && e.touches.length > 0) ? e.touches[0].clientY : e.clientY;
  const scaleX = dom.canvas.width / rect.width;
  const scaleY = dom.canvas.height / rect.height;
  return {
    x: (clientX - rect.left) * scaleX,
    y: (clientY - rect.top) * scaleY,
  };
}

function isOverCard(x, y) {
  const margin = CARD_MARGIN;
  let cardYStart = (state.ratio === "9:16" ? STORY_TOP_SAFE : margin) + state.offsetY;
  let cardYEnd = (state.ratio === "9:16" ? state.height - STORY_BOTTOM_SAFE : state.height - margin) + state.offsetY;
  const cardXStart = margin + state.offsetX;
  const cardXEnd = state.width - margin + state.offsetX;
  return x >= cardXStart && x <= cardXEnd && y >= cardYStart && y <= cardYEnd;
}

export function clampOffset() {
  const maxOffsetX = state.width * 0.2;
  const maxOffsetY = state.height * 0.2;
  state.offsetX = Math.max(-maxOffsetX, Math.min(maxOffsetX, state.offsetX));
  state.offsetY = Math.max(-maxOffsetY, Math.min(maxOffsetY, state.offsetY));
}

function onDragStart(e) {
  const coords = canvasCoords(e);
  if (isOverCard(coords.x, coords.y)) {
    isDragging = true;
    if (e.cancelable) e.preventDefault();
    dragStartX = coords.x;
    dragStartY = coords.y;
    initialOffsetX = state.offsetX;
    initialOffsetY = state.offsetY;
    dom.canvas.style.cursor = "grabbing";
  }
}

function onDragMove(e) {
  const coords = canvasCoords(e);
  if (isDragging) {
    if (e.cancelable) e.preventDefault();
    state.offsetX = initialOffsetX + (coords.x - dragStartX);
    state.offsetY = initialOffsetY + (coords.y - dragStartY);
    clampOffset();
    safeRender();
    updateCLIPostCmd();
  } else {
    dom.canvas.style.cursor = isOverCard(coords.x, coords.y) ? "grab" : "default";
  }
}

function onDragEnd() {
  if (isDragging) {
    isDragging = false;
    dom.canvas.style.cursor = "grab";
  }
}

export function initDrag(domRefs) {
  const canvas = domRefs.canvas || dom.canvas;
  canvas.addEventListener("mousedown", onDragStart);
  canvas.addEventListener("touchstart", onDragStart, { passive: false });
  canvas.addEventListener("mousemove", onDragMove);
  canvas.addEventListener("touchmove", onDragMove, { passive: false });
  window.addEventListener("mouseup", onDragEnd);
  window.addEventListener("touchend", onDragEnd);
}

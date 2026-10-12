/** Standard-mapping Xbox Gamepad API navigation for the native web game. */
const DEADZONE = 0.18;
export const GAME_WIDTH = 640;
export const GAME_HEIGHT = 480;
export function newControllerState() {
  return { x: 320, y: 240, aHeld: false, bHeld: false, active: false };
}
const pressed = (gamepad, index) => Boolean(gamepad.buttons?.[index]?.pressed);
export function controllerStep(gamepad, state, seconds, handlers = {}) {
  if (!gamepad || gamepad.mapping !== "standard") {
    state.active = false;
    state.aHeld = false;
    state.bHeld = false;
    return state;
  }
  state.active = true;
  const horizontal = Number.isFinite(gamepad.axes?.[0]) ? gamepad.axes[0] : 0;
  const vertical = Number.isFinite(gamepad.axes?.[1]) ? gamepad.axes[1] : 0;
  const directionX = (pressed(gamepad, 15) ? 1 : 0) - (pressed(gamepad, 14) ? 1 : 0);
  const directionY = (pressed(gamepad, 13) ? 1 : 0) - (pressed(gamepad, 12) ? 1 : 0);
  const dx = directionX || (Math.abs(horizontal) > DEADZONE ? horizontal : 0);
  const dy = directionY || (Math.abs(vertical) > DEADZONE ? vertical : 0);
  const dt = Math.max(0, Math.min(0.1, Number(seconds) || 0));
  state.x = Math.max(0, Math.min(GAME_WIDTH - 1, state.x + dx * dt * 320));
  state.y = Math.max(0, Math.min(GAME_HEIGHT - 1, state.y + dy * dt * 320));
  const a = pressed(gamepad, 0);
  const b = pressed(gamepad, 1);
  if (a && !state.aHeld) handlers.activate?.(Math.round(state.x), Math.round(state.y));
  if (b && !state.bHeld) handlers.back?.();
  state.aHeld = a;
  state.bHeld = b;
  return state;
}

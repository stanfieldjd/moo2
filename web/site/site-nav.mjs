/**
 * Independent browser navigation input for Game Lab website pages.
 * This module intentionally has no DOM, storage, game-engine or network APIs.
 * It models only standard Gamepad A/B and D-pad/stick edge transitions.
 */
export function createControllerState() {
  return {direction: 0, confirm: false, back: false};
}

const pressed = (buttons, n) => buttons?.[n]?.pressed === true;
const axis = (axes, n) => {
  const value = axes?.[n];
  return Number.isFinite(value) ? value : 0;
};

/** Stateless input interpretation, graceful when no Gamepad API exists. */
export function readController(gamepad) {
  if (!gamepad || gamepad.connected === false) {
    return createControllerState();
  }
  const buttons = gamepad.buttons || [];
  const axes = gamepad.axes || [];
  const up = pressed(buttons, 12) || axis(axes, 1) < -0.58;
  const down = pressed(buttons, 13) || axis(axes, 1) > 0.58;
  const left = pressed(buttons, 14) || axis(axes, 0) < -0.58;
  const right = pressed(buttons, 15) || axis(axes, 0) > 0.58;
  return {
    direction: (down || right) && !(up || left) ? 1 :
               (up || left) && !(down || right) ? -1 : 0,
    confirm: pressed(buttons, 0),
    back: pressed(buttons, 1),
  };
}

export function controllerEvents(previous, current) {
  const before = previous || createControllerState();
  const next = current || createControllerState();
  return {
    move: next.direction !== 0 && next.direction !== before.direction ? next.direction : 0,
    activate: next.confirm && !before.confirm,
    back: next.back && !before.back,
  };
}

/** Returns a bounded focus index; no navigation control may invent a link. */
export function nextFocusIndex(current, count, direction) {
  if (!Number.isInteger(count) || count < 1) return -1;
  if (direction !== -1 && direction !== 1) return current >= 0 && current < count ? current : 0;
  if (!Number.isInteger(current) || current < 0 || current >= count) return 0;
  return (current + direction + count) % count;
}

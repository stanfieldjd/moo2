/**
 * Read-only Gamepad API feature probe for Xbox One Edge compatibility tests.
 * No device telemetry is transmitted or stored.
 *
 * The Gamepad API may be unavailable, permission-blocked, or may produce
 * an empty list until a physical input event occurs.
 */
export function probeGamepads(navigatorLike) {
  if (!navigatorLike || typeof navigatorLike.getGamepads !== "function") {
    return { status: "unsupported", gamepads: [] };
  }
  try {
    const reported = navigatorLike.getGamepads();
    if (!reported || typeof reported[Symbol.iterator] !== "function") {
      return { status: "invalid-response", gamepads: [] };
    }
    const gamepads = Array.from(reported).filter(pad => pad && pad.connected !== false);
    return { status: gamepads.length ? "detected" : "waiting-for-input", gamepads };
  } catch (error) {
    return {
      status: "blocked",
      gamepads: [],
      reason: typeof error?.name === "string" ? error.name : "unknown-error",
    };
  }
}

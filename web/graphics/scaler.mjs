/**
 * Pixel-preserving scaling for predecoded RGBA game artwork.
 *
 * Input is ImageData-shaped {width,height,data:Uint8ClampedArray}; callers
 * retain palette conversion and animation timing in their separate importer.
 * Does not depend on game assets or LBX archives at browser runtime.
 */
function rgbaAt(data, width, height, x, y) {
  const xx = Math.max(0, Math.min(width - 1, x));
  const yy = Math.max(0, Math.min(height - 1, y));
  return (yy * width + xx) * 4;
}

function equalsAt(data, first, second) {
  return data[first] === data[second]
    && data[first + 1] === data[second + 1]
    && data[first + 2] === data[second + 2]
    && data[first + 3] === data[second + 3];
}

function assignPixel(target, destination, original, source) {
  target[destination] = original[source];
  target[destination + 1] = original[source + 1];
  target[destination + 2] = original[source + 2];
  target[destination + 3] = original[source + 3];
}

/** Scale2x/EPX: exact-color edge-aware 2x scaling. No invented colors. */
export function scale2x(image) {
  const { width, height, data } = image;
  if (!Number.isSafeInteger(width) || !Number.isSafeInteger(height)
      || width < 1 || height < 1 || width * height > 4194304
      || !data || data.length !== width * height * 4) {
    throw new RangeError("Invalid RGBA image dimensions or buffer.");
  }
  const outputWidth = width * 2;
  const output = new Uint8ClampedArray(outputWidth * height * 2 * 4);
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const e = rgbaAt(data, width, height, x, y);
      const b = rgbaAt(data, width, height, x, y - 1);
      const d = rgbaAt(data, width, height, x - 1, y);
      const f = rgbaAt(data, width, height, x + 1, y);
      const h = rgbaAt(data, width, height, x, y + 1);
      let a = e; let c = e; let g = e; let i = e;
      if (!equalsAt(data, b, h) && !equalsAt(data, d, f)) {
        if (equalsAt(data, d, b)) a = d;
        if (equalsAt(data, b, f)) c = f;
        if (equalsAt(data, d, h)) g = d;
        if (equalsAt(data, h, f)) i = f;
      }
      const top = ((y * 2) * outputWidth + x * 2) * 4;
      const bottom = (((y * 2) + 1) * outputWidth + x * 2) * 4;
      assignPixel(output, top, data, a);
      assignPixel(output, top + 4, data, c);
      assignPixel(output, bottom, data, g);
      assignPixel(output, bottom + 4, data, i);
    }
  }
  return { width: outputWidth, height: height * 2, data: output };
}

/** Pixel-perfect 2x nearest-neighbor scaling; useful for text and UI. */
export function nearest2x(image) {
  const { width, height, data } = image;
  if (!Number.isSafeInteger(width) || !Number.isSafeInteger(height)
      || width < 1 || height < 1 || width * height > 4194304
      || !data || data.length !== width * height * 4) {
    throw new RangeError("Invalid RGBA image dimensions or buffer.");
  }
  const out = new Uint8ClampedArray(width * height * 16);
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const from = (y * width + x) * 4;
      const top = ((y * 2) * (width * 2) + x * 2) * 4;
      const below = top + width * 2 * 4;
      assignPixel(out, top, data, from);
      assignPixel(out, top + 4, data, from);
      assignPixel(out, below, data, from);
      assignPixel(out, below + 4, data, from);
    }
  }
  return { width: width * 2, height: height * 2, data: out };
}

export function fitContain(width, height, boxWidth, boxHeight) {
  for (const n of [width, height, boxWidth, boxHeight]) {
    if (!Number.isFinite(n) || n <= 0) throw new RangeError("Dimensions must be positive.");
  }
  const ratio = Math.min(boxWidth / width, boxHeight / height);
  const outW = Math.max(1, Math.floor(width * ratio));
  const outH = Math.max(1, Math.floor(height * ratio));
  return { width: outW, height: outH, x: Math.floor((boxWidth - outW) / 2), y: Math.floor((boxHeight - outH) / 2) };
}

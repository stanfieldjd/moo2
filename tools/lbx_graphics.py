#!/usr/bin/env python3
"""Strict offline MOO2 LBX palette-indexed sprite/frame to RGBA PNG exporter.

For locally owned game archives only. Neither source game images nor derived
artwork belong in GitHub. Pure Python (standard library only).

Frame/animation rules independently implemented from Nick Bowler's liblbx
image-format specification (2ooM project; see accompanying research note).
"""
import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path
from zipfile import ZipFile


class FormatError(ValueError):
    pass


def u16(data, at):
    if at < 0 or at + 2 > len(data):
        raise FormatError("truncated uint16")
    return struct.unpack_from("<H", data, at)[0]


def u32(data, at):
    if at < 0 or at + 4 > len(data):
        raise FormatError("truncated uint32")
    return struct.unpack_from("<I", data, at)[0]


def lbx_entries(raw):
    """Read a genuine SimTex LBX container (not SMK video or FONTS content)."""
    if len(raw) < 12 or raw[2:6] != b"\xad\xfe\x00\x00":
        raise FormatError("not a SimTex LBX container")
    count = u16(raw, 0)
    if count < 1 or count > 4096 or 12 + count * 4 > len(raw):
        raise FormatError("implausible LBX entry count")
    offsets = [u32(raw, 8 + 4 * k) for k in range(count + 1)]
    if offsets[0] < 12 + count * 4 or offsets[-1] != len(raw):
        raise FormatError("incorrect LBX offsets or file size")
    if any(a > b for a, b in zip(offsets, offsets[1:])):
        raise FormatError("LBX offsets not monotonic")
    return [raw[a:b] for a, b in zip(offsets, offsets[1:])]


def image_info(raw):
    """Return checked header, offsets, embedded palette and animation flags."""
    if len(raw) < 20:
        raise FormatError("empty or non-graphics LBX entry")
    w, h, unknown, frames, unknown2, lead, chunk, flags = struct.unpack_from(
        "<HHHBBBBH", raw, 0
    )
    if not (1 <= w <= 2048 and 1 <= h <= 2048 and w*h <= 1048576):
        raise FormatError("invalid image dimensions")
    if not (1 <= frames <= 255 and lead < frames):
        raise FormatError("invalid animation frame count/lead-in")
    if unknown or unknown2:
        raise FormatError("unsupported image header fields")
    if flags & ~0x3d00:
        raise FormatError("unknown image flags")
    offsets_end = 12 + 4 * (frames + 1)
    if offsets_end > len(raw):
        raise FormatError("missing frame offset table")
    offsets = [u32(raw, 12 + 4*i) for i in range(frames+1)]
    if offsets[0] < offsets_end or offsets[-1] > len(raw):
        raise FormatError("frame offsets outside image")
    if any(a > b for a, b in zip(offsets, offsets[1:])):
        raise FormatError("frame offsets not monotonic")
    colors = {}
    if flags & 0x1000:
        base = offsets_end
        first = u16(raw, base)
        count = u16(raw, base+2)
        if first > 255 or count > 256 or first + count > 256:
            raise FormatError("invalid embedded palette range")
        if base + 4 + 4*count > offsets[0]:
            raise FormatError("embedded palette overlaps first frame")
        for idx in range(count):
            a, r, g, b = raw[base+4+4*idx:base+8+4*idx]
            if a not in (0, 1) or max(r,g,b) > 63:
                raise FormatError("unsupported DAC palette entry")
            colors[first+idx] = (r*4,g*4,b*4,255)
    return {
        "width":w, "height":h, "frames":frames, "lead_in":lead,
        "chunk":chunk, "flags":flags, "offsets":offsets,
        "palette":colors,
        "raw_frames":bool(flags & 0x100),
        "overwrite_frames":bool(flags & 0x400),
    }


def index_frame(entry, image, frame):
    """Decode indexed color + transparency mask through the selected frame.

    Transparent/omitted pixels retain the previous animation frame unless the
    image's overwrite/chunk flags specify a reset.
    """
    if frame < 0 or frame >= image["frames"]:
        raise FormatError("requested frame outside animation")
    width = image["width"]
    height = image["height"]
    size = width * height
    buf = bytearray(size)
    mask = bytearray(size)
    offsets = image["offsets"]
    step = 1 if image["overwrite_frames"] else image["chunk"]
    for i in range(frame+1):
        if i == 0 or (step and i % step == 0):
            buf[:] = b"\0" * size
            mask[:] = b"\0" * size
        start,end = offsets[i:i+2]
        if image["raw_frames"]:
            if end - start < size:
                raise FormatError("truncated raw frame")
            buf[:] = entry[start:start+size]
            mask[:] = b"\1" * size
            continue
        if end - start < 4 or u16(entry,start) != 1:
            raise FormatError("missing compressed frame header")
        x = 0
        y = u16(entry,start+2)
        p = start+4
        ended = False
        while p + 4 <= end:
            length = u16(entry,p)
            delta = u16(entry,p+2)
            p += 4
            if length == 0:
                if delta == 1000:
                    ended = True
                    break
                y += delta
                x = 0
                if y > height:
                    raise FormatError("row command exceeds image height")
                continue
            x += delta
            if y >= height or x + length > width or p + length > end:
                raise FormatError("paint command exceeds image/frame")
            target = y*width + x
            buf[target:target+length] = entry[p:p+length]
            mask[target:target+length] = b"\1"*length
            x += length
            p += length + (length & 1)
            if p > end:
                raise FormatError("pixel padding exceeds frame")
        if not ended:
            raise FormatError("missing end-of-frame marker")
    return buf, mask


def read_external_palette(raw):
    """Read 256 RGB6 entries from a non-image FONTS.LBX palette entry.

    The official data stores the palette in the initial 1024 bytes of
    a longer fonts archive entry. The first byte is 1 (unlike embedded
    image palette records, whose first byte may be 0).
    """
    if len(raw) < 1024:
        raise FormatError("external FONTS palette truncated")
    result={}
    for i in range(256):
        tag,r,g,b=raw[i*4:i*4+4]
        if tag != 1 or max(r,g,b)>63:
            raise FormatError("external palette header/channels invalid")
        result[i]=(r*4,g*4,b*4,255)
    return result


def resolve_palette(embedded, external=None):
    """Merge validated base and image-embedded overrides.

    An image's embedded palette entries take precedence over the external
    base palette, as intended by the original game format.
    """
    palette=dict(external or {})
    palette.update(embedded)
    return palette


def rgba_frame(pixels, mask, palette):
    if not palette:
        raise FormatError("no palette supplied; cannot render faithful colors")
    out = bytearray(4 * len(pixels))
    for i, (idx, opaque) in enumerate(zip(pixels,mask)):
        if opaque:
            try:
                out[i*4:i*4+4] = bytes(palette[idx])
            except KeyError as exc:
                raise FormatError(
                    f"color index {idx} missing from palette; external palette required"
                ) from exc
    return bytes(out)


def png_rgba(width,height,rgba):
    if len(rgba) != width*height*4:
        raise FormatError("RGBA buffer size mismatch")
    def chunk(tag,data):
        return struct.pack(">I",len(data))+tag+data+struct.pack(">I",zlib.crc32(tag+data)&0xffffffff)
    rows=b"".join(
        b"\0"+rgba[i*width*4:(i+1)*width*4] for i in range(height)
    )
    return (b"\x89PNG\r\n\x1a\n"
            +chunk(b"IHDR",struct.pack(">IIBBBBB",width,height,8,6,0,0,0))
            +chunk(b"IDAT",zlib.compress(rows,6))
            +chunk(b"IEND",b""))


def convert(archive, member, index, frame, destination, palette_member=None, palette_entry=None):
    if destination.exists():
        raise FormatError("destination exists; refusing overwrite")
    if archive.resolve() == destination.resolve():
        raise FormatError("source and destination must differ")
    if (palette_member is None) != (palette_entry is None):
        raise FormatError("palette-member and palette-entry must be supplied together")
    if palette_entry is not None and palette_entry < 0:
        raise FormatError("palette entry must be nonnegative")
    external={}
    with ZipFile(archive) as z:
        image_lbx = z.read(member)
        if palette_member is not None:
            pal_entries=lbx_entries(z.read(palette_member))
            if palette_entry >= len(pal_entries):
                raise FormatError("palette entry outside archive")
            external=read_external_palette(pal_entries[palette_entry])
    entries=lbx_entries(image_lbx)
    if index < 0 or index >= len(entries):
        raise FormatError("LBX image index outside archive")
    entry=entries[index]
    info=image_info(entry)
    pixels,mask=index_frame(entry,info,frame)
    palette=resolve_palette(info["palette"],external)
    rgba=rgba_frame(pixels,mask,palette)
    png=png_rgba(info["width"],info["height"],rgba)
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_bytes(png)
    result={
        "archive_member":member,"entry_index":index,"frame":frame,
        "width":info["width"],"height":info["height"],"frames":info["frames"],
        "lead_in":info["lead_in"],"chunk":info["chunk"],
        "image_flags":hex(info["flags"]),
        "palette_entries":len(palette),
        "palette_source": f"{palette_member}:{palette_entry}" if palette_member else "embedded-only",
        "opaque_pixels":sum(mask),"source_entry_sha256":hashlib.sha256(entry).hexdigest(),
        "rgba_sha256":hashlib.sha256(rgba).hexdigest(),
        "png_sha256":hashlib.sha256(png).hexdigest(),
        "png_bytes":len(png),"destination":str(destination),
        "note":"Local conversion from game owned by user; private, not for GitHub.",
    }
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive",type=Path)
    parser.add_argument("--member",required=True,
                        help="zip internal path like mastori2/LOGO.LBX")
    parser.add_argument("--entry",type=int,default=0)
    parser.add_argument("--frame",type=int,default=0)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--palette-member",help="external palette container such as mastori2/FONTS.LBX")
    parser.add_argument("--palette-entry",type=int,help="index of external palette in container")
    a=parser.parse_args()
    print(json.dumps(convert(a.archive,a.member,a.entry,a.frame,a.output,
                             a.palette_member,a.palette_entry),
                     indent=2,sort_keys=True))


if __name__=="__main__":
    main()

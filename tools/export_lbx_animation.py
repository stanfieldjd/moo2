#!/usr/bin/env python3
"""Export a MOO2 LBX animation to a private PNG sequence and manifest.

Requires a locally owned original game archive; never overwrites an existing
directory or uploads converted artwork. Select external palettes explicitly.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from zipfile import ZipFile

from lbx_graphics import (
    FormatError, image_info, index_frame, lbx_entries, png_rgba,
    read_external_palette, resolve_palette, rgba_frame,
)


def export_animation(archive: Path, member: str, entry_index: int,
                     outdir: Path, palette_member=None, palette_entry=None,
                     max_frames=255):
    if outdir.exists():
        raise FormatError("destination already exists; refusing overwrite")
    if (palette_member is None) != (palette_entry is None):
        raise FormatError("palette-member and palette-entry required together")
    if palette_entry is not None and palette_entry < 0:
        raise FormatError("invalid palette index")
    if max_frames < 1 or max_frames > 255:
        raise FormatError("invalid maximum frame count")
    with ZipFile(archive) as z:
        blobs = lbx_entries(z.read(member))
        if entry_index < 0 or entry_index >= len(blobs):
            raise FormatError("entry index out of bounds")
        src = blobs[entry_index]
        metadata = image_info(src)
        if metadata["frames"] > max_frames:
            raise FormatError("source animation exceeds requested maximum")
        external = {}
        if palette_member is not None:
            pal_blobs = lbx_entries(z.read(palette_member))
            if palette_entry >= len(pal_blobs):
                raise FormatError("external palette index out of bounds")
            external = read_external_palette(pal_blobs[palette_entry])
        colors = resolve_palette(metadata["palette"], external)
        # Reject incomplete palettes before creating the destination folder.
        frames = []
        for index in range(metadata["frames"]):
            pixels, mask = index_frame(src, metadata, index)
            image = rgba_frame(pixels, mask, colors)
            frames.append({
                "index": index,
                "rgba_hash": hashlib.sha256(image).hexdigest(),
                "png": png_rgba(metadata["width"], metadata["height"], image),
            })
    manifest = {
        "format": "moo2-browser-frames-v1",
        "source_member": member,
        "source_entry_index": entry_index,
        "source_entry_sha256": hashlib.sha256(src).hexdigest(),
        "palette_source": f"{palette_member}:{palette_entry}" if palette_member else "embedded",
        "width": metadata["width"], "height": metadata["height"],
        "frame_count": metadata["frames"],
        "lead_in": 0 if metadata["flags"] & 0x2000 else metadata["lead_in"],
        "chunk_size": 1 if metadata["flags"] & 0x0400 else metadata["chunk"],
        "frames": [
            {"frame": f["index"], "file": f"frame-{f['index']:03d}.png",
             "rgba_sha256": f["rgba_hash"],
             "png_sha256": hashlib.sha256(f["png"]).hexdigest()}
            for f in frames
        ],
        "warning": "Privately converted copyrighted game artwork; do not publish in GitHub or an unauthenticated server.",
        # No FPS claim. Game-timed frame cadence is not established by the LBX header.
        "frame_rate_verified": False,
    }
    outdir.mkdir(parents=True, exist_ok=False)
    try:
        for f in frames:
            (outdir / f"frame-{f['index']:03d}.png").write_bytes(f["png"])
        (outdir / "manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    except BaseException:
        shutil.rmtree(outdir)
        raise
    return manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive",type=Path)
    parser.add_argument("--member",required=True)
    parser.add_argument("--entry",type=int,default=0)
    parser.add_argument("--palette-member")
    parser.add_argument("--palette-entry",type=int)
    parser.add_argument("--output-dir",required=True,type=Path)
    parser.add_argument("--max-frames",type=int,default=255)
    args=parser.parse_args()
    manifest=export_animation(args.archive,args.member,args.entry,args.output_dir,
                              args.palette_member,args.palette_entry,args.max_frames)
    print(json.dumps({k:v for k,v in manifest.items() if k!="frames"},indent=2))


if __name__=="__main__":
    main()

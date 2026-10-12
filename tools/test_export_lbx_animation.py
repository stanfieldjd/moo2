#!/usr/bin/env python3
"""Synthetic checks for offline exported LBX animation manifests and safety."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from export_lbx_animation import export_animation
from lbx_graphics import FormatError
from test_lbx_graphics import make_archive, make_image, frame, command_pixels


class ExportTests(unittest.TestCase):
    def make_zip(self, destination, external=False):
        one=frame(command_pixels([1,1,1]))
        two=frame(command_pixels([1],skip=2))
        content=make_image([one,two],flags=0 if external else 0x1000)
        with ZipFile(destination,"w") as zipfile:
            zipfile.writestr("game/ART.LBX",make_archive(content))
            if external:
                colors=b"".join(bytes([1,i%64,0,(i//4)%64]) for i in range(256))
                zipfile.writestr("game/FONTS.LBX",make_archive(colors+b"more data"))
    def test_animation_export_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            source=root/"original.zip";self.make_zip(source)
            out=root/"derived"
            meta=export_animation(source,"game/ART.LBX",0,out)
            self.assertEqual((meta["width"],meta["height"],meta["frame_count"]),(3,2,2))
            self.assertEqual([e["file"] for e in meta["frames"]],["frame-000.png","frame-001.png"])
            self.assertTrue((out/"frame-000.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertEqual(json.loads((out/"manifest.json").read_text())["frame_count"],2)
            with self.assertRaises(FormatError):
                export_animation(source,"game/ART.LBX",0,out)
    def test_external_palette_export(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/"original.zip";self.make_zip(source,external=True)
            meta=export_animation(source,"game/ART.LBX",0,root/"private",
                                  "game/FONTS.LBX",0)
            self.assertEqual(meta["palette_source"],"game/FONTS.LBX:0")
            self.assertTrue((root/"private/frame-001.png").exists())
    def test_incomplete_palette_and_limits_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/"original.zip";self.make_zip(source,external=True)
            with self.assertRaises(FormatError):
                export_animation(source,"game/ART.LBX",0,root/"bad")
            self.assertFalse((root/"bad").exists())
            with self.assertRaises(FormatError):
                export_animation(source,"game/ART.LBX",0,root/"over",
                                 "game/FONTS.LBX",0,max_frames=1)
            self.assertFalse((root/"over").exists())


if __name__=="__main__":
    unittest.main(verbosity=2)

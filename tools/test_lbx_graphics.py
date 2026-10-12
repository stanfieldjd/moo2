#!/usr/bin/env python3
"""Tests for the deterministic offline MOO2 graphics decoder.

Synthetic fixture tests run without proprietary data; optional integration
tests require the user's original local archive in MOO2_GAME_ARCHIVE.
"""
import hashlib
import os
import struct
import unittest
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO

from lbx_graphics import (
    FormatError,lbx_entries,image_info,index_frame,rgba_frame,png_rgba,
    read_external_palette,resolve_palette,
)


def make_image(frames, width=3, height=2, flags=0x1000, chunk=0, lead=0):
    """Build a tiny self-contained image with two embedded palette colors."""
    n=len(frames)
    prefix=struct.pack("<HHHBBBBH",width,height,0,n,0,lead,chunk,flags)
    palette = (struct.pack("<HH",0,2)
               + bytes([0,0,0,0, 0,63,63,63])) if flags & 0x1000 else b""
    pos=12+4*(n+1)+len(palette)
    offsets=[pos]
    for f in frames:
        pos+=len(f);offsets.append(pos)
    return prefix+struct.pack("<"+"I"*(n+1),*offsets)+palette+b"".join(frames)


def make_archive(*data):
    count=len(data)
    pos=max(2048,8+4*(count+1))
    offsets=[pos]
    for frame in data:
        pos+=len(frame)
        offsets.append(pos)
    return (struct.pack("<HIH",count,0xFEAD,0)
            +struct.pack("<"+"I"*(count+1),*offsets)
            +bytes(max(2048,8+4*(count+1))-(8+4*(count+1)))
            +b"".join(data))


def command_pixels(pixels,skip=0):
    return struct.pack("<HH",len(pixels),skip)+bytes(pixels)+(b"\0" if len(pixels)%2 else b"")


def frame(*commands):
    return struct.pack("<HH",1,0)+b"".join(commands)+struct.pack("<HH",0,1000)


class DecoderTests(unittest.TestCase):
    def test_lbx_archive_and_reject_video(self):
        archive=make_archive(b"cat",b"doge")
        self.assertEqual(lbx_entries(archive),[b"cat",b"doge"])
        with self.assertRaises(FormatError):
            lbx_entries(b"SMK2"+b"x"*60)
        damaged=bytearray(archive)
        struct.pack_into("<I",damaged,16,0)
        with self.assertRaises(FormatError):
            lbx_entries(damaged)

    def test_raw_single_frame_and_palette(self):
        original=make_image([bytes([0,1,1,0,1,0])],flags=0x1100)
        info=image_info(original)
        pixels,mask=index_frame(original,info,0)
        self.assertEqual(list(pixels),[0,1,1,0,1,0])
        self.assertEqual(list(mask),[1]*6)
        self.assertEqual(info["palette"][1],(252,252,252,255))
        png=png_rgba(3,2,rgba_frame(pixels,mask,info["palette"]))
        self.assertEqual(png[:8],b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">II",png[16:24]),(3,2))

    def test_transparency_skip_padding_and_frame_delta(self):
        first=frame(command_pixels([1,1]),struct.pack("<HH",0,1),command_pixels([1],skip=1))
        second=frame(command_pixels([0],skip=2))
        raw=make_image([first,second])
        info=image_info(raw)
        pixels,mask=index_frame(raw,info,0)
        self.assertEqual(list(pixels),[1,1,0,0,1,0])
        self.assertEqual(list(mask),[1,1,0,0,1,0])
        pixels,mask=index_frame(raw,info,1)
        self.assertEqual(list(pixels),[1,1,0,0,1,0])
        self.assertEqual(list(mask),[1,1,1,0,1,0])
        rgba=rgba_frame(pixels,mask,info["palette"])
        self.assertEqual(rgba[8:12],bytes([0,0,0,255]))
        self.assertEqual(rgba[12:16],b"\0"*4)

    def test_chunk_and_overwrite_reset(self):
        first=frame(command_pixels([1,1,1]))
        second=frame(command_pixels([1],skip=2))
        for flags,chunk in [(0x1000,1),(0x1400,0)]:
            raw=make_image([first,second],flags=flags,chunk=chunk)
            info=image_info(raw)
            px,mask=index_frame(raw,info,1)
            self.assertEqual(list(mask),[0,0,1,0,0,0])

    def test_missing_palette_rejected(self):
        raw=make_image([frame(command_pixels([1]))],flags=0)
        image=image_info(raw)
        pixels,mask=index_frame(raw,image,0)
        with self.assertRaises(FormatError):
            rgba_frame(pixels,mask,image["palette"])

    def test_truncated_frame_or_oversized_row(self):
        frame_bytes=frame(command_pixels([1,1,1,1]))
        raw=make_image([frame_bytes])
        with self.assertRaises(FormatError):
            index_frame(raw,image_info(raw),0)
        bad=raw[:-4]  # lost end-of-frame marker
        with self.assertRaises(FormatError):
            index_frame(bad,image_info(bad),0)

    def test_external_palette_and_precedence(self):
        import itertools
        raw=b"".join(bytes([1,i%64,0,63]) for i in range(256))
        colors=read_external_palette(raw+b"some other font data")
        self.assertEqual(len(colors),256)
        self.assertEqual(colors[63],(252,0,252,255))
        self.assertEqual(resolve_palette({5:(9,8,7,255)},colors)[5],(9,8,7,255))
        with self.assertRaises(FormatError):read_external_palette(raw[:1023])
        with self.assertRaises(FormatError):read_external_palette(bytes([2])+raw[1:])
        with self.assertRaises(FormatError):read_external_palette(bytes([1,64])+raw[2:])

    def test_real_mainmenu_external_palette_when_supplied(self):
        path=os.getenv("MOO2_GAME_ARCHIVE")
        if not path:self.skipTest("set MOO2_GAME_ARCHIVE to locally owned ZIP")
        with ZipFile(path) as z:
            font=lbx_entries(z.read("mastori2/FONTS.LBX"))[6]
            palette=read_external_palette(font)
            self.assertEqual(len(palette),256)
            bg=lbx_entries(z.read("mastori2/MAINMENU.LBX"))[0]
            info=image_info(bg)
            self.assertEqual((info["width"],info["height"],info["frames"]),(640,480,50))
            self.assertEqual(len(info["palette"]),0)
            for frame,expected in [
                (0,"fa88fcdb0d52b837eeb85c8dc73263e60a8a911e4406746c3582cb30a4b9cb4e"),
                (49,"2420bc887b5032b79579afb8a2dff97fedf9684d9587fe66a8d83609a9c97239"),
            ]:
                with self.subTest(frame=frame):
                    pixels,mask=index_frame(bg,info,frame)
                    self.assertEqual(sum(mask),307200)
                    self.assertEqual(hashlib.sha256(rgba_frame(pixels,mask,resolve_palette(info["palette"],palette))).hexdigest(),expected)

    def test_real_original_animated_frames_when_supplied(self):
        path=os.getenv("MOO2_GAME_ARCHIVE")
        if not path:
            self.skipTest("set MOO2_GAME_ARCHIVE to locally owned game ZIP")
        with ZipFile(path) as z:
            logo=lbx_entries(z.read("mastori2/LOGO.LBX"))[1]
            image=image_info(logo)
            self.assertEqual((image["width"],image["height"],image["frames"]),(640,480,64))
            for frame,expected in [
                (0,"d483433bcbb422b9b02ecf9bae3332c50830b8b5696698ad3e629c00c35da68e"),
                (63,"3afe946498bb3d843364af766626a4681828beb76762332c1014bd2e4ee6129b"),
            ]:
                with self.subTest(frame=frame):
                    indices,mask=index_frame(logo,image,frame)
                    self.assertEqual(sum(mask),307200)
                    self.assertEqual(hashlib.sha256(rgba_frame(indices,mask,image["palette"])).hexdigest(),expected)
            # MAINMENU frame 49 is valid indexed animation, but must *not* be
            # painted in guessed colors: this entry requires an external palette.
            menu=lbx_entries(z.read("mastori2/MAINMENU.LBX"))[0]
            metadata=image_info(menu)
            self.assertEqual(metadata["frames"],50)
            indices,mask=index_frame(menu,metadata,49)
            self.assertEqual(sum(mask),307200)
            with self.assertRaises(FormatError):
                rgba_frame(indices,mask,metadata["palette"])

    def test_real_original_embedded_palettes_when_supplied(self):
        path=os.getenv("MOO2_GAME_ARCHIVE")
        if not path:
            self.skipTest("set MOO2_GAME_ARCHIVE to locally owned game ZIP")
        with ZipFile(path) as z:
            checks={
                ("mastori2/LOGO.LBX",0):(640,480,1,256,300671,
                    "6659d5496e098ec1f9bc33ffc82bd77e3fca60e1a016bc643c4755d94e082190"),
                ("mastori2/MAINMENU.LBX",1):(640,480,1,256,307200,
                    "fa88fcdb0d52b837eeb85c8dc73263e60a8a911e4406746c3582cb30a4b9cb4e"),
            }
            for (name,index),(w,h,frames,pal,opaque,expected) in checks.items():
                with self.subTest(name=name,index=index):
                    entries=lbx_entries(z.read(name))
                    image=image_info(entries[index])
                    self.assertEqual((image["width"],image["height"],image["frames"],len(image["palette"])),(w,h,frames,pal))
                    px,mask=index_frame(entries[index],image,0)
                    self.assertEqual(sum(mask),opaque)
                    self.assertEqual(hashlib.sha256(rgba_frame(px,mask,image["palette"])).hexdigest(),expected)


if __name__=="__main__":
    unittest.main(verbosity=2)

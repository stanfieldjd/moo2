#!/usr/bin/env python3
"""Read-only verifier and Watcom-symbol probe for official MOO2 v1.31 ORION2.EXE."""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path

OFFICIAL_SHA256 = '4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f'
WATCOM_MASTER_SIGNATURE = 0x8386
TARGET_SYMBOLS = (
    '_planet_size_table', '_planet_max_farms', '_planet_max_mines',
    '_planet_max_population', '_climate_modifier_table', '_food_per_farmer_table',
)
GAMEPLAY_FUNCTIONS = (
    'Size_Subterranean_Pop_Bonus_',
    'Size_And_Climate_Max_Population_',
    'Size_And_Climate_Race_Pop_Limit_',
    'Planet_Max_Population_For_Player_',
    'Colony_Race_Pop_Limit_',
    'Colony_Pop_Grows_',
    'Apply_Colony_Pop_Growth_',
    'Housing_Is_Useless_',
    'Enforce_Population_Limits_At_Colony_',
    'Colony_Food2_Per_Farmer_',
    'Colony_Food_Maintenance_',
    'isqrt_',
)

class ProbeError(ValueError): pass

def u16(d: bytes, o: int) -> int: return struct.unpack_from('<H', d, o)[0]
def u32(d: bytes, o: int) -> int: return struct.unpack_from('<I', d, o)[0]

def watcom_layout(data: bytes) -> dict:
    # master_dbg_header is fixed at EOF and is 14 bytes in Watcom format.
    if len(data) < 14: raise ProbeError('file too short for Watcom master header')
    o = len(data) - 14
    sig, exmaj, exmin, objmaj, objmin, lang_size, segment_size, debug_size = struct.unpack_from('<HBBBBHHI', data, o)
    if sig != WATCOM_MASTER_SIGNATURE: raise ProbeError('Watcom debug master signature not found at EOF')
    if not (14 <= debug_size <= len(data)): raise ProbeError('invalid Watcom debug size')
    debug_start = len(data) - debug_size
    section_start = debug_start + lang_size + segment_size
    if section_start + 18 > o: raise ProbeError('truncated Watcom section header')
    mod_off, gbl_off, addr_off, section_size, section_id = struct.unpack_from('<IIIIH', data, section_start)
    if not (mod_off < gbl_off < addr_off < section_size): raise ProbeError('invalid Watcom section offsets')
    if section_start + section_size > o: raise ProbeError('Watcom section exceeds debug area')
    return {
        'debug_start': debug_start, 'debug_size': debug_size,
        'exe_debug_version': [exmaj, exmin], 'object_debug_version': [objmaj, objmin],
        'language_table_size': lang_size, 'segment_table_size': segment_size,
        'section_start': section_start, 'section_size': section_size, 'section_id': section_id,
        'module_info_start': section_start + mod_off,
        'global_symbols_start': section_start + gbl_off,
        'address_info_start': section_start + addr_off,
    }

def global_symbols(data: bytes, layout: dict) -> dict[str, dict]:
    p, end = layout['global_symbols_start'], layout['address_info_start']
    result: dict[str, dict] = {}
    while p < end:
        if p + 10 > end: raise ProbeError('truncated global symbol record')
        offset, segment, module_index, kind, name_len = struct.unpack_from('<IHHBB', data, p)
        p += 10
        if p + name_len > end: raise ProbeError('truncated global symbol name')
        name = data[p:p+name_len].decode('latin1'); p += name_len
        result[name] = {'segment': segment, 'offset': offset, 'module_index': module_index, 'kind': kind}
    if p != end: raise ProbeError('global symbol class length mismatch')
    return result

def mz_image_size(data: bytes) -> int:
    """Return the byte size described by the leading DOS MZ header."""
    if len(data) < 0x1c or data[:2] != b'MZ':
        raise ProbeError('leading DOS MZ header not found')
    last_page_bytes = u16(data, 2)
    page_count = u16(data, 4)
    if page_count == 0:
        raise ProbeError('invalid MZ page count')
    size = (page_count - 1) * 512 + (last_page_bytes or 512)
    if size > len(data):
        raise ProbeError('MZ image exceeds file size')
    return size

def bound_payload(data: bytes) -> dict:
    """Identify the executable appended after the DOS loader image.

    ORION2.EXE is a bound executable: its MZ header describes the loader
    image, and the next executable begins immediately after that image.
    We identify the payload but deliberately do not guess a selector-to-file
    mapping until its descriptor records have been decoded.
    """
    start = mz_image_size(data)
    if start + 2 > len(data):
        raise ProbeError('no bound payload after MZ image')
    signature = data[start:start+2]
    if signature not in (b'BW', b'LE', b'LX'):
        raise ProbeError(f'unsupported bound payload signature {signature!r}')
    return {'file_offset': start, 'signature': signature.decode('ascii')}


def le_layout(data: bytes, module_base: int) -> dict:
    """Parse the chained DOS/4GW LE image used by the official executable."""
    if module_base + 0x40 > len(data) or data[module_base:module_base+2] != b'MZ':
        raise ProbeError('chained MZ image not found')
    le_start = module_base + u32(data, module_base + 0x3c)
    if le_start + 0xc4 > len(data) or data[le_start:le_start+2] != b'LE':
        raise ProbeError('chained LE image not found')
    page_size = u32(data, le_start + 0x28)
    objtab_off = u32(data, le_start + 0x40)
    object_count = u32(data, le_start + 0x44)
    objmap_off = u32(data, le_start + 0x48)
    data_pages_off = u32(data, le_start + 0x80)
    if page_size == 0 or object_count == 0:
        raise ProbeError('invalid LE image geometry')
    objects = []
    for i in range(object_count):
        o = le_start + objtab_off + 24 * i
        if o + 24 > len(data): raise ProbeError('truncated LE object table')
        size, address, flags, map_index, map_count, reserved = struct.unpack_from('<IIIIII', data, o)
        objects.append({'number': i + 1, 'size': size, 'address': address, 'flags': flags,
                        'map_index': map_index, 'map_count': map_count, 'reserved': reserved})
    return {'module_base': module_base, 'le_start': le_start, 'page_size': page_size,
            'object_page_map': le_start + objmap_off,
            # In this bound image the LE data-page offset is relative to the chained MZ module.
            'data_pages_start': module_base + data_pages_off, 'objects': objects}

def le_object_file_offset(data: bytes, le: dict, object_number: int, offset: int) -> int:
    if not (1 <= object_number <= len(le['objects'])):
        raise ProbeError('LE object number out of range')
    obj = le['objects'][object_number - 1]
    if not (0 <= offset < obj['size']): raise ProbeError('LE object offset out of range')
    page_size = le['page_size']; logical_page, within = divmod(offset, page_size)
    if logical_page >= obj['map_count']: raise ProbeError('LE object offset is not file-backed')
    entry = le['object_page_map'] + 4 * (obj['map_index'] - 1 + logical_page)
    if entry + 4 > len(data): raise ProbeError('truncated LE page map')
    # LE stores its 24-bit physical page number most-significant byte first.
    page_number = int.from_bytes(data[entry:entry+3], 'big'); page_flags = data[entry+3]
    if page_number == 0 or page_flags != 0: raise ProbeError('LE page is not a normal file-backed page')
    result = le['data_pages_start'] + (page_number - 1) * page_size + within
    if result >= len(data): raise ProbeError('mapped LE offset exceeds file size')
    return result

def extract_target_tables(data: bytes, syms: dict[str, dict], le: dict) -> dict[str, dict]:
    """Extract each target through its debug-symbol address, never a guessed raw offset."""
    ordered = sorted((v['offset'], n) for n, v in syms.items() if v['segment'] == 2)
    next_offset = {ordered[i][1]: ordered[i+1][0] for i in range(len(ordered)-1)}
    result = {}
    for name in TARGET_SYMBOLS:
        sym = syms.get(name)
        if sym is None or sym['segment'] != 2 or name not in next_offset: continue
        length = next_offset[name] - sym['offset']
        file_offset = le_object_file_offset(data, le, 2, sym['offset'])
        raw = data[file_offset:file_offset+length]
        if len(raw) != length: raise ProbeError('truncated target table')
        result[name] = {'file_offset': file_offset, 'length': length, 'bytes': list(raw),
                        'signed_bytes': [b - 256 if b >= 128 else b for b in raw]}
    return result

def inspect(path: Path) -> dict:
    data = path.read_bytes(); digest = hashlib.sha256(data).hexdigest()
    payload = bound_payload(data)
    layout = watcom_layout(data)
    syms = global_symbols(data, layout)
    targets = {name: syms.get(name) for name in TARGET_SYMBOLS}
    # The first BW header points to the chained MZ/LE program image with an absolute file offset.
    bw_next_header = u32(data, payload['file_offset'] + 0x1c)
    le = le_layout(data, bw_next_header)
    tables = extract_target_tables(data, syms, le)
    gameplay_functions = {}
    for name in GAMEPLAY_FUNCTIONS:
        sym = syms.get(name)
        if sym is None:
            continue
        file_offset = le_object_file_offset(data, le, sym['segment'], sym['offset'])
        gameplay_functions[name] = {**sym, 'file_offset': file_offset,
                                    'first_bytes': data[file_offset:file_offset+32].hex()}
    return {
        'path': str(path), 'size': len(data), 'sha256': digest,
        'official_v131_reference': digest == OFFICIAL_SHA256,
        'bound_payload': payload,
        'le_image': le,
        'watcom': layout,
        'target_symbols': targets,
        'target_tables': tables,
        'gameplay_functions': gameplay_functions,
        'all_gameplay_functions_resolved': len(gameplay_functions) == len(GAMEPLAY_FUNCTIONS),
        'all_target_symbols_resolved': all(v is not None for v in targets.values()),
        'note': 'Addresses are linker unrelocated segment:offset values, not raw file offsets.',
    }

def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument('exe', type=Path); ap.add_argument('--json', action='store_true'); a=ap.parse_args()
    try: result=inspect(a.exe)
    except (OSError, ProbeError, struct.error) as e:
        print(f'error: {e}'); raise SystemExit(2)
    if a.json: print(json.dumps(result, indent=2))
    else:
        print('SHA-256:', result['sha256']); print('Official v1.31 reference:', result['official_v131_reference'])
        print('Bound payload:', result['bound_payload']['signature'], f"@ 0x{result['bound_payload']['file_offset']:x}")
        for n,v in result['target_symbols'].items():
            print(f"{n}: {v['segment']:04x}:{v['offset']:08x}" if v else f'{n}: NOT FOUND')
        for n,v in result['gameplay_functions'].items():
            print(f"{n}: {v['segment']:04x}:{v['offset']:08x} -> file 0x{v['file_offset']:x}")
        for n,v in result['target_tables'].items():
            values = v['signed_bytes'] if n == '_climate_modifier_table' else v['bytes']
            print(f"{n} data @ 0x{v['file_offset']:x} ({v['length']} bytes): {values}")
        print(result['note'])
    raise SystemExit(0 if result['official_v131_reference'] and result['all_target_symbols_resolved'] else 2)
if __name__=='__main__': main()

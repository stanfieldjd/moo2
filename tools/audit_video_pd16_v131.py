#!/usr/bin/env python3
"""Recover original v1.31 Watcom video real-mode functions, not 32-bit gameplay.

Source-byte authenticates original eight-byte zero storage and four complete
independent 16-bit video helper bodies (plus one RET helper), with exact
instruction boundaries, original near control transfer destinations,
explicit state stores, far segment loads and format operations.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
PD_SYMBOL_SHA="4fc3b2a5781a5ecac7bb49222db60a6217605e951969cacf3ef526ea4ed889d3"
SEGMENTS=[
 ("video_base_position",0x1583A5,0x1583D5,29,"5e4fd6eda38910b842bbdea2774e0d244a1326562119ea9767db2fb73a8d0c39"),
 ("video_character",0x1583D5,0x1583FC,22,"c648095e9df03e070e13a56f8285b87b39cedfb72af0c0a1993856440c25d3d2"),
 ("video_NUL_terminated_string",0x1583FC,0x158420,24,"a3125eb2a69f505a63a6225de72e8101d63a54b564c35c8801abde5dd8485096"),
 ("video_two_hex_digits",0x158420,0x158459,28,"1804b85a0e0dc3e4581c929fc3a93ae6c765e5f519d323abd632a48e43e6ea6d"),
 ("ISR_delay_RET_helper",0x158459,0x15845A,1,"ae3f4619b0413d70d3004b9131c3752153074e45725be13b9a148978895e359e"),
]
BRANCHES={
 0x1583E7:("je",0x1583F6),
 0x15840C:("je",0x15841A),
 0x158418:("jmp",0x158408),
 0x158436:("jle",0x15843A),
 0x15844B:("jle",0x15844F),
}
NEAR_CALLS={
 0x158411:0x1583D5,
 0x15843B:0x1583D5,
 0x158450:0x1583D5,
}
SOURCE_OPS={
 0x1583B0:("les","bx,DWORD PTR ds:0x26d"),
 0x1583B7:("mov","cl,0xa0"),
 0x1583B9:("mul","cl"),
 0x1583C0:("shl","ax,1"),
 0x1583C6:("mov","ds:0x273,ax"),
 0x1583C9:("mov","WORD PTR ds:0x271,bx"),
 0x1583DE:("les","bx,DWORD PTR ds:0x271"),
 0x1583EC:("mov","BYTE PTR es:[bx],al"),
 0x1583EF:("add","bx,0x2"),
 0x1583F2:("mov","WORD PTR ds:0x271,bx"),
 0x158408:("mov","al,BYTE PTR [bx]"),
 0x15840A:("cmp","al,0x0"),
 0x158411:("call","0x1583d5"),
 0x158424:("mov","ax,WORD PTR [bp+0x4]"),
 0x15842F:("and","ax,0xf"),
 0x158432:("add","al,0x30"),
 0x158434:("cmp","al,0x39"),
 0x158438:("add","al,0x7"),
 0x158444:("and","ax,0xf"),
 0x158447:("add","al,0x30"),
 0x158449:("cmp","al,0x39"),
 0x15844D:("add","al,0x7"),
 0x158459:("ret",""),
}
RX_MORE=re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s*)+)$',re.I)
RX_INSN=re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$',re.I)

def digest(data):return hashlib.sha256(data).hexdigest()

def decode16(image,path,begin,end):
    proc=subprocess.run(["objdump","-D","-b","binary","-m","i8086","-M","intel",
                         f"--start-address={begin}",f"--stop-address={end}",str(path)],
                        capture_output=True,text=True,check=True)
    ins=[]
    for line in proc.stdout.splitlines():
        m=RX_MORE.match(line)
        if m:
            a=int(m.group(1),16);raw=bytes.fromhex(m.group(2))
            if not ins or ins[-1][0]+len(ins[-1][1])!=a:raise ValueError("Orphaned original video machine-byte continuation")
            addr,prev,op,args=ins[-1]
            ins[-1]=(addr,prev+raw,op,args)
            continue
        m=RX_INSN.match(line)
        if m:ins.append((int(m.group(1),16),bytes.fromhex(m.group(2)),m.group(3).lower(),m.group(4).strip()))
    cur=begin
    for a,raw,op,args in ins:
        if a!=cur or image[a:a+len(raw)]!=raw:
            raise ValueError(f"Incorrect original 16-bit CODE instruction at {a:#x}")
        cur+=len(raw)
    if cur!=end:raise ValueError(f"16-bit original video routine not fully decoded: {begin:#x}:{cur:#x}!={end:#x}")
    return ins

def displacement(addr,raw):
    if raw[0] in (*range(0x70,0x80),0xeb,0xe3) and len(raw)==2:
        signed=int.from_bytes(raw[1:2],"little",signed=True)
    elif raw[0] in (0xe8,0xe9) and len(raw)==3:
        signed=int.from_bytes(raw[1:],"little",signed=True)
    else:raise ValueError(f"Not a verified original real-mode direct control transfer at {addr:#x}")
    return addr+len(raw)+signed

def audit(exe,code):
    source=code.read_bytes()
    if (len(source),digest(source),digest(exe.read_bytes()))!=(1410709,CODE_SHA,EXE_SHA):
        raise ValueError("Official DOS v1.31 source fingerprint differs")
    headers={r["name"]:r for r in csv.DictReader((ROOT/"decompilation/functions.csv").open())}
    sym={r["name"]:r for r in csv.DictReader((ROOT/"decompilation/symbols.csv").open()) if r["segment"]=="1"}
    src_begin=0x15839D
    src_end=0x158459
    if headers["__VideoBasePD16"]["offset"]!=str(src_begin) or int(headers["__VideoBasePD16"]["inferred_size"])!=188:
        raise ValueError("Original Watcom mixed storage/video CODE source span differs")
    if sym["__VideoBasePD16"]["kind"]!="4" or digest(source[src_begin:src_end])!=PD_SYMBOL_SHA:
        raise ValueError("Original Watcom video section whole-body source bytes differ")
    if source[src_begin:src_begin+8]!=b"\x00"*8:
        raise ValueError("Original video output pointer storage isn't eight zero bytes")
    if source[src_end:src_end+1]!=b"\xc3":
        raise ValueError("Delay helper source RET adjacent to video CODE differs")
    instructions=[]
    reports=[]
    for name,start,end,count,sha in SEGMENTS:
        if digest(source[start:end])!=sha:
            raise ValueError(f"Original 16-bit CODE source body SHA differs {name}")
        decoded=decode16(source,code,start,end)
        if len(decoded)!=count or decoded[-1][2]!="ret":
            raise ValueError("Expected source complete real-mode RET function body missing")
        reports.append({"reconstructed_role":name,"original_CODE_start":hex(start),
            "original_CODE_end_exclusive":hex(end),"machine_code_bytes":end-start,
            "original_source_complete_body_SHA256":sha,
            "complete_original_real_mode_instructions":len(decoded),
            "terminates_16bit_RET":True})
        instructions.extend(decoded)
    if (len(instructions),sum(len(v[1]) for v in instructions))!=(104,181):
        raise ValueError("Complete real-mode helper function inventory changed")
    by_addr={r[0]:r for r in instructions}
    if len(by_addr)!=104:raise ValueError("Overlapping original CODE instruction addresses")
    branches={a for a,raw,op,args in instructions if op.startswith("j")}
    calls={a for a,raw,op,args in instructions if op=="call"}
    if branches!=set(BRANCHES) or calls!=set(NEAR_CALLS):
        raise ValueError("Original 16-bit video branch/CALL site inventory differs")
    for a,(expected_op,dest) in BRANCHES.items():
        actual=by_addr[a]
        if actual[2]!=expected_op or displacement(a,actual[1])!=dest or dest not in by_addr:
            raise ValueError(f"Original 16-bit video jump destination invalid at {a:#x}")
    for a,dest in NEAR_CALLS.items():
        real=by_addr[a]
        if real[2]!="call" or displacement(a,real[1])!=dest or dest not in by_addr:
            raise ValueError(f"Original video helper CALL source destination invalid {a:#x}")
    for a,(opcode,args) in SOURCE_OPS.items():
        raw=by_addr.get(a)
        if not raw or (raw[2],raw[3])!=(opcode,args):
            raise ValueError(f"Original video source opcode/args changed {a:#x}: {raw}")
    # Redundancy check: the already audited source segment RR16 includes the
    # same one-byte RET delay helper at 0x158459, immediately before ISR entry.
    if source[0x15845A:0x15845E]!=bytes.fromhex("558bec1e"):
        raise ValueError("Original adjacent Greenleaf ISR entry prefix changed")
    baseline=json.loads((ROOT/"decompilation/function_cfg_extents.json").read_text())
    if (baseline["functions"],baseline["cfg_membership_records"])!=(5635,396305):
        raise ValueError("Do not substitute the separate 16-bit count for the global i386 CFG")
    return {
     "status":"original-source-authenticated-MOO2-v131-mixed-PD16-video-helpers",
     "official_original_EXE_SHA256":EXE_SHA,"original_Watcom_CODE_SHA256":CODE_SHA,
     "original_video_PD16_symbol_start":hex(src_begin),
     "original_video_PD16_symbol_bytes":188,
     "original_video_PD16_full_source_SHA256":PD_SYMBOL_SHA,
     "original_video_PD16_zero_storage_prefix_bytes":8,
     "source_full_16bit_CODE_helper_records":reports,
     "all_complete_original_16bit_instructions_authenticated":len(instructions),
     "source_original_16bit_CODE_machine_bytes":sum(len(v[1]) for v in instructions),
     "source_exact_direct_16bit_branch_destinations":[{"site":hex(a),"target":hex(t),"opcode":op} for a,(op,t) in BRANCHES.items()],
     "source_exact_direct_16bit_helper_CALLs":[{"site":hex(a),"target":hex(t)} for a,t in NEAR_CALLS.items()],
     "original_source_opcode_and_operand_assertions":len(SOURCE_OPS),
     "source_operand_offsets_confirmed":{
       "video_far_segment_base":"DS:0x26D; LES BX loads ES:BX",
       "video_far_cursor":"DS:0x271 and DS:0x273 are two WORD halves of a far pointer",
       "video_position_arithmetic":"CL=0xA0, MUL CL, plus twice second argument",
       "video_output_instruction":"MOV BYTE PTR ES:[BX],AL",
       "video_output_cursor_step":"ADD BX,0x02",
       "hexadecimal_nibble_character_map":"AND AX,0x000F, ADD AL,0x30, conditional ADD AL,0x07"
     },
     "source_original_zero_storage_not_decoded_as_opcodes":8,
     "source_16bit_delay_helper_adjacent_to_ISR":hex(0x158459),
     "global_32bit_CFG_memberships_unmodified":baseline["cfg_membership_records"],
     "scope":"Source 16-bit Video Base runtime code and original 8-byte storage are independently audited. No native DOS hardware video test or game screen parity is claimed, and these 104 instructions are NOT added to the global 32-bit CFG metric.",
     "limits":["Original hardware display mode/screen layout not established from these functions alone",
               "16-bit source routine call ABI inferred only from verified stack-relative instructions",
               "No claim of complete game semantic decompilation or browser game playability"]
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe",required=True,type=Path)
    parser.add_argument("--code",required=True,type=Path)
    parser.add_argument("--output",type=Path)
    a=parser.parse_args()
    report=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))

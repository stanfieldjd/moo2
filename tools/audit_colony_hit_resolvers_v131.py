#!/usr/bin/env python3
"""Audit the original v1.31 MOO2 bomb and biological hit resolver regions.

Two complete Watcom named function source-byte SHA hashes and selected
original x86 opcode anchors. The biological resolver branches to a
shared 6-byte LEAVE/POPs/RET in the Destroy_Colony_ symbol interval,
rather than an in-function epilogue for its no-target case.
No DOS dynamic equivalence or full resolver side effects claimed.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
SPECS=[
 ("Resolve_Bomb_Hit_",0xCCEBD,641,
  "ee665889d157c0882ac1512a67f1f940bf25a1d3d76811dcad0f30558d53dc89"),
 ("Resolve_Biological_Hit_",0xCD13E,436,
  "b19a11cb99d998a561924d948cb77b58fa2c69f246aca89e6c9f9379c6a81dd8"),
]
SHARED_OFFSET=0xCCEB7
SHARED_BYTES=6
SHARED_SHA="0488d06b31fc4e6e52f9e400c94ead43b0ebe94d902f47cab4c51cbf59946c54"
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
OPS={
  0xCD146:("mov","ebx,eax"),
  0xCD148:("movzx","esi,byte ptr [eax+0xa]"),
  0xCD155:("shl","ecx,0x2"),
  0xCD158:("xor","edi,edi"),
  0xCD15E:("mov","eax,dword ptr [ecx+0x8]"),
  0xCD164:("and","eax,0xf"),
  0xCD168:("cmp","eax,0x8"),
  0xCD170:("call","0x1147a0"),
  0xCD175:("cmp","eax,0x1"),
  0xCD17A:("mov","dword ptr [ebp-0x4],esi"),
  0xCD17F:("jg","0xcd15e"),
  0xCD181:("cmp","dword ptr [ebp-0x4],0x0"),
  0xCD185:("jl","0xcceb7"),
  0xCD18B:("mov","byte ptr [edx+0x41],0x1"),
  0xCD18F:("cmp","byte ptr [ebx+0xa],0x2"),
  0xCD1B0:("call","0x1147a0"),
  0xCD1B9:("inc","word ptr [edx+0xc]"),
  0xCD1BD:("inc","word ptr [edx+0x3f]"),
  0xCD1C1:("dec","byte ptr [ebx+0xa]"),
  0xCD217:("dec","word ptr [ebx+0x130]"),
  0xCD21E:("inc","word ptr [edx+0x8]"),
  0xCD227:("dec","word ptr [ebx+0x132]"),
  0xCD22E:("inc","word ptr [edx+0xa]"),
  0xCD26A:("cmp","word ptr [ebx+eax*2+0xb4],0x64"),
  0xCD275:("inc","word ptr [edx+0xc]"),
  0xCD28A:("mov","word ptr [ebx+eax*2+0xb4],0x0"),
  0xCD2A6:("mov","byte ptr [edx+0x42],0x1"),
  0xCD2E4:("sub","word ptr [ebx+eax*2+0xb4],0x64"),
  0xCCEE4:("mov","ebx,0x31"),
  0xCCEEF:("dec","edi"),
  0xCCEF0:("dec","ebx"),
  0xCCEF1:("cmp","byte ptr [edi+0x136],0x0"),
  0xCCEFA:("cmp","ebx,0x9"),
  0xCCEFF:("cmp","ebx,0x1a"),
  0xCCF04:("cmp","ebx,0x1b"),
  0xCCF09:("cmp","ebx,0x2a"),
  0xCCF0E:("cmp","ebx,0x2f"),
  0xCCF13:("cmp","ebx,0x8"),
  0xCCF18:("cmp","ebx,0x28"),
  0xCCF1D:("cmp","ebx,0x29"),
  0xCCF25:("inc","dword ptr [ebp-0x8]"),
  0xCCF28:("mov","byte ptr [edx+ebp*1-0x44],bl"),
  0xCCF2C:("test","ebx,ebx"),
  0xCCF30:("mov","edx,dword ptr [ebp-0x8]"),
  0xCCF33:("movsx","edi,word ptr [ecx+0x130]"),
  0xCCF3A:("movsx","ebx,word ptr [ecx+0x132]"),
  0xCCF49:("cmp","word ptr [ecx+0x125],0x0"),
  0xCCF56:("cmp","byte ptr [ecx+0xa],0x1"),
  0xCD009:("mov","eax,dword ptr [ebp-0x4]"),
  0xCD00C:("call","0x1147a0"),
  0xCD011:("lea","ebx,[eax-0x1]"),
  0xCD014:("cmp","ebx,dword ptr [ebp-0x8]"),
  0xCD07B:("dec","word ptr [ecx+0x130]"),
  0xCD082:("mov","byte ptr [esi+0x41],0x1"),
  0xCD086:("inc","word ptr [esi+0x8]"),
  0xCD0CB:("dec","word ptr [ecx+0x132]"),
  0xCD0D2:("mov","byte ptr [esi+0x41],0x1"),
  0xCD0D6:("inc","word ptr [esi+0xa]"),
  0xCD102:("inc","word ptr [esi+0xc]"),
  0xCD106:("dec","byte ptr [ecx+0xa]"),
  0xCD130:("mov","eax,0x1"),
  0xCD135:("mov","byte ptr [esi+0x41],0x1"),
  # Newly recovered branch-selected colony, event and player-stat writes.
  0xCD0EC:("mov","ax,word ptr [ecx+0x125]"),
  0xCD0F3:("mov","word ptr [esi+0x43],ax"),
  0xCD0F7:("mov","word ptr [ecx+0x125],0x0"),
  0xCD1C4:("movzx","eax,byte ptr [ebx+0xa]"),
  0xCD1CB:("mov","eax,dword ptr [ebx+eax*4+0xc]"),
  0xCD1CF:("mov","dword ptr [ebx+ecx*4+0xc],eax"),
  0xCD1D3:("movsx","eax,byte ptr [ebx]"),
  0xCD1D6:("imul","eax,eax,0xea9"),
  0xCD1DC:("mov","ebx,dword ptr ds:0x1ff98"),
  0xCD1E4:("movsx","eax,byte ptr [edx]"),
  0xCD1E7:("inc","word ptr [ebx+eax*2+0x6ff]"),
  0xCD115:("movsx","ebx,byte ptr [ecx]"),
  0xCD118:("imul","ebx,ebx,0xea9"),
  0xCD11E:("mov","eax,ds:0x1ff98"),
  0xCD125:("movsx","eax,byte ptr [esi]"),
  0xCD128:("inc","word ptr [ebx+eax*2+0x6ff]"),
  0xCCFBE:("movsx","eax,byte ptr [ecx]"),
  0xCCFC1:("imul","eax,eax,0xea9"),
  0xCCFC7:("mov","ebx,dword ptr ds:0x1ff98"),
  0xCCFCF:("movsx","eax,byte ptr [esi]"),
  0xCCFD2:("add","word ptr [ebx+eax*2+0x6ff],0xa"),
  0xCD2AA:("movsx","ebx,byte ptr [ebx]"),
  0xCD2AD:("imul","ebx,ebx,0xea9"),
  0xCD2B3:("mov","eax,ds:0x1ff98"),
  0xCD2B8:("movsx","edx,byte ptr [edx]"),
  0xCD2BD:("add","word ptr [eax+edx*2+0x6ff],0xa"),
  0xCD279:("inc","word ptr [edx+0x3f]"),
  0xCD297:("mov","byte ptr [ebx+0xa],cl"),
  SHARED_OFFSET:("leave",""),
  0xCCEB8:("pop","edi"),
  0xCCEB9:("pop","esi"),
  0xCCEBA:("pop","ecx"),
  0xCCEBB:("pop","ebx"),
  0xCCEBC:("ret",""),
}
def rows(name):
    with (ROOT/"decompilation"/name).open(newline="") as fp:
        return list(csv.DictReader(fp))
def ins(code,off):
    run=subprocess.run(["objdump","-D","-M","intel","-b","binary","-m","i386",
        f"--start-address=0x{off:x}",f"--stop-address=0x{off+15:x}",str(code)],
        capture_output=True,text=True,check=True).stdout
    for line in run.splitlines():
        m=RX.match(line)
        if m and int(m[1],16)==off:
            return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"No original instruction at {off:#x}")
def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=SHA:
        raise ValueError("Original executable identity differs")
    b=code.read_bytes()
    if len(b)!=1410709:
        raise ValueError("Original unrelocated LE CODE object differs")
    fs={r["name"]:r for r in rows("functions.csv")}
    checked=[]
    for name,at,length,expected in SPECS:
        row=fs[name]
        if int(row["offset"])!=at or int(row["inferred_size"])!=length:
            raise ValueError(f"Original Watcom symbol extent changed: {name}")
        actual=hashlib.sha256(b[at:at+length]).hexdigest()
        if actual!=expected:
            raise ValueError(f"Original {name} bytes mismatch")
        checked.append({"name":name,"CODE_offset":hex(at),
                        "size_bytes":length,"original_bytes_sha256":actual})
    if hashlib.sha256(b[SHARED_OFFSET:SHARED_OFFSET+SHARED_BYTES]).hexdigest()!=SHARED_SHA:
        raise ValueError("Biological resolver shared epilogue original bytes changed")
    for name,offset in [
        ("Destroy_Colony_",0xCCDac),
        ("Random_",0x1147a0),
        ("Resolve_Bomb_Hit_",0xccebd),
        ("Resolve_Biological_Hit_",0xcd13e)
    ]:
        if int(fs[name]["offset"])!=offset:
            raise ValueError(f"Named helper changed: {name}")
    globals={r["name"]:int(r["offset"]) for r in rows("symbols.csv")
             if r["segment"]=="2"}
    for name,expected in [("_colony",0x1ab18),("_player",0x1ff98)]:
        if globals.get(name)!=expected:
            raise ValueError(f"Original DATA global differs: {name}")
    for at,expected in OPS.items():
        got=ins(code,at)
        if got!=expected:
            raise ValueError(f"Original CODE opcode at {at:#x}: {got} != {expected}")
    return {
        "original_sha256":SHA,
        "original_named_resolver_bodies":checked,
        "total_original_named_resolver_bytes":sum(c["size_bytes"] for c in checked),
        "original_instruction_anchors":len(OPS),
        "biological_shared_6_byte_epilogue":{"CODE_offset":hex(SHARED_OFFSET),
                                            "source_sha256":SHARED_SHA,
                                            "located_in_Watcom_symbol":"Destroy_Colony_"},
        "original_colony_record_stride":361,
        "biological_target_loop":{
            "entry_count_byte":"colony+0x0a",
            "array_base":"colony+0x0c, DWORD per entry",
            "scan":"reverse from count-1 to 0",
            "skip":"original DWORD low nibble == 8",
            "selection":"reservoir: for each eligible, ++EDI and call Random_(EDI), pick current index if result==1",
            "no_candidate":"original JL at 0xcd185 branches to external shared 0xcceb7 epilogue",
        },
        "bomb_eligibility_loop":{
            "scan":"49 original positions index48 down to index0",
            "byte_flag":"colony+0x136+index nonzero",
            "excluded_indices":[8,9,26,27,40,41,42,47],
            "eligible_indices":"recorded in local byte array in descending order",
            "subsequent_random_draw":"original Random_(total eligible plus other colony defenses/populations)",
        },
        "source_mutations":"Selected original population and combat-result writes, owner-indexed 16-bit player-stat +1/+10, and packed population removal now have independent bounded C implementations; full hit resolver decision trees and all side effects remain incomplete",
        "reconstructed_bounded_mutation_primitives":{
            "derived_colony_population_counter_words":["0x130","0x132"],
            "derived_result_event_counter_words":["0x08","0x0a","0x0c","0x3f"],
            "status_transfer":"colony word+0x125 -> event word+0x43, then clear colony word",
            "packed_population_remove":"decrement colony byte+0x0a and copy last population DWORD to selected slot+0x0c+4*index",
            "defense_decrement":"when original signed defense word >100, subtract 100 from colony+0xb4+2*index",
            "player_stat_source":"signed colony[0]*0xea9 + signed event[0]*2 + 0x6ff within original _player record, +1 or +10 branch effects"
        },
        "scope":"two fully hashed resolver CODE bodies and selected branch sites, original target-selection semantics only; not all resolver side effects, dynamic DOS equivalence or gameplay completeness"
    }
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",type=Path,required=True)
    p.add_argument("--code",type=Path,required=True)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    r=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))

#!/usr/bin/env python3
"""Authenticate the five original Watcom v1.31 RNG lifecycle helpers.

These functions are separate from original Random_ (audited separately).
Checks complete original source-body hashes, named Watcom callees and
exact opcode anchors. Derived C uses host callbacks for time_ and
Check_Release_Version_ and does not claim original DOS side effects.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
FUNCS=[
 ("Set_Game_Random_Seed_",0x7CA,28,
  "78221b4c36c0fadda05bcd58cad26c254c8b57f8efdaaca6de48422b85fdb6c7"),
 ("Random_With_Restore_",0x69F05,33,
  "9094bc56611b32c4d41cecc48f2ba4663d436a4e7c3745600971f8e059e1d3b5"),
 ("Set_Random_Seed_",0x114820,44,
  "30b232c9ddb480d5a2ae8b1b088f06567ba42c956ef8eba42c01a8899aa2f737"),
 ("Get_Random_Seed_",0x11484C,44,
  "38cab2251e3dcf251aa7560e1542f897226dd227fa9b98a4005a84f218cbd20f"),
 ("Randomize_",0x114878,51,
  "5e02b0cac9c1f45efc31fea015101057deb5a3b6add12a713e0881432b541f1d"),
]
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
OPS={
   0x7CA:("call","0x100b5c"),   # Check_Release_Version_
   0x7CF:("cmp","dword ptr ds:0x1b27c,0x0"), # _cmd_line_seed
   0x7D6:("je","0x114878"),    # Randomize_
   0x7DC:("mov","eax,ds:0x1b27c"),
   0x7E1:("jmp","0x114820"),  # Set_Random_Seed_
   0x69F09:("call","0x11484c"), # get
   0x69F12:("call","0x1147a0"), # random
   0x69F1B:("call","0x114820"), # restore
   0x69F20:("movsx","eax,bx"),
   0x11483E:("mov","ds:0x41e34,eax"),
   0x114864:("mov","eax,ds:0x41e34"),
   0x114890:("xor","eax,eax"),
   0x114892:("call","0x12c905"), # time_
   0x11489D:("call","0x114820"), # set
}

def csv_rows(path):
    with (ROOT/"decompilation"/path).open(newline="") as f:
        return list(csv.DictReader(f))

def instruction(code,addr):
    p=subprocess.run(["objdump","-D","-M","intel","-b","binary","-m","i386",
         f"--start-address=0x{addr:x}",f"--stop-address=0x{addr+15:x}",str(code)],
         capture_output=True,text=True,check=True)
    for line in p.stdout.splitlines():
        m=RX.match(line)
        if m and int(m[1],16)==addr:
            return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"Missing original Watcom instruction {addr:#x}")

def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=SHA:
        raise ValueError("Source executable checksum differs")
    b=code.read_bytes()
    if len(b)!=1410709:raise ValueError("Original CODE object size differs")
    fs={r["name"]:r for r in csv_rows("functions.csv")}
    checked=[]
    for name,at,size,digest in FUNCS:
        f=fs[name]
        if int(f["offset"])!=at or int(f["inferred_size"])!=size:
            raise ValueError(f"Watcom named function size differs: {name}")
        actual=hashlib.sha256(b[at:at+size]).hexdigest()
        if actual!=digest:
            raise ValueError(f"Original bytes differ: {name}")
        checked.append({"name":name,"original_code_offset":hex(at),
                        "size_bytes":size,"source_bytes_sha256":actual})
    for name,at in [
        ("Check_Release_Version_",0x100B5C),
        ("Random_",0x1147A0),
        ("time_",0x12C905)
    ]:
        if int(fs[name]["offset"])!=at:
            raise ValueError(f"Original callee identity differs: {name}")
    globals={r["name"]:int(r["offset"]) for r in csv_rows("symbols.csv")
             if r["segment"]=="2"}
    if globals.get("_random_seed")!=0x41E34 or globals.get("_cmd_line_seed")!=0x1B27C:
        raise ValueError("Original random or command-line seed DATA globals differ")
    for addr,expected in OPS.items():
        actual=instruction(code,addr)
        if actual!=expected:
            raise ValueError(f"Original opcode differs at {addr:#x}: {actual} != {expected}")
    return {
        "original_sha256":SHA,
        "verified_named_function_count":len(checked),
        "complete_original_body_bytes_verified":sum(r["size_bytes"] for r in checked),
        "selected_original_instruction_anchors":len(OPS),
        "original_seed_symbol":"_random_seed",
        "original_seed_data_offset":"0x41e34",
        "original_command_line_seed_symbol":"_cmd_line_seed",
        "original_cmd_line_seed_data_offset":"0x1b27c",
        "set_game_seed_logic":"call Check_Release_Version_; if _cmd_line_seed==0 tail-jump Randomize_, otherwise tail-jump Set_Random_Seed_ with EAX=command_line_seed",
        "randomize_logic":"call time_(NULL) then Set_Random_Seed_(time_result)",
        "random_with_restore_logic":"save current seed; Random_(maximum); restore saved seed; MOVSX EAX,BX (signed low16 of random result)",
        "scope":"fully verified source function-body bytes for five small seed helpers; time_/preflight side effects and full DOS runtime are not reimplemented",
        "functions":checked
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",type=Path,required=True)
    p.add_argument("--code",type=Path,required=True)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    result=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

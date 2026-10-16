#!/usr/bin/env python3
"""Join original v1.31 switch-target evidence into a CFG-consumable inventory.

Legacy Watcom table export + independently audited omitted CS SIB/prescaled
dispatch reports. Every case target is re-read from the authentic original
unrelocated CODE. No speculative jump-table or dynamic-game inference.
"""
import argparse,csv,hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"decompilation"
EXE_HASH="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_HASH="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
OUT=D/"switch_targets_reconciled.csv"
MAN=D/"switch_targets_reconciled.json"

def readcsv(filename):
    with (D/filename).open(newline="") as f:return list(csv.DictReader(f))
def sha(b):return hashlib.sha256(b).hexdigest()
def load(name):return json.loads((D/"reports"/name).read_text())
def source_target(blob,table,index):
    start=table+4*index
    if not 0<=start<len(blob)-3:raise ValueError("Original source table out of CODE image")
    return int.from_bytes(blob[start:start+4],"little")
def audit(exe,code):
    original=code.read_bytes()
    if len(original)!=1410709 or sha(original)!=CODE_HASH or sha(exe.read_bytes())!=EXE_HASH:
        raise ValueError("Official original v1.31 DOS EXE/CODE identity mismatch")
    existing=readcsv("switch_tables.csv")
    legacy_cases=readcsv("switch_targets.csv")
    by_site={}
    for x in legacy_cases:
        site=int(x["site_hex"],16);idx=int(x["case_index"]);target=int(x["target_offset"])
        if idx in by_site.setdefault(site,{}):raise ValueError("Duplicate legacy table case")
        by_site[site][idx]=target
    if len(existing)!=135 or len(legacy_cases)!=1080:raise ValueError("Legacy original switch inventory changed")
    rows=[];meta=[];seen=set()
    def append(site,table,targets,kind):
        if site in seen:raise ValueError("Duplicated original indirect JMP site")
        if not 0<=site<len(original):raise ValueError("Original source jump site outside CODE")
        if not targets:raise ValueError("Empty original table")
        for i,t in enumerate(targets):
            if source_target(original,table,i)!=t or not 0<=t<len(original):
                raise ValueError(f"Original switch table bytes mismatch {site:#x} case {i}")
            rows.append({"site_hex":hex(site),"case_index":i,"target_offset":t,"target_hex":hex(t),"source":kind})
        meta.append({"site_offset":hex(site),"table_offset":hex(table),
                     "case_count":len(targets),"distinct_targets":len(set(targets)),"source":kind})
        seen.add(site)
    for entry in existing:
        site=int(entry["site_offset"])
        tab=int(entry["table_offset"])
        n=int(entry["entry_count"])
        indexed=by_site.get(site)
        if indexed is None or set(indexed)!=set(range(n)):
            raise ValueError("Legacy case-order mapping incomplete")
        append(site,tab,[indexed[i] for i in range(n)],"legacy_verified")
    extra=load("omitted_game_switches_v131_2026-10-13.json")
    prescaled=load("omitted_prescaled_dispatches_v131_2026-10-13.json")
    if extra["source_sha256"]!=EXE_HASH or prescaled["source_sha256"]!=EXE_HASH:
        raise ValueError("Omitted original switch report provenance changed")
    for v in extra["additional_switches"]:
        if v["watcom_module_index"]>=133:raise ValueError("Expected game-only source dispatch")
        append(int(v["site_offset"],16),int(v["original_code_table_offset"],16),
               [int(k,16) for k in v["original_case_target_offsets"]],"omitted_game_verified")
        if len(v["original_case_target_offsets"])!=v["case_count"]:
            raise ValueError("Game switch source case count mismatch")
    for v in prescaled["sites"]:
        append(int(v["site_offset"],16),int(v["original_table_offset"],16),
               [int(k,16) for k in v["target_offsets"]],"prescaled_verified")
        if len(v["target_offsets"])!=v["case_count"]:
            raise ValueError("Prescaled original table case count mismatch")
    if (len(seen),len(rows))!=(205,1625):
        raise ValueError("Expected 205 site / 1,625 case authenticated union")
    hist={kind:sum(x["source"]==kind for x in meta)
          for kind in ("legacy_verified","omitted_game_verified","prescaled_verified")}
    if hist!={"legacy_verified":135,"omitted_game_verified":68,"prescaled_verified":2}:
        raise ValueError("Case provenance cardinality mismatch")
    rows.sort(key=lambda r:(int(r["site_hex"],16),r["case_index"]))
    report={"status":"reconciled-source-authenticated-original-v131-switch-sites",
      "original_EXE_SHA256":EXE_HASH,"original_CODE_SHA256":CODE_HASH,
      "legacy_source_site_count":135,"additional_verified_game_sites":68,
      "additional_verified_prescaled_sites":2,"merged_site_count":len(seen),
      "verified_original_case_entries":len(rows),
      "unique_case_destination_addresses":len(set(x["target_offset"] for x in rows)),
      "table_source_counts":hist,"site_provenance":meta,
      "scope":"Only the union of three independently original-byte authenticated switch reports. Not an exhaustive set of all indirect jumps or C-level semantics."}
    return rows,report

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exe",type=Path,required=True)
    ap.add_argument("--code",type=Path,required=True)
    ap.add_argument("--output",type=Path,default=OUT)
    ap.add_argument("--manifest",type=Path,default=MAN)
    args=ap.parse_args()
    rows,report=audit(args.exe,args.code)
    with args.output.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["site_hex","case_index","target_offset","target_hex","source"])
        w.writeheader();w.writerows(rows)
    args.manifest.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="site_provenance"},indent=2))
if __name__=="__main__":main()

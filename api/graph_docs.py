#!/usr/bin/env python3
# graph_docs.py

import json
import pandas as pd
import networkx as nx
from pathlib import Path

def main():
    BASE      = Path(__file__).parent
    merged    = pd.read_parquet(BASE/"merged.parquet")
    pop_long  = pd.read_parquet(BASE/"pop_long.parquet")

    G = nx.Graph()

    # 1) Add building nodes & edges to district
    for _, r in merged.iterrows():
        bnode = f"building_{r['PNU']}"
        G.add_node(bnode, 
                   type="building", 
                   name=r["name"], 
                   addr=r["addr"],
                   month=int(r["사용년월"]), 
                   kwh=int(r["kwh"]))
        code = r["시군구코드"]
        if pd.notna(code):
            dcode = int(code)
            dnode = f"district_{dcode}"
            G.add_node(dnode, type="district", code=dcode)
            G.add_edge(bnode, dnode)

    # 2) Aggregate per‐district total kWh & population
    for dnode, data in list(G.nodes(data=True)):
        if data.get("type") != "district":
            continue
        code = data["code"]
        df   = merged[merged["시군구코드"] == code]
        for ms, sub in df.groupby("사용년월"):
            total = int(sub["kwh"].sum())
            ms_str = str(ms)
            pop_series = pop_long[
                (pop_long["시군구코드"] == code) &
                (pop_long["period"]     == ms_str)
            ]["population"]
            pop = int(pop_series.iloc[0]) if not pop_series.empty else None
            # attach stats
            G.nodes[dnode].setdefault("energy", {})[int(ms_str)]     = total
            G.nodes[dnode].setdefault("population", {})[int(ms_str)] = pop

    # 3) Serialize each node as a tiny text doc
    docs_out = BASE / "docs.jsonl"
    with open(docs_out, "w", encoding="utf-8") as f:
        for node, data in G.nodes(data=True):
            if data["type"] == "building":
                text = (
                    f"PNU: {node.split('_',1)[1]}\n"
                    f"Building: {data['name']}\n"
                    f"Address: {data['addr']}\n"
                    f"Month: {data['month']}\n"
                    f"Energy (kWh): {data['kwh']}"
                )
                # link back to district
                for nbr in G.neighbors(node):
                    if G.nodes[nbr]["type"] == "district":
                        text += f"\nDistrict code: {G.nodes[nbr]['code']}"
                meta = {"node": node, **data}

            else:  # district
                for ms, total in data.get("energy", {}).items():
                    pop = data["population"].get(ms)
                    text = (
                        f"District code: {data['code']}\n"
                        f"Month: {ms}\n"
                        f"Total energy (kWh): {total}\n"
                        f"Population: {pop}"
                    )
                    builds = []
                    for b in G.neighbors(node):
                        nm   = G.nodes[b].get("name") or G.nodes[b].get("addr")
                        if isinstance(nm, str):
                            builds.append(nm)
                    if builds:
                        text += "\nBuildings: " + ", ".join(builds[:5])
                    meta = {"node": node, "code": data['code'], "period": ms}

                    f.write(json.dumps({"text": text, "metadata": meta}, ensure_ascii=False) + "\n")
                continue

            f.write(json.dumps({"text": text, "metadata": meta}, ensure_ascii=False) + "\n")

    print(f"Wrote node‐documents to {docs_out}")

if __name__ == "__main__":
    main()

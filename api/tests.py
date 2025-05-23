#!/usr/bin/env python3
"""
tests.py – smoke-tests for the FastAPI backend.
Run *after* uvicorn is up.
"""
import requests, sys, json, textwrap

BASE = "http://localhost:8000"

cases = [
    ("Which district had the highest per capita energy usage in July 2023?",
     lambda a: "kWh" in a),
    ("List the top 3 buildings that used more than 10000 kWh in March 2023",
     lambda a: a.count("\n") <= 6),        # header + 5 rows
]

def run():
    ok = 0
    for q, check in cases:
        r = requests.get(f"{BASE}/qa", params={"q": q}, timeout=120) # When you switch to OpenAI later timeout=15
        assert r.status_code == 200, f"HTTP {r.status_code}"
        ans = r.json()["answer"]
        passed = check(ans)
        status = "✅" if passed else "❌"
        # print(f"{status}  {q}\n{ textwrap.shorten(ans, 100) }\n")
        print(f"{status}  {q}\n{ans}\n")
        ok += passed
    print(f"{ok}/{len(cases)} tests passed.")
    sys.exit(0 if ok == len(cases) else 1)

if __name__ == "__main__":
    run()

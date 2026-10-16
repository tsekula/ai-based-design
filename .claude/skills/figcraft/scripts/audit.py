#!/usr/bin/env python3
"""Compliance gate for a saved .figcraft file.

usage: python3 -I audit.py FILE.figcraft ROOT_NODE_ID [ROOT_NODE_ID ...]

A layer passes when every visual property is bound to a variable or style:
  fill / stroke colour, stroke weight, corner radius, gap, padding, effects, text style + colour.
Colour variables must come from a semantic collection (not the Primitives tier).
Geometry (x/y/width/height/rotation) is exempt.
"""
import json, sys, zipfile

path, roots = sys.argv[1], sys.argv[2:]
doc = json.loads(zipfile.ZipFile(path).read("document.json"))
nodes = doc["nodes"]
colls = {c["id"]: c["name"] for c in doc["variables"]["collections"]}
var_coll = {v["id"]: colls[v["collection"]] for v in doc["variables"]["variables"]}
var_type = {v["id"]: v["resolvedType"] for v in doc["variables"]["variables"]}
PRIMITIVES = "Primitives"

violations, seen, instances = [], 0, 0


def path_of(n):
    out = []
    while n and n["id"] not in map(int, roots):
        out.append(n.get("name", "?"))
        n = nodes.get(str(n.get("parent")))
    return " > ".join(reversed(out)) or "(root)"


def solid(paints):
    return [p for p in (paints or []) if p.get("visible", True) and p.get("type") == "solid"]


def check(n):
    global seen, instances
    t, b, st = n["type"], n.get("bound") or {}, n.get("styles") or {}
    if t in ("group", "slice"):
        return
    seen += 1
    if t == "instance":
        instances += 1
    bad = lambda m: violations.append((path_of(n), m))

    if solid(n.get("fills")):
        k = [x for x in b if x == "fill" or x.startswith("fills/")]
        if not k and not st.get("fill"):
            bad("hard-coded fill")
        for x in k:
            if var_coll.get(b[x]) == PRIMITIVES:
                bad("fill bound to a primitive, not a semantic variable")
    if solid(n.get("strokes")):
        if not any(x == "stroke" or x.startswith("strokes/") for x in b) and not st.get("stroke"):
            bad("hard-coded stroke colour")
        if "strokeWeight" not in b:
            bad("hard-coded stroke weight")
    radii = (n.get("corners") or {}).get("radii") or []
    if any(r > 0 for r in radii) and "cornerRadius" not in b:
        bad("hard-coded corner radius")
    if n.get("effects") and not st.get("effect"):
        bad("effect not from an effect style")
    lay = n.get("layout")
    if lay and lay.get("mode") in ("horizontal", "vertical", "grid"):
        if lay.get("gap", 0) > 0 and "gap" not in b:
            bad("hard-coded gap")
        pad = lay.get("padding") or [0, 0, 0, 0]
        if (pad[1] or pad[3]) and "paddingHorizontal" not in b:
            bad("hard-coded horizontal padding")
        if (pad[0] or pad[2]) and "paddingVertical" not in b:
            bad("hard-coded vertical padding")
    if t == "text":
        sid = (n.get("style") or {}).get("style_id")
        if not st.get("text") or sid != st.get("text"):
            bad("text without a single text style")
        if not any(x.startswith("fills/") for x in b):
            bad("hard-coded text colour")


def walk(i):
    n = nodes[str(i)]
    check(n)
    for c in n.get("children") or []:
        walk(c)


for r in roots:
    walk(int(r))

top = [nodes[str(c)] for c in nodes[roots[0]].get("children", [])]
print(json.dumps({
    "pass": not violations,
    "layersChecked": seen,
    "violations": len(violations),
    "details": [{"path": p, "issue": m} for p, m in violations[:40]],
    "componentBacked": f"{sum(c['type']=='instance' for c in top)}/{len(top)} top-level layers are instances",
}, indent=2))
sys.exit(1 if violations else 0)

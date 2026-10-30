"""Small ink trees drawn as tapered wood, needles, and loose leaf strokes.

All geometry is vector-native and deterministic. The public tree() signature
matches the landscape renderer; each tree sways around its grounded origin.
"""
import math
import random
import xml.etree.ElementTree as ET

NS = "http://www.w3.org/2000/svg"
from palette import TREE, FINE, BG


def _add(parent, tag, attrs):
    return ET.SubElement(parent, f"{{{NS}}}{tag}",
                         {key: str(value) for key, value in attrs.items()})


def _points(points):
    return " ".join(f"{x:.3f},{y:.3f}" for x, y in points)


def _curve(a, b, c, d, steps=10):
    result = []
    for i in range(steps + 1):
        t = i / steps
        s = 1 - t
        result.append((s**3*a[0]+3*s*s*t*b[0]+3*s*t*t*c[0]+t**3*d[0],
                       s**3*a[1]+3*s*s*t*b[1]+3*s*t*t*c[1]+t**3*d[1]))
    return result


def _brush(parent, points, width, opacity=.62, color=TREE, taper="branch"):
    """An irregular pressure envelope around a curved brush centerline."""
    if len(points) < 2:
        return
    left, right = [], []
    for i, (x, y) in enumerate(points):
        before, after = points[max(0, i-1)], points[min(len(points)-1, i+1)]
        dx, dy = after[0]-before[0], after[1]-before[1]
        length = math.hypot(dx, dy) or 1
        t = i / (len(points)-1)
        if taper == "leaf":
            pressure = math.sin(math.pi*t)**.72
        else:
            pressure = (1-t)**.85 * (.88+.12*math.sin(t*8.3+1))
        w = max(.012, width*pressure)
        # Unequal sides keep branches from looking like machine-cut ribbons.
        left.append((x-dy/length*w, y+dx/length*w))
        right.append((x+dy/length*w*.76, y-dx/length*w*.76))
    _add(parent, "polygon", {"points": _points(left+right[::-1]),
                              "fill": color, "opacity": f"{opacity:.3f}"})


def _leaf(parent, base, tip, width, rng, opacity=.57):
    dx, dy = tip[0]-base[0], tip[1]-base[1]
    bend = rng.uniform(-.25, .25)
    line = _curve(base, (base[0]+dx*.3-dy*bend, base[1]+dy*.3+dx*bend),
                  (base[0]+dx*.8, base[1]+dy*.75), tip, 5)
    _brush(parent, line, width, opacity, taper="leaf")


def tree(parent, x, y, height, kind, seed):
    """Draw an airy pine, a windswept broadleaf, or a river willow."""
    rng = random.Random(seed)
    h = max(1., float(height))
    kind = int(kind) % 3
    unit = h/40
    anchor = _add(parent, "g", {"transform": f"translate({x:.3f} {y:.3f})",
                                  "data-tree-kind": ("pine", "broadleaf", "willow")[kind]})
    sway = _add(anchor, "g", {"class": "tree-sway",
              "style": f"animation-duration:{rng.choice((9,12,15,18))}s;animation-delay:-{rng.uniform(0,15):.2f}s"})
    direction = rng.choice((-1, 1))
    lean = direction*h*rng.uniform(.08, .22)
    # A small opposing bend at the roots makes the canopy's lean believable.
    bend = -direction*h*rng.uniform(.025, .065)
    trunk = _curve((0, 0), (bend, -h*.27), (lean*.86, -h*.65), (lean, -h), 16)

    def stem(t):
        index = t*(len(trunk)-1)
        lo = min(len(trunk)-2, int(index))
        blend = index-lo
        return (trunk[lo][0]*(1-blend)+trunk[lo+1][0]*blend,
                trunk[lo][1]*(1-blend)+trunk[lo+1][1]*blend)

    # Short splayed roots and a split ink edge ground the tree to its bank.
    for side in (-1, 1):
        _brush(sway, _curve((side*.3*unit, -h*.14), (side*.3*unit, -h*.035),
                           (side*2.1*unit, -.3*unit), (side*rng.uniform(3, 4.6)*unit, .5*unit), 7),
               .72*unit, .52, FINE)
    _brush(sway, trunk, 1.05*unit, .73, FINE)
    _brush(sway, [(px-.22*unit, py) for px, py in trunk], .55*unit, .77)
    # One interrupted dark fissure leaves the trunk looking dry and fibrous.
    _brush(sway, trunk[2:10], .16*unit, .57, BG)

    if kind == 0:
        # Alternating long and short boughs leave open windows in the crown.
        levels = (.29, .44, .59, .73, .86)
        for j, level in enumerate(levels):
            at = stem(level)
            primary = direction if j % 2 == 0 else -direction
            for side, weight in ((primary, 1.), (-primary, rng.uniform(.42, .72))):
                extent = h*(.26*(1-level)**.4)*weight*rng.uniform(.87, 1.15)
                end = (at[0]+side*extent, at[1]-h*rng.uniform(.015, .06))
                bough = _curve(at, (at[0]+side*extent*.25, at[1]+h*.035),
                               (end[0]-side*extent*.2, end[1]+h*.015), end, 9)
                _brush(sway, bough, (.44-.15*level)*unit, .70)
                for k in (3, 6, 8):
                    bx, by = bough[k]
                    twig = (bx+side*h*rng.uniform(.025, .055), by-h*rng.uniform(.035, .065))
                    _brush(sway, _curve((bx, by), (bx, by-h*.02), twig, twig, 4), .20*unit, .56)
                    # Separated, uneven needle fans rather than filled triangles.
                    for needle in range(3):
                        angle = -math.pi/2 + side*(needle-.7)*.60+rng.uniform(-.18, .18)
                        length = h*rng.uniform(.04, .085)
                        tip = (twig[0]+math.cos(angle)*length, twig[1]+math.sin(angle)*length)
                        _leaf(sway, twig, tip, .32*unit, rng, rng.uniform(.45, .70))
        # A spare terminal spray breaks the otherwise regular tier rhythm.
        for side in (-1, 1):
            _leaf(sway, stem(.93), (lean+side*h*.04, -h*1.015), .26*unit, rng, .64)

    elif kind == 1:
        # Broadleaf crowns grow on angular forks, with wind opening the lee side.
        for j, level in enumerate((.36, .50, .63, .76, .87)):
            at = stem(level)
            side = direction if j % 3 != 1 else -direction
            spread = h*rng.uniform(.17, .26)*(1 if side==direction else .72)
            end = (at[0]+side*spread, at[1]-h*rng.uniform(.08, .17))
            branch = _curve(at, (at[0]+side*spread*.28, at[1]-h*.02),
                            (end[0]-side*spread*.18, end[1]+h*.08), end, 10)
            _brush(sway, branch, .43*unit*(1-level*.35), .71)
            for fork in (-1, 1):
                start = branch[6 if fork==-1 else 9]
                tip = (end[0]+fork*h*rng.uniform(.04, .095), end[1]-h*rng.uniform(.015, .065))
                _brush(sway, _curve(start, (start[0], start[1]-h*.03), tip, tip, 5), .20*unit, .53)
                # Individual dry-brush leaf strokes overlap lightly, retaining
                # gaps; there is no enclosing oval or solid canopy blob.
                for leaf in range(5):
                    bx = tip[0]+rng.uniform(-.045, .045)*h
                    by = tip[1]+rng.uniform(-.025, .025)*h
                    angle = -math.pi/2 + rng.uniform(-1.15, 1.15) + direction*.25
                    length = h*rng.uniform(.04, .085)
                    endleaf = (bx+math.cos(angle)*length, by+math.sin(angle)*length)
                    _leaf(sway, (bx, by), endleaf, rng.uniform(.40, .64)*unit, rng, rng.uniform(.45, .68))

    else:
        # The crown divides into arched branches; fronds hang independently.
        crown = stem(.80)
        for j in range(7):
            side = -1 if j < 3 else 1
            reach = h*(.105 + (j % 4)*.055)*rng.uniform(.9, 1.15)
            tip = (crown[0]+side*reach, -h*rng.uniform(.64, .78))
            arch = _curve(crown, (crown[0]+side*reach*.38, -h*1.02),
                          (tip[0], -h*.95), tip, 11)
            _brush(sway, arch, .35*unit, .65)
            for branchpoint in (7, 10):
                start = arch[branchpoint]
                end = (start[0]+direction*h*rng.uniform(.025, .07),
                       start[1]+h*rng.uniform(.25, .43))
                frond = _curve(start, (start[0]+direction*h*.015, start[1]+h*.13),
                               (end[0]-direction*h*.015, end[1]-h*.10), end, 10)
                _brush(sway, frond, .19*unit, .51)
                for k in (2, 5, 8):
                    base = frond[k]
                    sideleaf = -1 if (k+j) % 2 else 1
                    tip_leaf = (base[0]+sideleaf*h*rng.uniform(.02, .04),
                                base[1]+h*rng.uniform(.035, .065))
                    _leaf(sway, base, tip_leaf, .25*unit, rng, .55)
    return anchor

"""Shared ink mountain geometry for measured peaks and decorative depth.

Developed from the contour/brush techniques of Lingdong Huang's shan-shui-inf
(MIT). Foreground and background use the same faceted, asymmetric renderer.
"""
import math
import random
import xml.etree.ElementTree as ET

NS = "http://www.w3.org/2000/svg"
from palette import BG, INK, MOUNTAIN


def add(parent, tag, attrs):
    return ET.SubElement(parent, f"{{{NS}}}{tag}", {k: str(v) for k, v in attrs.items()})


def pts(points):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in points)


def noise(x, seed):
    return (.50 + .24 * math.sin(x * 1.71 + seed * 2.37)
            + .14 * math.sin(x * 4.27 - seed * .83)
            + .08 * math.sin(x * 9.31 + seed * 1.17))


def brush(parent, points, color=INK, width=.7, opacity=.3):
    left, right = [], []
    for i, (x, y) in enumerate(points):
        a, b = points[max(0, i - 1)], points[min(len(points) - 1, i + 1)]
        angle = math.atan2(b[1] - a[1], b[0] - a[0]) + math.pi / 2
        w = width * math.sin(math.pi * i / (len(points) - 1)) * (.65 + .35 * noise(i * .5, width))
        dx, dy = math.cos(angle) * w, math.sin(angle) * w
        left.append((x + dx, y + dy))
        right.append((x - dx, y - dy))
    add(parent, "polygon", {"points": pts(left + right[::-1]), "fill": color, "opacity": opacity})


def ridge(height, half, seed, base):
    rng = random.Random(seed)
    profiles = []
    for _ in range(2):
        slope = rng.uniform(1.1, 1.65)
        crags = []
        for lower, upper in [(.16, .34), (.37, .59), (.64, .83)]:
            if rng.random() < .85:
                crags.append((rng.uniform(lower, upper), rng.uniform(.055, .13), rng.uniform(.08, .23)))
        crags.append((rng.uniform(.22, .65), rng.uniform(.07, .15), -rng.uniform(.04, .13)))
        profiles.append((slope, crags))
    points = []
    for k in range(81):
        u = -1 + k / 40
        slope, crags = profiles[0 if u < 0 else 1]
        distance = abs(u)
        shape = (1 - distance) ** slope
        for position, width, amplitude in crags:
            shape += amplitude * max(0, 1 - abs(distance - position) / width)
        shape = max(0, min(1 - distance * .2, shape))
        rough = 1 - .12 * (1 - noise(k * .78, seed / 91 + .1)) * distance ** .4
        points.append((u * half, base - height * shape * rough))
    return points


def paint_mountain(defs, parent, identifier, height, half, seed, base=535, detail=1):
    """Paint a peak with an exact height; atmosphere belongs to the caller."""
    rim = ridge(height, half, seed, base)
    silhouette = rim + [(half, base + 3), (-half, base + 3)]
    clip = add(defs, "clipPath", {"id": identifier + "-clip"})
    add(clip, "polygon", {"points": pts(silhouette)})
    add(parent, "polygon", {"points": pts(silhouette), "fill": MOUNTAIN})
    add(parent, "polygon", {"points": pts(silhouette), "fill": "url(#mountain-wash)"})
    interior = add(parent, "g", {"clip-path": f"url(#{identifier}-clip)"})
    rng = random.Random(seed + 57)

    # Long rock planes read first; fine broken grain sits within them.
    fold = [(0, base - height), (.09 * half, base - height * .72),
            (-.02 * half, base - height * .47), (.24 * half, base - height * .2),
            (.4 * half, base + 4), (half, base + 4)]
    add(interior, "polygon", {"points": pts(fold), "fill": BG, "opacity": ".32"})
    brush(interior, fold[:5], INK, .9, .22)
    for sample in [19, 30, 53, 64]:
        x, top = min(rim[sample - 3:sample + 4], key=lambda point: point[1])
        direction = -1 if x < 0 else 1
        reach = base - top
        face = [(x, top), (x + direction * half * .025, top + reach * .28),
                (x + direction * half * .08, top + reach * .52),
                (x + direction * half * .16, base),
                (x + direction * half * .33, base)]
        add(interior, "polygon", {"points": pts(face), "fill": BG, "opacity": ".12"})
        brush(interior, face[:4], INK, .55, .20)

    for j in range(max(8, round(half * height / 850 * detail))):
        u = rng.uniform(-.94, .94)
        x = u * half
        top = rim[max(0, min(80, round((u + 1) * 40)))][1]
        start = top + rng.uniform(.03, .45) * (base - top)
        finish = min(base + 1, start + rng.uniform(.12, .55) * height)
        trace = []
        for k in range(9):
            t = k / 8
            trace.append((x + (noise(t * 5, j + seed) - .5) * (2 + height * .016)
                          + u * t * half * .12, start + t * (finish - start)))
        brush(interior, trace, INK if j % 4 else BG, rng.uniform(.35, .8), rng.uniform(.10, .22))

    # Broken strata follow the crags, with unequal offsets to avoid a mesh.
    for j, fraction in enumerate([.18, .29, .43, .61, .78]):
        contour = []
        for k, (x, y) in enumerate(rim):
            yy = base - (base - y) * fraction
            contour.append((x * (1.03 - fraction * .03), yy + math.sin(k * .3 + j) * min(2, height * .015)))
        for start, end in [(6 + j, 27 + j), (43 - j, 70 - j)]:
            brush(interior, contour[start:end], INK, .34, .10 + .035 * fraction)

    for _ in range(round((6 + height / 9) * detail)):
        x = rng.uniform(-half * .84, half * .84)
        y = base - rng.uniform(.04, .54) * height
        brush(interior, [(x, y), (x + 3, y - 1), (x + rng.uniform(5, 11), y + 1)],
              INK, rng.uniform(.3, .6), rng.uniform(.12, .25))
    brush(parent, rim, INK, .82, .82)
    return rim

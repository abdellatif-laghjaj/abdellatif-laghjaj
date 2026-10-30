"""Quiet native SVG weather and river life for the ink landscape.

build_ambient(defs, background_group, water_group) appends SVG elements to
the supplied ElementTree nodes and returns their CSS. No script, raster,
external resources, or browser-only generation is used in the output.
All cycles divide 180 seconds, the scene's common repeat interval.
"""
import random
import xml.etree.ElementTree as ET

NS = "http://www.w3.org/2000/svg"
from palette import FISH as INK, WATER, CLOUD

FISH_COUNT = 20
FISH_PERIOD = 60
FISH_INTERVAL = FISH_PERIOD / FISH_COUNT
FISH_FIRST_JUMP = 1.5


def _add(parent, tag, attrs=None, text=None):
    node = ET.SubElement(parent, f"{{{NS}}}{tag}",
                         {key: str(value) for key, value in (attrs or {}).items()})
    node.text = text
    return node


def _clouds(defs, background_group):
    cloud_fill = _add(defs, "linearGradient", {
        "id": "ambient-cloud-wash", "x1": "0", "y1": "0",
        "x2": "0", "y2": "1",
    })
    for offset, opacity in [
        ("0", "0"), (".22", ".10"), (".46", ".25"),
        (".72", ".12"), ("1", "0"),
    ]:
        _add(cloud_fill, "stop", {
            "offset": offset, "stop-color": CLOUD, "stop-opacity": opacity,
        })

    # Each cloud is built from separate brush deposits: a broad wash, a
    # broken lower wash, and dry, tapering ends. There is deliberately no
    # enclosing outline, symmetrical lens, or regular cloud scallop.
    clouds = _add(defs, "g", {"id": "ambient-cloud-tile"})
    for d, opacity in [
        ("M72 319 C126 309 158 321 201 314 C234 310 247 298 276 300 "
         "C302 301 311 307 341 304 C385 299 405 289 446 294 "
         "C473 297 497 304 529 301 C565 297 603 304 634 312 "
         "C591 307 571 317 537 314 C506 310 487 318 453 317 "
         "C411 313 402 325 366 320 C333 315 315 323 291 320 "
         "C258 316 244 329 206 324 C160 318 126 328 72 319Z", 1),
        ("M171 330 C207 320 238 330 269 325 C294 322 314 327 341 323 "
         "C372 318 388 330 421 325 C452 321 478 326 499 324 "
         "C470 334 450 329 428 333 C399 339 372 329 349 333 "
         "C320 338 298 330 272 334 C237 338 218 331 171 330Z", .68),
        ("M759 288 C795 281 813 288 834 281 C854 275 870 280 887 274 "
         "C909 268 932 273 949 275 C973 278 989 270 1013 279 "
         "C1034 286 1058 283 1088 290 C1050 287 1029 293 1002 289 "
         "C973 284 959 291 935 286 C910 281 895 289 874 285 "
         "C849 280 822 295 799 289 C784 286 771 288 759 288Z", .88),
        ("M842 298 C878 288 902 295 926 291 C949 287 966 296 997 292 "
         "C978 302 955 297 937 301 C906 303 887 298 842 298Z", .53),
    ]:
        _add(clouds, "path", {
            "d": d, "fill": "url(#ambient-cloud-wash)", "opacity": opacity,
        })
    for d, opacity in [
        ("M91 317 Q114 313 143 316 Q168 319 191 315", .15),
        ("M179 332 C204 326 224 333 244 329 M254 329 l17 -1", .18),
        ("M321 307 C345 307 364 299 388 301 M397 300 l10 -1", .14),
        ("M464 319 C487 315 505 321 525 317 M535 317 l13 -1", .16),
        ("M590 310 Q611 311 638 316 M645 317 l17 3", .12),
        ("M791 288 Q808 290 830 285 M838 284 l11 -1", .14),
        ("M925 291 Q949 286 971 291 M979 292 l13 -1", .17),
        ("M1051 288 Q1069 288 1091 292 M1098 293 l14 2", .10),
    ]:
        _add(clouds, "path", {
            "d": d, "fill": "none", "stroke": CLOUD,
            "stroke-width": ".55", "opacity": opacity,
            "stroke-linecap": "round",
        })
    cloud_lane = _add(background_group, "g", {
        "class": "ambient-motion ambient-clouds",
        "data-ambient-layer": "slow-clouds", "aria-hidden": "true",
    })
    for offset in [-1200, 0, 1200, 2400]:
        _add(cloud_lane, "use", {"href": "#ambient-cloud-tile", "x": offset})

    # A separate higher wisp moves at half the cloud-lane speed. Its repeat
    # interval is half as wide, so both lanes still meet at 180 seconds.
    high = _add(defs, "g", {"id": "ambient-high-wisp"})
    for d, opacity in [
        ("M44 279 C80 273 111 283 137 276 C161 270 183 280 213 274 "
         "C240 269 261 275 282 272 C308 267 325 273 353 270 "
         "C385 268 403 274 424 272 C452 270 470 277 509 279 "
         "C475 278 454 282 428 279 C401 277 383 283 358 279 "
         "C333 275 312 280 287 278 C258 276 242 283 217 279 "
         "C190 275 168 283 144 280 C109 276 85 283 44 279Z", .7),
        ("M213 284 C247 280 271 287 298 282 C324 278 343 287 375 282 "
         "C402 279 423 285 449 283 C419 290 399 285 377 288 "
         "C347 292 326 284 300 288 C270 291 248 285 213 284Z", .45),
    ]:
        _add(high, "path", {
            "d": d, "fill": "url(#ambient-cloud-wash)", "opacity": opacity,
        })
    _add(high, "path", {
        "d": "M66 278 Q91 278 109 280 M119 280 l12 -1 "
             "M246 283 Q267 286 286 283 M296 282 l13 -1 "
             "M446 277 Q466 277 487 280 M498 281 l15 1",
        "fill": "none", "stroke": CLOUD, "stroke-width": ".5",
        "stroke-linecap": "round", "opacity": ".15",
    })
    high_lane = _add(background_group, "g", {
        "class": "ambient-motion ambient-high-clouds",
        "data-ambient-layer": "high-clouds", "aria-hidden": "true",
    })
    for offset in [-600, 0, 600, 1200, 1800]:
        _add(high_lane, "use", {"href": "#ambient-high-wisp", "x": offset})


def _river(water_group):
    rng = random.Random(5602)
    ripples = _add(water_group, "g", {
        "data-ambient-layer": "moving-water", "aria-hidden": "true",
    })
    # Sparse families of tapered brush marks give depth without turning the
    # river into a grid of equal line segments. Broken echoes vary by cluster.
    for i in range(21):
        x = 54 + i * 51 + rng.uniform(-22, 22)
        y = rng.uniform(563, 610)
        depth = (y - 563) / 50
        length = rng.uniform(26, 69) + depth * 48
        thickness = .32 + depth * .48
        crest = rng.uniform(-1.4, -.4)
        period = 12 if depth < .35 else 9 if depth < .72 else 6
        anchored = _add(ripples, "g", {"transform": f"translate({x:.2f} {y:.2f})"})
        mark = _add(anchored, "g", {
            "class": "ambient-motion ambient-wave",
            "style": f"animation-duration:{period}s;animation-delay:-{(i * 1.37) % period:.2f}s",
        })
        _add(mark, "path", {
            "d": f"M0 0 C{length*.23:.2f} {crest:.2f} {length*.35:.2f} {crest:.2f} "
                 f"{length*.58:.2f} -.15 Q{length*.78:.2f} .45 {length:.2f} 0 "
                 f"Q{length*.77:.2f} {thickness:.2f} {length*.57:.2f} {thickness*.6:.2f} "
                 f"C{length*.34:.2f} {crest+thickness:.2f} {length*.2:.2f} -.05 0 0Z",
            "fill": WATER,
        })
        if i % 3 != 1:
            start, end = length * .21, length * rng.uniform(.56, .82)
            echo_y = rng.uniform(2, 3.1)
            _add(mark, "path", {
                "d": f"M{start:.2f} {echo_y:.2f} "
                     f"Q{(start+end)*.5:.2f} {echo_y-.55:.2f} {end:.2f} {echo_y+.1:.2f}",
                "fill": "none", "stroke": WATER, "stroke-width": ".4",
                "stroke-linecap": "round", "opacity": ".55",
            })
        if i % 4 == 0:
            _add(mark, "path", {
                "d": f"M{length+6:.2f} .1 l{rng.uniform(5,13):.2f} -.35",
                "fill": "none", "stroke": WATER, "stroke-width": ".45",
                "stroke-linecap": "round", "opacity": ".75",
            })


def _fish_marks(defs):
    """Share the fine brush shapes across every river position."""
    fish = _add(defs, "g", {"id": "ambient-fish-body"})
    _add(fish, "path", {
        "d": "M6 0 C3.2 -2.2 .2 -2.4 -2.8 -.6 "
             "L-5.7 -2.6 L-4.9 0 L-5.7 2.5 L-2.8 .6 "
             "C.1 2.2 3.4 1.8 6 0Z",
        "fill": INK,
    })
    _add(fish, "path", {
        "d": "M-.8 -1.2 L.4 -3.1 L2 -1.5 M.1 1.1 L-1 2.6 L2.1 1.3",
        "fill": INK, "opacity": ".7",
    })
    takeoff = _add(defs, "g", {"id": "ambient-fish-takeoff"})
    _add(takeoff, "path", {
        "d": "M-6 0 Q-2 -1.6 3 -.5 M-5 1 Q0 2 5 .5",
        "fill": "none", "stroke": WATER, "stroke-width": ".65",
        "stroke-linecap": "round",
    })
    splash = _add(defs, "g", {"id": "ambient-fish-landing"})
    _add(splash, "path", {
        "d": "M-9 0 C-7 -2.1 5 -2.7 9 -.1 M-8 .9 C-4 2.4 4 2.3 7 1 "
             "M-5 -.2 Q0 -1.3 4 -.3",
        "fill": "none", "stroke": INK, "stroke-width": ".6",
        "stroke-linecap": "round",
    })
    droplets = _add(defs, "g", {"id": "ambient-fish-droplets"})
    for d in ["M-3 -1 q-3 -2 -3.6 -4.5", "M1 -1 q0 -3 1 -5", "M4 0 q2 -1.4 3 -3"]:
        _add(droplets, "path", {
            "d": d, "fill": "none", "stroke": INK,
            "stroke-width": ".55", "stroke-linecap": "round",
        })


def _fish_locations():
    """Twenty spread-out locations, ordered to avoid nearby successive jumps.

    Stepping by seven visits every one of twenty horizontal slots before
    repeating. Jitter, river depth, direction, and size remain deterministic.
    Even the last-to-first transition crosses a substantial stretch of water.
    """
    rng = random.Random(9753)
    for index in range(FISH_COUNT):
        slot = (index * 7 + 13) % FISH_COUNT
        x = 145 + slot * (910 / (FISH_COUNT - 1)) + rng.uniform(-8, 8)
        y = 575 + ((index * 11) % 31) + rng.uniform(-1.8, 1.8)
        scale = max(.74, min(1, .75 + (y - 573) / 34 * .23 + rng.uniform(-.025, .025)))
        direction = -1 if index % 4 in (1, 2) else 1
        yield round(x, 2), round(y, 2), direction, round(scale, 3)


def _fish(water_group, x, y, direction, scale, index):
    # Negative phases place all jumps correctly in the very first cycle.
    # CSS uses a sixty-second clock; its two-percent flight still lasts 1.2s.
    phase = (FISH_PERIOD - index * FISH_INTERVAL) % FISH_PERIOD
    timing = f"animation-delay:-{phase:g}s"
    anchor = _add(water_group, "g", {
        "transform": f"translate({x} {y}) scale({direction*scale:g} {scale:g})",
        "aria-hidden": "true", "data-ambient-layer": "occasional-fish",
        "data-fish-index": index,
        "data-fish-start": FISH_FIRST_JUMP + index * FISH_INTERVAL,
    })
    for class_name, mark, landing in [
        ("ambient-fish", "ambient-fish-body", False),
        ("ambient-takeoff", "ambient-fish-takeoff", False),
        ("ambient-splash", "ambient-fish-landing", True),
        ("ambient-droplets", "ambient-fish-droplets", True),
    ]:
        parent = _add(anchor, "g", {"transform": "translate(48 0)"}) if landing else anchor
        animated = _add(parent, "g", {
            "class": f"ambient-motion {class_name}", "opacity": "0", "style": timing,
        })
        _add(animated, "use", {"href": f"#{mark}"})


def build_ambient(defs, background_group, water_group):
    """Append native SVG weather and river life, returning their CSS.

    The caller can crop/translate the scene: original local coordinates are
    preserved (clouds y265..345, river marks y563..613). Tiny fish jump one
    at a time every three seconds, visiting twenty positions per minute.
    Every flight takes 1.2 seconds. All motion repeats exactly at 180 seconds.
    """
    _clouds(defs, background_group)
    _river(water_group)
    _fish_marks(defs)
    for index, (x, y, direction, scale) in enumerate(_fish_locations()):
        _fish(water_group, x, y, direction, scale, index)
    return CSS


CSS = """
.ambient-clouds { animation: ambient-cloud-drift 180s linear infinite; }
.ambient-high-clouds { animation: ambient-high-drift 180s linear infinite; }
@keyframes ambient-cloud-drift {
  from { transform:translateX(0px); }
  to { transform:translateX(-1200px); }
}
@keyframes ambient-high-drift {
  from { transform:translateX(0px); }
  to { transform:translateX(-600px); }
}
.ambient-wave { opacity:.17; animation:ambient-water 12s ease-in-out infinite; }
@keyframes ambient-water {
  0%,100% { transform:translate(-8px,0px) scaleX(.84); opacity:.07; }
  50% { transform:translate(12px,-.35px) scaleX(1.08); opacity:.27; }
}
.ambient-fish { animation:ambient-fish-jump 60s linear infinite; }
@keyframes ambient-fish-jump {
  0%,2.495% { opacity:0; transform:translate(0px,0px) rotate(-55deg); }
  2.5% { opacity:0; transform:translate(0px,0px) rotate(-55deg); }
  2.625% { opacity:.7; transform:translate(3px,-11px) rotate(-49deg); }
  2.75% { opacity:.85; transform:translate(6px,-20px) rotate(-42deg); }
  3% { opacity:.85; transform:translate(12px,-35px) rotate(-28deg); }
  3.25% { opacity:.85; transform:translate(18px,-43px) rotate(-14deg); }
  3.5% { opacity:.85; transform:translate(24px,-46px) rotate(0deg); }
  3.75% { opacity:.85; transform:translate(30px,-43px) rotate(14deg); }
  4% { opacity:.85; transform:translate(36px,-35px) rotate(28deg); }
  4.25% { opacity:.8; transform:translate(42px,-20px) rotate(42deg); }
  4.45% { opacity:.3; transform:translate(47px,-4px) rotate(53deg); }
  4.5%,100% { opacity:0; transform:translate(48px,0px) rotate(55deg); }
}
.ambient-takeoff { animation:ambient-takeoff-ring 60s linear infinite; }
@keyframes ambient-takeoff-ring {
  0%,2.35% { opacity:0; transform:scale(.7); }
  2.5% { opacity:.24; transform:scale(.85); }
  2.85% { opacity:.15; transform:scale(1.25); }
  3.65%,100% { opacity:0; transform:scale(1.8); }
}
.ambient-splash { animation:ambient-landing 60s linear infinite; }
@keyframes ambient-landing {
  0%,4.45% { opacity:0; transform:scale(.5); }
  4.55% { opacity:.4; transform:scale(.65); }
  5.15% { opacity:.23; transform:scale(1.3); }
  6.5%,100% { opacity:0; transform:scale(2.5); }
}
.ambient-droplets { animation:ambient-droplet-fade 60s ease-out infinite; }
@keyframes ambient-droplet-fade {
  0%,4.45% { opacity:0; transform:translateY(0px); }
  4.55% { opacity:.45; transform:translateY(-1px); }
  5.15%,100% { opacity:0; transform:translateY(2px); }
}
@media(prefers-reduced-motion:reduce) {
  .ambient-motion { animation:none !important; }
  .ambient-fish,.ambient-takeoff,.ambient-splash,.ambient-droplets { opacity:0 !important; }
}
"""

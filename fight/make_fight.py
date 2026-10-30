#!/usr/bin/env python3
"""
make_fight4.py  ·  builds fight-light.svg and fight-dark.svg  (v4, 30 s loop)

Looks like a plain profile README. Isn't.

Everything is SMIL. No JavaScript, no CSS, no external fonts, so GitHub's
image proxy renders it as-is. Every word is its own <text> with a fixed
textLength, so single words can be kicked, sliced and used as trampolines
while the layout stays identical on every OS.

The copy opens like the mountjoy README (a struck-out "Dear Diary", then
"First of all, let me get something straight: This is a README, not a
diary.") Edit PARAS to change it. Words the fight uses by name: "called"
(kicked apart), "Ted." (the hole, and later the bear's home), "teddy" /
"Engineering" / "README," (sliced).

ANIMATION TOOLKIT
  anticipation, squash & stretch, easing on every tween, 6-pose run cycle,
  hit-stop, impact frames, smears, afterimages, screen shake and rumble,
  follow-through, idle breathing

BEAT SHEET (seconds)
 0.9  Cracks race out from "Ted." in three stages. Shivers, jolts.
 1.7  SHATTER. Rings, forks, twelve glass shards. The hole opens.
 1.9  Red climbs out. Lands. Dusts off. Hands on hips.
 3.9  Red jump-kicks "called". The letters scatter.
 4.5  Ink drops in from the top. Superhero landing. Points.
 4.8  Red flinches and DRAWS A KATANA. Shing.
 5.3  Ink cracks his knuckles and TELEPORTS behind him. Tap tap. "?" "!"
 6.7  Red slashes. Ink leans back, matrix-style.
 7.1  The chase up the page. Red slices "teddy", "Engineering" and "README,"
      in half, one hop behind Ink.
 8.6  Ink drops, Red dives, the katana sticks in the floor. Red tugs. Ink kicks.
10.5  Ink whistles. The word "Ted." lying on the floor shakes, poof, a bear.
      It bites Red's leg, gets kicked off, poofs away.
12.7  Hand sign. Three clones. Two hit each other. The third one is awkward.
14.1  The real Red charges. Ink shoots straight up, hovers, his eyes light
      up, and a LASER sweeps the floor into Red. Right wall. Cracks.
16.9  Red blows a kiss. The charm heart lands. Ink goes limp, floats on his
      back toward Red with hearts over his head. Red winds up. And winds up.
      Trembling, charging, the page rumbles.
19.6  MEGA PUNCH. Ink flies into the left wall.
21.0  Red places six pixel-cubes into a wall and hides. Ink knocks. It tips
      over and BURIES him. The pile shakes. Red digs out with a pickaxe.
24.0  Ink walks to centre. Hand sign. "Domain Expansion. Infinite Void."
25.4  The void swallows the page. Red floats off into the stars. The README
      heals inside the void.
28.1  The void collapses into Ink's palm and takes him with it. Clean page.
30.0  Loop.
"""
import math
import html
from PIL import ImageFont

# ---------------------------------------------------------------- constants
T = 31.0
EPS = 0.002
LEAD_TRIM = 0.25      # the whole loop starts this much sooner (the calm opening is shortened)
W, H, FLOOR = 830, 277, 272
H1_Y, RULE_Y = 32, 50
P_Y = [84, 124, 164, 204]
BODY_Y = -17
FONT = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 16)
FONT_B = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 16)
FONT_STACK = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"

H1_TEXT = "Hi, I'm Jeremy \U0001F44B"
PARAS = [
    "~~Dear~~ ~~Diary~~",
    "First of all, let me get something straight: This is a **README,** not a diary.",
    "Systems Design Engineering @ UWaterloo.",
    "I'm building a teddy bear called Ted.",
]
PALETTES = {
    "light": dict(bg="#ffffff", fg="#1f2328", rule="#d1d9e0", red="#cf222e", spark="#e3b341",
                  blade="#d6dbe0", blade_edge="#6b7580", hamon="#ffffff", tsuba="#8a6d2f", wrap="#2b2b2b",
                  pink="#d6409f", void_fg="#f0f0ff", smoke="#8c959f", flash="#ffffff", crack="#9ea5ad",
                  laser="#6e5cf5", scorch="#4b4f55", wood="#7a5230", wind="#22a9bd", wind_hi="#7fe3f0"),
    "dark":  dict(bg="#0d1117", fg="#e6edf3", rule="#3d444d", red="#f85149", spark="#e3b341",
                  blade="#dfe5ec", blade_edge="#6b7580", hamon="#ffffff", tsuba="#c9a24a", wrap="#2b2b2b",
                  pink="#f778ba", void_fg="#f0f0ff", smoke="#8b949e", flash="#f0f0ff", crack="#8b949e",
                  laser="#9d8dff", scorch="#aeb6bf", wood="#9a6b3f", wind="#5fd8e8", wind_hi="#ffffff"),
}
VOID_RIM = "#8f7cff"
BLOCK_GREEN = ["#5d9b3c", "#6fb04a", "#4e8a32"]
BLOCK_BROWN = ["#8a5a3c", "#9c6b47", "#74492f", "#a97a52"]
BEAR_COL = "#a0673d"
SPLINES = {"lin": "0 0 1 1", "in": "0.55 0 1 1", "out": "0 0 0.45 1", "inout": "0.45 0 0.55 1", "snap": "0 0 0.15 1"}

# the page heals while it is hidden inside the void (see ACT 6 for the window)
FADE = (27.13, 27.63)
RESTORE = (27.23, 28.23)


def n(v):
    s = f"{v:.1f}"
    s = s[:-2] if s.endswith(".0") else s
    return "0" if s == "-0" else s


def rnd(i):
    x = math.sin(i * 12.9898 + 78.233) * 43758.5453
    return x - math.floor(x)


# ---------------------------------------------------------------- tracks
class Track:
    def __init__(self, v0):
        self.keys = [[0.0, v0, "lin"]]

    @property
    def t(self):
        return self.keys[-1][0]

    @property
    def v(self):
        return self.keys[-1][1]

    def add(self, t, v, ease="lin"):
        if t <= self.t:
            t = self.t + EPS
        self.keys.append([round(t, 5), v, ease])

    def hold(self, t):
        if t > self.t + 1e-9:
            self.keys.append([round(t, 5), self.v, "lin"])

    def set(self, t, v):
        self.hold(t - EPS)
        self.add(t, v)

    def finished(self):
        ks = [list(k) for k in self.keys]
        assert ks[-1][0] <= T, f"key past loop end {ks[-1]}"
        if ks[-1][0] < T:
            ks.append([T, ks[-1][1], "lin"])
        return ks


def _bisect(keys, t):
    lo, hi = 0, len(keys) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if keys[mid][0] <= t:
            lo = mid
        else:
            hi = mid - 1
    return lo


def eased(s, ease):
    """The same cubic-bezier mapping the browser applies to keySplines, so world-space lookups
    land where the animation actually is mid-tween."""
    if ease == "lin" or s <= 0 or s >= 1:
        return s
    x1, y1, x2, y2 = (float(v) for v in SPLINES[ease].split())
    lo, hi = 0.0, 1.0
    for _ in range(24):
        mid = (lo + hi) / 2
        x = 3 * (1 - mid) ** 2 * mid * x1 + 3 * (1 - mid) * mid ** 2 * x2 + mid ** 3
        if x < s:
            lo = mid
        else:
            hi = mid
    u = (lo + hi) / 2
    return 3 * (1 - u) ** 2 * u * y1 + 3 * (1 - u) * u ** 2 * y2 + u ** 3


def _segment(ks, t):
    i = _bisect(ks, t)
    if i >= len(ks) - 1:
        return ks[-1], ks[-1], 0.0
    t0, v0, _ = ks[i]
    t1, v1, e = ks[i + 1]
    s = 0 if t1 == t0 else (t - t0) / (t1 - t0)
    return ks[i], ks[i + 1], eased(s, e)


def eval_num(track, t):
    k0, k1, s = _segment(track.keys, t)
    v0, v1 = k0[1], k1[1]
    if isinstance(v0, (int, float)):
        return v0 + (v1 - v0) * s
    return tuple(a + (b - a) * s for a, b in zip(v0, v1))


def eval_step(track, t):
    return track.keys[_bisect(track.keys, t)][1]


def window_track(track, t0, t1):
    """A copy of `track` that only carries the keys between t0 and t1 (used for props that are
    invisible outside that window, so their animations stay small)."""
    w = Track(eval_step(track, t0))
    w.hold(t0 - EPS)
    for t, v, e in track.keys:
        if t0 <= t <= t1:
            w.add(t, v, e)
    w.hold(t1)
    return w


def animate(attr, track, fmt):
    keys = track.finished()
    # shift everything earlier by LEAD_TRIM; the loop still ends at T, with the tail hold absorbing it
    keys = [[0.0, keys[0][1], "lin"]] + [[max(EPS, t - LEAD_TRIM), v, e] for t, v, e in keys[1:]]
    for i in range(1, len(keys)):
        if keys[i][0] <= keys[i - 1][0]:
            keys[i][0] = keys[i - 1][0] + EPS / 2
    keys[-1][0] = T
    vals = ";".join(fmt(v) for _, v, _ in keys)
    kt = ";".join(f"{t / T:.6f}" for t, _, _ in keys)
    if any(e != "lin" for _, _, e in keys[1:]):
        ks = ";".join(SPLINES[e] for _, _, e in keys[1:])
        return (f'<animate attributeName="{attr}" values="{vals}" keyTimes="{kt}" keySplines="{ks}" '
                f'calcMode="spline" dur="{T}s" repeatCount="indefinite"/>')
    return f'<animate attributeName="{attr}" values="{vals}" keyTimes="{kt}" dur="{T}s" repeatCount="indefinite"/>'


def animate_tf(kind, track, fmt):
    return animate("transform", track, fmt).replace("<animate ", f'<animateTransform type="{kind}" ')


f_xy = lambda v: f"{n(v[0])} {n(v[1])}"
f_rot = lambda v: f"{n(v[0])} {n(v[1])} {n(v[2])}"
f_s = lambda v: f"{v:.3f}".rstrip("0").rstrip(".")
f_ss = lambda s: f"{f_s(s)} {f_s(s)}"


# ---------------------------------------------------------------- poses
# local coords, feet at (0,0), up is -y, facing +x.  WT = weapon tip (sword or pickaxe head)
P_ = dict
POSES = {
    "stand":  P_(H=(0, -30), N=(0, -25), P=(0, -13), LE=(-3, -18), LH=(-4, -11), RE=(3, -18), RH=(4, -11), LK=(-2, -6), LF=(-3, 0), RK=(2, -6), RF=(3, 0)),
    "guard":  P_(H=(1, -30), N=(0, -25), P=(0, -13), LE=(3, -19), LH=(6, -25), RE=(6, -21), RH=(9, -27), LK=(-4, -7), LF=(-6, 0), RK=(4, -7), RF=(6, 0)),
    # run cycle: contact -> down (absorb) -> passing -> up (push off). Leaning into the run.
    "runA":   P_(H=(5, -29), N=(4, -24), P=(0, -13), LE=(-5, -20), LH=(-10, -16), RE=(8, -21), RH=(13, -26), LK=(-6, -8), LF=(-12, -2), RK=(8, -8), RF=(12, 0)),
    "runD":   P_(H=(5, -27), N=(4, -22), P=(0, -12), LE=(-4, -18), LH=(-8, -13), RE=(7, -20), RH=(11, -24), LK=(-8, -7), LF=(-13, -5), RK=(4, -6), RF=(3, 0)),
    "runB":   P_(H=(5, -31), N=(4, -26), P=(0, -15), LE=(1, -21), LH=(2, -15), RE=(4, -22), RH=(6, -17), LK=(5, -10), LF=(2, -5), RK=(-2, -9), RF=(-4, -1)),
    "punch":  P_(H=(4, -29), N=(3, -24), P=(0, -13), LE=(-3, -20), LH=(1, -24), RE=(10, -25), RH=(18, -26), LK=(-6, -7), LF=(-9, 0), RK=(5, -6), RF=(8, 0)),
    "kick":   P_(H=(-2, -30), N=(-1, -25), P=(0, -13), LE=(-5, -21), LH=(-9, -17), RE=(4, -21), RH=(8, -18), LK=(-2, -6), LF=(-3, 0), RK=(7, -16), RF=(16, -22)),
    "fkick":  P_(H=(-14, -24), N=(-9, -23), P=(0, -20), LE=(-13, -18), LH=(-18, -14), RE=(-10, -28), RH=(-16, -31), LK=(-4, -13), LF=(-8, -10), RK=(7, -20), RF=(16, -19)),
    "crouch": P_(H=(2, -20), N=(1, -16), P=(0, -8), LE=(-4, -11), LH=(-3, -5), RE=(5, -11), RH=(7, -6), LK=(-6, -6), LF=(-7, 0), RK=(6, -6), RF=(7, 0)),
    "hit":    P_(H=(-5, -28), N=(-3, -24), P=(0, -13), LE=(-8, -30), LH=(-10, -36), RE=(2, -31), RH=(0, -37), LK=(2, -8), LF=(5, -2), RK=(-4, -7), RF=(-7, 0)),
    "tuck":   P_(H=(4, -24), N=(2, -20), P=(0, -12), LE=(6, -16), LH=(5, -10), RE=(7, -15), RH=(6, -9), LK=(7, -10), LF=(2, -6), RK=(8, -11), RF=(3, -7)),
    "lying":  P_(H=(-16, -5), N=(-11, -4), P=(0, -3), LE=(-7, -9), LH=(-3, -7), RE=(-10, -1), RH=(-6, 0), LK=(6, -6), LF=(12, -7), RK=(7, -1), RF=(14, 0)),
    "climb":  P_(H=(0, -30), N=(0, -25), P=(0, -13), LE=(-9, -22), LH=(-14, -19), RE=(9, -22), RH=(14, -19), LK=(-1, -6), LF=(-2, 0), RK=(1, -6), RF=(2, 0)),
    "fall":   P_(H=(0, -30), N=(0, -25), P=(0, -13), LE=(-6, -30), LH=(-8, -37), RE=(6, -30), RH=(8, -37), LK=(-3, -7), LF=(-5, -1), RK=(3, -7), RF=(5, -1)),
    "hips":   P_(H=(0, -30), N=(0, -25), P=(0, -13), LE=(-6, -19), LH=(-2, -14), RE=(6, -19), RH=(2, -14), LK=(-2, -6), LF=(-3, 0), RK=(2, -6), RF=(3, 0)),
    "point":  P_(H=(1, -30), N=(0, -25), P=(0, -13), LE=(-4, -19), LH=(-5, -12), RE=(8, -23), RH=(16, -24), LK=(-2, -6), LF=(-3, 0), RK=(2, -6), RF=(3, 0)),
    "dust":   P_(H=(0, -30), N=(0, -25), P=(0, -13), LE=(4, -20), LH=(7, -18), RE=(5, -19), RH=(8, -20), LK=(-2, -6), LF=(-3, 0), RK=(2, -6), RF=(3, 0)),
    "dust2":  P_(H=(0, -30), N=(0, -25), P=(0, -13), LE=(5, -19), LH=(8, -21), RE=(4, -21), RH=(7, -17), LK=(-2, -6), LF=(-3, 0), RK=(2, -6), RF=(3, 0)),
    "wave1":  P_(H=(0, -30), N=(0, -25), P=(0, -13), LE=(-3, -18), LH=(-4, -11), RE=(7, -30), RH=(9, -38), LK=(-2, -6), LF=(-3, 0), RK=(2, -6), RF=(3, 0)),
    "wave2":  P_(H=(0, -30), N=(0, -25), P=(0, -13), LE=(-3, -18), LH=(-4, -11), RE=(7, -30), RH=(13, -36), LK=(-2, -6), LF=(-3, 0), RK=(2, -6), RF=(3, 0)),
    "dizzy":  P_(H=(-2, -29), N=(-1, -24), P=(0, -13), LE=(-6, -20), LH=(-9, -16), RE=(5, -20), RH=(8, -16), LK=(-4, -7), LF=(-7, 0), RK=(5, -7), RF=(8, 0)),
    "lean":   P_(H=(-3, -30), N=(-2, -25), P=(0, -13), LE=(-8, -22), LH=(-12, -18), RE=(3, -22), RH=(7, -18), LK=(-2, -6), LF=(-3, 0), RK=(3, -6), RF=(4, 0)),
    "tap":    P_(H=(1, -30), N=(0, -25), P=(0, -13), LE=(-4, -19), LH=(-5, -12), RE=(8, -24), RH=(15, -24), LK=(-2, -6), LF=(-3, 0), RK=(2, -6), RF=(3, 0)),
    "tap2":   P_(H=(1, -30), N=(0, -25), P=(0, -13), LE=(-4, -19), LH=(-5, -12), RE=(7, -23), RH=(12, -22), LK=(-2, -6), LF=(-3, 0), RK=(2, -6), RF=(3, 0)),
    "scratch": P_(H=(1, -30), N=(0, -25), P=(0, -13), LE=(-3, -18), LH=(-4, -11), RE=(6, -30), RH=(3, -36), LK=(-2, -6), LF=(-3, 0), RK=(2, -6), RF=(3, 0)),
    "shrug":  P_(H=(0, -29), N=(0, -24), P=(0, -13), LE=(-7, -19), LH=(-11, -23), RE=(7, -19), RH=(11, -23), LK=(-2, -6), LF=(-3, 0), RK=(2, -6), RF=(3, 0)),
    "sign":   P_(H=(0, -30), N=(0, -25), P=(0, -13), LE=(4, -20), LH=(5, -27), RE=(5, -19), RH=(5, -28), LK=(-3, -7), LF=(-5, 0), RK=(3, -7), RF=(5, 0)),
    "clap":   P_(H=(1, -30), N=(0, -25), P=(0, -13), LE=(6, -22), LH=(13, -26), RE=(6, -21), RH=(13, -25), LK=(-3, -7), LF=(-5, 0), RK=(3, -7), RF=(5, 0)),
    "windup": P_(H=(-4, -28), N=(-3, -23), P=(0, -13), LE=(3, -20), LH=(7, -23), RE=(-10, -26), RH=(-16, -24), LK=(-6, -7), LF=(-9, 0), RK=(5, -7), RF=(8, 0)),
    "windup2": P_(H=(-7, -27), N=(-6, -22), P=(-1, -13), LE=(4, -20), LH=(9, -24), RE=(-14, -25), RH=(-21, -21), LK=(-8, -6), LF=(-12, 0), RK=(6, -7), RF=(9, 0)),
    "mega":   P_(H=(8, -27), N=(6, -22), P=(0, -13), LE=(-6, -19), LH=(-10, -14), RE=(16, -24), RH=(26, -25), LK=(-8, -6), LF=(-13, 0), RK=(7, -6), RF=(10, 0)),
    "mega2":  P_(H=(10, -26), N=(8, -21), P=(1, -13), LE=(-6, -19), LH=(-10, -14), RE=(18, -23), RH=(28, -23), LK=(-8, -6), LF=(-13, 0), RK=(7, -6), RF=(10, 0)),
    "cover":  P_(H=(2, -19), N=(1, -15), P=(0, -8), LE=(-2, -20), LH=(2, -24), RE=(4, -19), RH=(1, -24), LK=(-6, -6), LF=(-7, 0), RK=(6, -6), RF=(7, 0)),
    "place_lo": P_(H=(2, -29), N=(1, -24), P=(0, -13), LE=(-4, -19), LH=(-5, -12), RE=(8, -20), RH=(15, -13), LK=(-2, -6), LF=(-3, 0), RK=(2, -6), RF=(3, 0)),
    "place_hi": P_(H=(2, -29), N=(1, -24), P=(0, -13), LE=(-4, -19), LH=(-5, -12), RE=(8, -26), RH=(15, -32), LK=(-2, -6), LF=(-3, 0), RK=(2, -6), RF=(3, 0)),
    "whistle": P_(H=(0, -30), N=(0, -25), P=(0, -13), LE=(-3, -18), LH=(-4, -11), RE=(5, -24), RH=(3, -31), LK=(-2, -6), LF=(-3, 0), RK=(2, -6), RF=(3, 0)),
    "kiss2":  P_(H=(1, -30), N=(0, -25), P=(0, -13), LE=(-3, -18), LH=(-4, -11), RE=(8, -25), RH=(16, -28), LK=(-2, -6), LF=(-3, 0), RK=(2, -6), RF=(3, 0)),
    "crack":  P_(H=(1, -30), N=(0, -25), P=(0, -13), LE=(4, -20), LH=(8, -23), RE=(5, -19), RH=(8, -22), LK=(-2, -6), LF=(-3, 0), RK=(2, -6), RF=(3, 0)),
    "crack2": P_(H=(1, -30), N=(0, -25), P=(0, -13), LE=(4, -19), LH=(9, -21), RE=(5, -20), RH=(9, -24), LK=(-2, -6), LF=(-3, 0), RK=(2, -6), RF=(3, 0)),
    # lovestruck: limp, floating on his back (used with face -1 and a +90 degree roll)
    "float":  P_(H=(-2, -31), N=(-1, -26), P=(0, -13), LE=(-6.8, -23.2), LH=(-12.6, -20.4), RE=(-4.8, -22.7), RH=(-9.6, -19.4), LK=(-1.5, -6.5), LF=(4.7, -9.8), RK=(1.0, -6.0), RF=(7.6, -9.5)),
    "push":   P_(H=(6, -27), N=(5, -22), P=(0, -13), LE=(10, -20), LH=(16, -19), RE=(10, -23), RH=(16, -22), LK=(-6, -7), LF=(-10, 0), RK=(5, -7), RF=(8, 0)),
    # flash step: a slow, deliberate stance, front foot planting
    "plant":  P_(H=(2, -29), N=(1, -24), P=(0, -13), LE=(-4, -19), LH=(-6, -13), RE=(4, -20), RH=(7, -14), LK=(-3, -6), LF=(-5, 0), RK=(9, -9), RF=(14, -3)),
    "plant2": P_(H=(3, -28), N=(2, -23), P=(0, -13), LE=(-4, -19), LH=(-6, -13), RE=(4, -20), RH=(7, -14), LK=(-3, -6), LF=(-5, 0), RK=(9, -8), RF=(15, 0)),
    "dash":   P_(H=(14, -24), N=(11, -20), P=(0, -13), LE=(-6, -17), LH=(-14, -14), RE=(0, -16), RH=(-8, -12), LK=(-7, -8), LF=(-14, -3), RK=(8, -9), RF=(16, -3)),
    # hovering for the laser
    "fly":    P_(H=(0, -31), N=(0, -26), P=(0, -14), LE=(-7, -27), LH=(-12, -31), RE=(7, -27), RH=(12, -31), LK=(-3, -8), LF=(-6, -2), RK=(2, -7), RF=(4, 0)),
    # sword poses
    "sw_draw": P_(H=(0, -30), N=(0, -25), P=(0, -13), LE=(-3, -19), LH=(-4, -12), RE=(-4, -28), RH=(-6, -33), LK=(-2, -6), LF=(-3, 0), RK=(2, -6), RF=(3, 0), WT=(-16, -19)),
    "sw_idle": P_(H=(1, -30), N=(0, -25), P=(0, -13), LE=(-4, -20), LH=(-6, -14), RE=(6, -21), RH=(10, -19), LK=(-4, -7), LF=(-6, 0), RK=(4, -7), RF=(6, 0), WT=(26, -36)),
    "sw_wind": P_(H=(-6, -29), N=(-5, -24), P=(-2, -13), LE=(-2, -19), LH=(2, -15), RE=(-12, -27), RH=(-16, -34), LK=(-8, -7), LF=(-11, 0), RK=(3, -7), RF=(6, 0), WT=(-40, -30)),
    "sw_up":   P_(H=(-1, -30), N=(-1, -25), P=(0, -13), LE=(-5, -20), LH=(-3, -14), RE=(2, -31), RH=(4, -39), LK=(-4, -7), LF=(-6, 0), RK=(4, -7), RF=(6, 0), WT=(-13, -58)),
    "sw_down": P_(H=(6, -27), N=(5, -22), P=(1, -13), LE=(-4, -19), LH=(-7, -14), RE=(12, -20), RH=(18, -14), LK=(-7, -7), LF=(-10, 0), RK=(7, -7), RF=(10, 0), WT=(34, 2)),
    "sw_thru": P_(H=(10, -25), N=(8, -20), P=(2, -12), LE=(-2, -18), LH=(-5, -13), RE=(10, -15), RH=(12, -8), LK=(-8, -6), LF=(-12, 0), RK=(9, -6), RF=(13, 0), WT=(4, 12)),
    "sw_rec":  P_(H=(6, -27), N=(5, -22), P=(1, -13), LE=(-3, -19), LH=(-6, -13), RE=(8, -18), RH=(11, -12), LK=(-6, -7), LF=(-9, 0), RK=(6, -7), RF=(9, 0), WT=(20, 8)),
    "sw_stab": P_(H=(-12, -26), N=(-8, -24), P=(0, -19), LE=(-10, -30), LH=(-16, -34), RE=(8, -20), RH=(14, -14), LK=(-6, -14), LF=(-12, -10), RK=(-4, -20), RF=(-10, -24), WT=(25, 3)),
    # rising cut: blade low and back, sweeps up and forward, ends high over the head (= a downswing's wind-up)
    "sw_low":    P_(H=(-3, -29), N=(-2, -24), P=(0, -13), LE=(-5, -20), LH=(-6, -15), RE=(2, -17), RH=(-2, -11), LK=(-5, -7), LF=(-8, 0), RK=(5, -7), RF=(8, 0), WT=(-20, 6)),
    "sw_upcut":  P_(H=(4, -29), N=(3, -24), P=(0, -13), LE=(-4, -20), LH=(-7, -15), RE=(10, -24), RH=(16, -22), LK=(-6, -7), LF=(-9, 0), RK=(6, -7), RF=(9, 0), WT=(40, -38)),
    "sw_upthru": P_(H=(1, -30), N=(0, -25), P=(0, -13), LE=(-4, -20), LH=(-6, -14), RE=(4, -33), RH=(2, -40), LK=(-4, -7), LF=(-6, 0), RK=(4, -7), RF=(6, 0), WT=(-18, -62)),
    # windwall cast: blade thrust out flat in front
    "ww_cast":   P_(H=(3, -30), N=(2, -25), P=(0, -13), LE=(5, -20), LH=(11, -22), RE=(9, -22), RH=(16, -21), LK=(-5, -7), LF=(-8, 0), RK=(5, -7), RF=(8, 0), WT=(46, -20)),
    "tug1":   P_(H=(-6, -28), N=(-4, -24), P=(0, -13), LE=(7, -19), LH=(14, -21), RE=(8, -22), RH=(14, -21), LK=(-6, -7), LF=(-9, 0), RK=(5, -7), RF=(8, 0)),
    "tug2":   P_(H=(-10, -27), N=(-8, -23), P=(-1, -13), LE=(6, -20), LH=(14, -21), RE=(7, -23), RH=(14, -21), LK=(-7, -7), LF=(-10, 0), RK=(5, -7), RF=(8, 0)),
    # crawling out of a hole, rim at local y=0 (feet below the rim, torso above). Facing +x.
    # climbing out of a manhole. Origin = a point on the hole's TOP rim. +y hangs down inside the hole,
    # -y is up above the rim on the page. Facing +x (then mirrored as needed).
    # 1. hanging from the rim by both hands, feet dangling in the dark
    "mh_hang":  P_(H=(0, 10), N=(0, 14), P=(0, 26), LE=(-6, 7), LH=(-8, 0), RE=(6, 7), RH=(8, 0), LK=(-3, 33), LF=(-4, 40), RK=(3, 33), RF=(4, 40)),
    # 2. pull-up: elbows bent, chin at the rim
    "mh_pull":  P_(H=(0, 2), N=(0, 7), P=(0, 19), LE=(-8, 5), LH=(-8, 0), RE=(8, 5), RH=(8, 0), LK=(-4, 27), LF=(-6, 34), RK=(4, 27), RF=(7, 33)),
    # 3. press-up: arms locked straight, chest above the rim, hips at the rim, legs hanging
    "mh_press": P_(H=(1, -17), N=(0, -12), P=(0, 1), LE=(-8, -6), LH=(-9, 0), RE=(8, -6), RH=(9, 0), LK=(-3, 9), LF=(-4, 17), RK=(3, 9), RF=(5, 17)),
    # 4. one knee swung up onto the page, other leg still hanging, leaning forward on the hands
    "mh_knee":  P_(H=(10, -20), N=(8, -15), P=(2, -3), LE=(2, -8), LH=(6, 0), RE=(10, -9), RH=(14, 0), LK=(-2, 6), LF=(-5, 13), RK=(12, -3), RF=(13, 3)),
    # 5. crouched on the page just past the rim, both feet on the page
    "mh_crouch": P_(H=(8, -22), N=(6, -18), P=(2, -9), LE=(-2, -13), LH=(0, -7), RE=(8, -13), RH=(11, -7), LK=(-3, -5), LF=(-4, 0), RK=(8, -5), RF=(10, 0)),
    # climbing out through the hole (older poses, kept). Origin = a point on the hole's bottom rim (the sill).
    # -y is inside the hole (behind the page), +y is outside, in front of the page.
    # squatting inside with both hands on the sill
    "sill":   P_(H=(0, -19), N=(0, -15), P=(0, -8), LE=(-7, -8), LH=(-9, 0), RE=(7, -8), RH=(9, 0), LK=(-6, -5), LF=(-5, 0), RK=(6, -5), RF=(5, 0)),
    # head and shoulders out, hanging down in front of the page, hands pressed on the page, legs kicking inside
    "flop1":  P_(H=(2, 13), N=(1, 8), P=(0, -9), LE=(-8, 10), LH=(-10, 17), RE=(8, 10), RH=(10, 17), LK=(-8, -13), LF=(-15, -15), RK=(8, -12), RF=(15, -14)),
    "flop1b": P_(H=(2, 13), N=(1, 8), P=(0, -9), LE=(-8, 10), LH=(-10, 17), RE=(8, 10), RH=(10, 17), LK=(-7, -15), LF=(-13, -20), RK=(9, -10), RF=(16, -10)),
    # hips over the sill, hands walking down the page, feet dragging over the rim
    "flop2":  P_(H=(2, 24), N=(1, 19), P=(0, 6), LE=(-8, 20), LH=(-10, 27), RE=(8, 20), RH=(10, 27), LK=(-8, 0), LF=(-14, -3), RK=(8, 1), RF=(14, -2)),
    # pickaxe poses (WT = the head end of the handle)
    "dig_hold": P_(H=(0, -30), N=(0, -25), P=(0, -13), LE=(-3, -18), LH=(-4, -11), RE=(5, -21), RH=(8, -27), LK=(-2, -6), LF=(-3, 0), RK=(2, -6), RF=(3, 0), WT=(-8, -44)),
    "dig_up":  P_(H=(-2, -30), N=(-1, -25), P=(0, -13), LE=(-4, -31), LH=(-6, -38), RE=(-3, -31), RH=(-5, -38), LK=(-3, -7), LF=(-5, 0), RK=(3, -7), RF=(5, 0), WT=(-16, -50)),
    "dig_down": P_(H=(4, -28), N=(3, -23), P=(0, -13), LE=(6, -20), LH=(12, -12), RE=(7, -21), RH=(13, -13), LK=(-5, -7), LF=(-8, 0), RK=(5, -7), RF=(8, 0), WT=(29, -1)),
}


def mirror_limbs(p):
    q = dict(p)
    for a, b in (("LE", "RE"), ("LH", "RH"), ("LK", "RK"), ("LF", "RF")):
        q[a], q[b] = p[b], p[a]
    return q


def breathe(p):
    q = dict(p)
    for k in ("H", "N"):
        q[k] = (p[k][0], p[k][1] - 1)
    for k in ("LE", "RE", "LH", "RH"):
        q[k] = (p[k][0], p[k][1] - 0.6)
    return q


for _nm in ("runA", "runD", "runB"):
    POSES[_nm + "2"] = mirror_limbs(POSES[_nm])
for _nm in ("stand", "hips", "guard", "sw_idle", "point", "dizzy", "cover", "fall", "tug1", "sign", "dig_hold", "fly", "float", "ww_cast"):
    POSES[_nm + "_b"] = breathe(POSES[_nm])
LIMBS = [("N", "P"), ("N", "LE", "LH"), ("N", "RE", "RH"), ("P", "LK", "LF"), ("P", "RK", "RF")]
RUN_CYCLE = ["runA", "runD", "runB", "runA2", "runD2", "runB2"]
RUN_BOB = [0, 1.2, -1.2, 0, 1.2, -1.2]       # vertical bob per run frame (down on contact, up on pass)


def pose_pt(P, key):
    if key == "WT":
        return P.get("WT", (P["RH"][0] + 4, P["RH"][1] - 22))
    return P[key]


def interp_pose(a, b, s):
    return {k: (pose_pt(a, k)[0] + (pose_pt(b, k)[0] - pose_pt(a, k)[0]) * s,
                pose_pt(a, k)[1] + (pose_pt(b, k)[1] - pose_pt(a, k)[1]) * s)
            for k in set(a) | set(b) | {"WT"}}


def eval_pose(track, t):
    k0, k1, s = _segment(track.keys, t)
    return interp_pose(POSES[k0[1]], POSES[k1[1]], s)


def limb_str(P, limb):
    return " ".join(f"{n(pose_pt(P, k)[0])},{n(pose_pt(P, k)[1])}" for k in limb)


def poly_str(pts):
    return " ".join(f"{n(x)},{n(y)}" for x, y in pts)


def frame_uv(P):
    """Unit vectors along the weapon (hand -> tip) and perpendicular to it, plus the length."""
    rh, wt = P["RH"], pose_pt(P, "WT")
    dx, dy = wt[0] - rh[0], wt[1] - rh[1]
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    return rh, wt, (ux, uy), (-uy, ux), L


def katana_parts(P):
    """A curved single-edged blade, temper line, oval tsuba, wrapped handle, end cap."""
    rh, wt, (ux, uy), (px, py), L = frame_uv(P)
    # the edge sits on the -perp side; the blade bows the other way, toward the spine
    bx, by = rh[0] + ux * 2.6, rh[1] + uy * 2.6
    lb = L - 2.6
    bend = lb * 0.075

    def spine(s):
        c = 4 * bend * s * (1 - s)
        return bx + ux * lb * s + px * c, by + uy * lb * s + py * c

    def off(pt, side, w):
        return pt[0] + px * side * w, pt[1] + py * side * w

    back = [off(spine(s), 1, 1.25 - 0.3 * s) for s in (0, 0.3, 0.6, 0.86)]
    edge = [off(spine(s), -1, 1.9 - 0.4 * s) for s in (0.86, 0.6, 0.3, 0)]
    blade = back + [wt] + edge
    hamon = [off(spine(s), -1, 0.55) for s in (0.06, 0.3, 0.6, 0.86)]
    cx, cy = rh[0] + ux * 1.2, rh[1] + uy * 1.2
    tsuba = [(cx + px * 3.4 * math.cos(a) + ux * 1.7 * math.sin(a), cy + py * 3.4 * math.cos(a) + uy * 1.7 * math.sin(a))
             for a in [i * math.pi / 4 for i in range(8)]]
    h0x, h0y = rh[0] - ux * 0.6, rh[1] - uy * 0.6
    h1x, h1y = rh[0] - ux * 10.5, rh[1] - uy * 10.5
    tsuka = [(h0x + px * 1.4, h0y + py * 1.4), (h1x + px * 1.4, h1y + py * 1.4), (h1x - px * 1.4, h1y - py * 1.4), (h0x - px * 1.4, h0y - py * 1.4)]
    diamonds = []
    for s in (0.22, 0.52, 0.82):
        dx_, dy_ = h0x + (h1x - h0x) * s, h0y + (h1y - h0y) * s
        diamonds.append([(dx_ + ux * 1.3, dy_ + uy * 1.3), (dx_ + px * 1.2, dy_ + py * 1.2), (dx_ - ux * 1.3, dy_ - uy * 1.3), (dx_ - px * 1.2, dy_ - py * 1.2)])
    kx, ky = rh[0] - ux * 11.3, rh[1] - uy * 11.3
    kashira = [(kx + ux * 0.9 + px * 1.6, ky + uy * 0.9 + py * 1.6), (kx - ux * 0.9 + px * 1.6, ky - uy * 0.9 + py * 1.6),
               (kx - ux * 0.9 - px * 1.6, ky - uy * 0.9 - py * 1.6), (kx + ux * 0.9 - px * 1.6, ky + uy * 0.9 - py * 1.6)]
    return dict(blade=blade, hamon=hamon, tsuba=tsuba, tsuka=tsuka, d0=diamonds[0], d1=diamonds[1], d2=diamonds[2], kashira=kashira)


KATANA_STYLE = [
    ("tsuka", "wrap", None, 0),
    ("d0", "red", None, 0), ("d1", "red", None, 0), ("d2", "red", None, 0),
    ("kashira", "tsuba", "fg", 0.5),
    ("blade", "blade", "blade_edge", 0.7),
    ("hamon", None, "hamon", 0.9),
    ("tsuba", "tsuba", "fg", 0.6),
]


def katana_svg(parts, p, animated=None):
    """animated: optional pose-track to animate `points` from; otherwise static."""
    out = []
    for key, fill, stroke, sw in KATANA_STYLE:
        pts = parts[key]
        tag = "polyline" if key == "hamon" else "polygon"
        attrs = f'fill="{p[fill]}"' if fill else 'fill="none"'
        if stroke:
            attrs += f' stroke="{p[stroke]}" stroke-width="{sw}" stroke-linejoin="round"'
        if key == "hamon":
            attrs += ' stroke-linecap="round" opacity="0.75"'
        anim = animate("points", animated, lambda nm, key=key: poly_str(katana_parts(POSES[nm])[key])) if animated else ""
        out.append(f'<{tag} points="{poly_str(pts)}" {attrs}>{anim}</{tag}>')
    return "".join(out)


def pick_parts(P):
    rh, wt, (ux, uy), (px, py), L = frame_uv(P)
    h0x, h0y = rh[0] - ux * 4, rh[1] - uy * 4
    handle = [(h0x + px * 1.1, h0y + py * 1.1), (wt[0] + px * 1.1, wt[1] + py * 1.1), (wt[0] - px * 1.1, wt[1] - py * 1.1), (h0x - px * 1.1, h0y - py * 1.1)]
    head = [(wt[0] + px * 11 - ux * 2.2, wt[1] + py * 11 - uy * 2.2), (wt[0] + px * 6 + ux * 2.2, wt[1] + py * 6 + uy * 2.2),
            (wt[0] + ux * 2.8, wt[1] + uy * 2.8), (wt[0] - px * 6 + ux * 2.2, wt[1] - py * 6 + uy * 2.2),
            (wt[0] - px * 11 - ux * 2.2, wt[1] - py * 11 - uy * 2.2), (wt[0] - px * 6 - ux * 1.2, wt[1] - py * 6 - uy * 1.2),
            (wt[0] - ux * 1.4, wt[1] - uy * 1.4), (wt[0] + px * 6 - ux * 1.2, wt[1] + py * 6 - uy * 1.2)]
    return dict(handle=handle, head=head)


def pick_svg(p, animated):
    out = []
    for key, fill, stroke in (("handle", "wood", "fg"), ("head", "blade", "fg")):
        pts = pick_parts(POSES[animated.keys[0][1]])[key]
        out.append(f'<polygon points="{poly_str(pts)}" fill="{p[fill]}" stroke="{p[stroke]}" stroke-width="0.7" stroke-linejoin="round">'
                   + animate("points", animated, lambda nm, key=key: poly_str(pick_parts(POSES[nm])[key])) + "</polygon>")
    return "".join(out)


def figure_static(P, colour, width=2.6):
    out = [f'<circle r="5" fill="{colour}" cx="{n(P["H"][0])}" cy="{n(P["H"][1])}"/>']
    for limb in LIMBS:
        out.append(f'<polyline fill="none" stroke="{colour}" stroke-width="{width}" stroke-linecap="round" '
                   f'stroke-linejoin="round" points="{limb_str(P, limb)}"/>')
    return "".join(out)


# ---------------------------------------------------------------- characters
class Char:
    def __init__(self, pose0="stand", pos0=(0, 0), face0=1):
        self.pos = Track(tuple(map(float, pos0)))
        self.rot = Track((0.0, 0.0, float(BODY_Y)))
        self.sx = Track(face0)
        self.sq = Track((1.0, 1.0))
        self.op = Track(0)
        self.pz = Track(pose0)
        self.wop = Track(0)
        self.pop = Track(0)
        self.lop = {}            # per-limb opacity tracks (only used by the "outside" copy)

    def limbs_out(self, t, names):
        """From t on, these limbs are in front of the page. names: 'H', 'torso', 'LA', 'RA', 'LL', 'RL'."""
        for nm in names:
            self.lop.setdefault(nm, Track(0)).set(t, 1)

    def at(self, t, x, y, ease="lin"):
        self.pos.add(t, (float(x), float(y)), ease)

    def stay(self, t):
        self.pos.hold(t)

    def put(self, t, x, y):
        self.pos.set(t, (float(x), float(y)))

    def x(self, t=None):
        return self.pos.v[0] if t is None else eval_num(self.pos, t)[0]

    def jump(self, t0, t1, x1, y1, h, step=0.04):
        self.pos.hold(t0)
        x0, y0 = self.pos.v
        k = max(4, int(round((t1 - t0) / step)))
        for i in range(1, k + 1):
            s = i / k
            self.pos.add(t0 + (t1 - t0) * s, (x0 + (x1 - x0) * s, y0 + (y1 - y0) * s - 4 * h * s * (1 - s)))

    def run(self, t0, t1, x1, frame=0.06, ease="lin"):
        self.pos.hold(t0)
        x0, y = self.pos.v
        t, i = t0, 0
        while t < t1 - 1e-6:
            self.pose(t, RUN_CYCLE[i % 6], tween=frame * 0.95, ease="inout")
            t += frame
            i += 1
            tt = min(t, t1)
            sx = eased((tt - t0) / (t1 - t0), ease)
            self.pos.add(tt, (x0 + (float(x1) - x0) * sx, y + RUN_BOB[i % 6]))
        self.pos.add(t1 + EPS, (float(x1), y))

    def jitter(self, t0, t1, amp, hz=24, amp1=None):
        """Shake in place. amp1 lets the shake grow (or shrink) over the interval."""
        self.pos.hold(t0)
        x, y = self.pos.v
        t, i = t0, 0
        while t < t1 - 1 / hz:
            t += 1 / hz
            i += 1
            a = amp if amp1 is None else amp + (amp1 - amp) * (t - t0) / (t1 - t0)
            self.pos.add(t, (x + a * (rnd(i * 3.1) - 0.5) * 2, y + a * 0.5 * (rnd(i * 7.7) - 0.5) * 2))
        self.pos.add(t1, (x, y))

    def pose(self, t, name, tween=0.08, ease="out"):
        assert name in POSES, name
        self.pz.hold(t - tween)
        self.pz.add(t, name, ease)

    def idle(self, t0, t1, base="stand", period=0.5):
        t, i = t0, 0
        while t < t1 - 1e-6:
            self.pose(t, base if i % 2 == 0 else base + "_b", tween=period * 0.9, ease="inout")
            t += period
            i += 1

    def face(self, t, d):
        self.sx.set(t, d)

    def spin(self, t0, t1, deg, ease="lin"):
        self.rot.hold(t0)
        a, px, py = self.rot.v
        end = a + deg
        self.rot.add(t1, (end, px, py), ease)
        self.rot.add(t1 + EPS, (((end + 180) % 360) - 180, px, py))

    def rot_to(self, t0, t1, a, ease="out", pivot=None):
        self.rot.hold(t0)
        _, px, py = self.rot.v
        if pivot is not None:
            px, py = pivot
            self.rot.add(t0 + EPS, (self.rot.v[0], float(px), float(py)))
        self.rot.add(t1, (float(a), px, py), ease)

    def rot_pivot(self, t, px=0.0, py=float(BODY_Y)):
        self.rot.hold(t)
        self.rot.add(t + EPS, (self.rot.v[0], float(px), float(py)))

    def wobble(self, t0, t1, deg, period=0.16, base=None):
        """Rock back and forth around the current (or given) angle."""
        self.rot.hold(t0)
        a0, px, py = self.rot.v
        if base is not None:
            a0 = base
        t, i = t0, 0
        while t < t1 - period / 2:
            t += period / 2
            i += 1
            self.rot.add(t, (a0 + (deg if i % 2 else -deg), px, py), "inout")
        self.rot.add(t1, (a0, px, py), "inout")

    def land(self, t, amount=0.26, pose="crouch"):
        self.sq.set(t, (1 + amount, 1 - amount))
        self.sq.add(t + 0.09, (0.95, 1.05), "out")
        self.sq.add(t + 0.17, (1.0, 1.0), "out")
        if pose:
            self.pose(t, pose, tween=0.03)

    def takeoff(self, t, amount=0.12):
        self.sq.hold(t - 0.05)
        self.sq.add(t, (1 - amount, 1 + amount), "out")
        self.sq.add(t + 0.1, (1.0, 1.0), "out")

    def hitstop(self, t, dur):
        for tr in (self.pos, self.rot, self.pz, self.sq):
            tr.hold(t)
            tr.hold(t + dur)

    def show(self, t):
        self.op.set(t, 1)

    def hide(self, t):
        self.op.set(t, 0)

    def weapon(self, t, on):
        self.wop.set(t, 1 if on else 0)

    def pick(self, t, on):
        self.pop.set(t, 1 if on else 0)

    def world(self, t, key):
        P = eval_pose(self.pz, t)
        x, y = pose_pt(P, key)
        sx = eval_step(self.sx, t)
        sqx, sqy = eval_num(self.sq, t)
        x, y = x * sx * sqx, y * sqy
        a, px, py = eval_num(self.rot, t)
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        dx, dy = x - px, y - py
        x, y = px + dx * ca - dy * sa, py + dx * sa + dy * ca
        X, Y = eval_num(self.pos, t)
        return X + x, Y + y

    def head_mark(self, t):
        hx, hy = self.world(t, "H")
        return hx, hy - 15

    def pose_at(self, t):
        return eval_pose(self.pz, t)

    def svg(self, colour, weapons=None, op_track=None, katana_win=(0, T), pick_win=(0, T), limb_ops=False, halo=None):
        """weapons: the palette dict when this character carries the katana / pickaxe.
        limb_ops: wrap each limb in its own opacity group driven by self.lop.
        halo: a colour; draws a thick knockout outline under the figure so it stays readable over busy linework."""
        op = op_track or self.op
        LIMB_NAMES = {("N", "P"): "torso", ("N", "LE", "LH"): "LA", ("N", "RE", "RH"): "RA", ("P", "LK", "LF"): "LL", ("P", "RK", "RF"): "RL"}

        def wrap(name, inner):
            if not limb_ops:
                return inner
            tr = self.lop.get(name, Track(0))
            return '<g opacity="0">' + animate("opacity", tr, str) + inner + "</g>"
        times = sorted({k[0] for k in self.sx.keys} | {k[0] for k in self.sq.keys})
        sc = Track((float(self.sx.keys[0][1]), 1.0))
        for tt in times:
            if tt == 0:
                continue
            s = eval_step(self.sx, tt)
            qx, qy = eval_num(self.sq, tt)
            sc.add(tt, (s * qx, qy))
        p0 = POSES[self.pz.keys[0][1]]
        out = [f'<g opacity="{op.keys[0][1]}">', animate("opacity", op, str), animate_tf("translate", self.pos, f_xy),
               "<g>", animate_tf("rotate", self.rot, f_rot), "<g>", animate_tf("scale", sc, lambda v: f"{f_s(v[0])} {f_s(v[1])}"),
               ]
        head_anim = animate("cx", self.pz, lambda nm: n(POSES[nm]["H"][0])) + animate("cy", self.pz, lambda nm: n(POSES[nm]["H"][1]))

        def body(col, width, r):
            parts = [wrap("H", f'<circle r="{r}" fill="{col}" cx="{n(p0["H"][0])}" cy="{n(p0["H"][1])}">' + head_anim + "</circle>")]
            for limb in LIMBS:
                parts.append(wrap(LIMB_NAMES[limb], f'<polyline fill="none" stroke="{col}" stroke-width="{width}" stroke-linecap="round" '
                                  f'stroke-linejoin="round" points="{limb_str(p0, limb)}">'
                                  + animate("points", self.pz, lambda nm, limb=limb: limb_str(POSES[nm], limb)) + "</polyline>"))
            return "".join(parts)
        if halo:
            out.append(body(halo, 5.4, 6.4))      # knockout pass, all limbs, under everything
        out.append(body(colour, 2.6, 5))
        if weapons:
            kz, pz = window_track(self.pz, *katana_win), window_track(self.pz, *pick_win)
            out.append('<g opacity="0">' + animate("opacity", self.wop, str) + katana_svg(katana_parts(POSES[kz.keys[0][1]]), weapons, animated=kz) + "</g>")
            out.append('<g opacity="0">' + animate("opacity", self.pop, str) + pick_svg(weapons, pz) + "</g>")
        out.append("</g></g></g>")
        return "".join(out)


# ---------------------------------------------------------------- words
class Word:
    def __init__(self, text, x, y, w, size=16, fixed_width=True, strike=False, bold=False):
        self.text, self.x, self.y, self.w, self.size, self.fixed = text, x, y, w, size, fixed_width
        self.strike, self.bold = strike, bold
        self.cx, self.cy = x + w / 2, y - size * 0.33
        self.tr, self.rot, self.op = Track((0.0, 0.0)), Track(0.0), Track(1)
        self.animated = False
        self.halves = None
        self.clip = None

    def shake(self, t0, t1, amp, hz=28):
        """Shiver in place, around wherever the word currently is."""
        self.animated = True
        self.tr.hold(t0)
        bx, by = self.tr.v
        t, i = t0, 0
        while t < t1 - 1 / hz:
            t += 1 / hz
            i += 1
            self.tr.add(t, (bx + amp * (1 if i % 2 else -1), by + amp * 0.4 * (1 if (i // 2) % 2 else -1)))
        self.tr.add(t1, (bx, by))

    def fly(self, t0, t1, lx, ly, rot, h, bounce=None):
        self.animated = True
        self.tr.hold(t0)
        self.rot.hold(t0)
        dx, dy = self.tr.v
        x0, y0, r0 = self.cx + dx, self.cy + dy, self.rot.v
        k = max(5, int(round((t1 - t0) / 0.04)))
        for i in range(1, k + 1):
            s = i / k
            x, y = x0 + (lx - x0) * s, y0 + (ly - y0) * s - 4 * h * s * (1 - s)
            self.tr.add(t0 + (t1 - t0) * s, (x - self.cx, y - self.cy))
            self.rot.add(t0 + (t1 - t0) * s, r0 + rot * s)
        if bounce:
            bx, bt, bh = bounce
            r0 = self.rot.v
            for i in range(1, 6):
                s = i / 5
                self.tr.add(t1 + bt * s, (lx + bx * s - self.cx, ly - 4 * bh * s * (1 - s) - self.cy))
                self.rot.add(t1 + bt * s, r0 + 12 * s)

    def dip(self, t, d=5):
        self.animated = True
        self.tr.hold(t)
        self.tr.add(t + 0.07, (0.0, d), "out")
        self.tr.add(t + 0.18, (0.0, -2.0), "inout")
        self.tr.add(t + 0.3, (0.0, 0.0), "inout")

    def restore(self, t0, t1):
        self.tr.hold(t0)
        self.rot.hold(t0)
        self.tr.add(t1, (0.0, 0.0), "inout")
        self.rot.add(t1, 0.0, "inout")

    def slice(self, t, angle, fall=((-26, 70), (24, -120)), through=None):
        """Cut along a line at `angle` degrees. `through` is a page point the line passes through
        (where the blade actually crossed the word); defaults to the word's centre."""
        self.animated = True
        self.op.set(t, 0)
        a = math.radians(angle)
        d, nn = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
        self.halves = []
        c = through if through else (self.cx, self.cy)
        for sgn, (ddx, drot) in zip((1, -1), fall):
            hw = Word(self.text, self.x, self.y, self.w, self.size, self.fixed, bold=self.bold)
            hw.op = Track(0)
            hw.op.set(t, 1)
            L = 120
            hw.clip = [(c[0] + d[0] * L, c[1] + d[1] * L), (c[0] - d[0] * L, c[1] - d[1] * L),
                       (c[0] - d[0] * L + sgn * nn[0] * L, c[1] - d[1] * L + sgn * nn[1] * L),
                       (c[0] + d[0] * L + sgn * nn[0] * L, c[1] + d[1] * L + sgn * nn[1] * L)]
            hw.animated = True
            hw.tr.hold(t)
            hw.tr.add(t + 0.1, (sgn * nn[0] * 5, sgn * nn[1] * 5), "out")
            hw.rot.hold(t + 0.1)
            x0, y0 = self.cx + sgn * nn[0] * 5, self.cy + sgn * nn[1] * 5
            lx, ly = self.cx + ddx, FLOOR - 7
            dur = 0.42 + 0.18 * (1 - self.cy / 300)
            for i in range(1, 11):
                s = i / 10
                hw.tr.add(t + 0.1 + dur * s, (x0 + (lx - x0) * s - self.cx, y0 + (ly - y0) * (s * s) - self.cy))
                hw.rot.add(t + 0.1 + dur * s, drot * s)
            self.halves.append(hw)

    def _text(self, fg):
        tl = f' textLength="{n(self.w)}"' if self.fixed else ""
        st = ' text-decoration="line-through"' if self.strike else ""
        fw = ' font-weight="700"' if self.bold else ""
        return (f'<text x="{n(self.x)}" y="{n(self.y)}" font-size="{self.size}" fill="{fg}"{tl}{st}{fw}>'
                f'{html.escape(self.text)}</text>')

    def svg(self, fg):
        text = self._text(fg)
        if not self.animated:
            return text
        clip = ""
        if self.clip:
            cid = f"c{abs(hash((self.text, self.x, self.clip[2]))) % 10**8}"
            pts = " ".join(f"{n(x)},{n(y)}" for x, y in self.clip)
            clip = f'<clipPath id="{cid}"><polygon points="{pts}"/></clipPath>'
            text = f'<g clip-path="url(#{cid})">{text}</g>'
        return (f'{clip}<g opacity="{self.op.keys[0][1]}">' + animate("opacity", self.op, str)
                + animate_tf("translate", self.tr, f_xy) + "<g>"
                + animate_tf("rotate", self.rot, lambda a: f"{n(a)} {n(self.cx)} {n(self.cy)}")
                + text + "</g></g>")

    def all_svg(self, fg):
        return self.svg(fg) + ("".join(h.svg(fg) for h in self.halves) if self.halves else "")

    def plain(self, fg):
        return self._text(fg)


def layout(text, y):
    words, x, sp = [], 0.0, FONT.getlength(" ")
    for tok in text.split(" "):
        strike = tok.startswith("~~") and tok.endswith("~~")
        bold = tok.startswith("**") and tok.endswith("**")
        tok = tok.strip("~").strip("*")
        w = (FONT_B if bold else FONT).getlength(tok)
        words.append(Word(tok, x, y, w, strike=strike, bold=bold))
        x += w + sp
    return words


LINES = [layout(p, P_Y[i]) for i, p in enumerate(PARAS)]
ALL_WORDS = [wd for line in LINES for wd in line]


def word(line, text):
    for wd in LINES[line]:
        if wd.text == text:
            return wd
    raise KeyError(text)


_kicked = word(3, "called")
NL, _x = [], _kicked.x
for ch in _kicked.text:
    cw = FONT.getlength(ch)
    NL.append(Word(ch, _x, _kicked.y, cw, fixed_width=False))
    _x += cw
LINES[3] = [wd for wd in LINES[3] if wd is not _kicked]
RD = word(3, "Ted.")
LINES[3] = [wd for wd in LINES[3] if wd is not RD]
S1, S2, S3 = word(3, "teddy"), word(2, "Engineering"), word(1, "README,")
IX, IY = RD.cx + 4, RD.cy + 1          # where the first crack starts

# ---------------------------------------------------------------- effect library
LAYERS = {k: [] for k in ("cracks", "debris", "props", "fx_low", "fx_mid", "over_red", "fx_high", "marks", "top")}


def layer(name, fn):
    LAYERS[name].append(fn)


def polyline_len(pts):
    return sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))


def path_d(pts):
    return "M" + " L".join(f"{n(x)},{n(y)}" for x, y in pts)


def point_along(pts, f):
    total = polyline_len(pts)
    target = total * f
    for i in range(len(pts) - 1):
        seg = math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
        if target <= seg or i == len(pts) - 2:
            s = max(0, min(1, target / seg)) if seg else 0
            return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * s, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * s)
        target -= seg
    return pts[-1]


def grow(d, L, w, t0, dur):
    """A path that draws itself from its start over `dur` seconds (dash-offset trick)."""
    off = Track(L + 2 * w)
    off.hold(t0)
    off.add(t0 + dur, 0.0, "out")
    return (f'<path d="{d}" stroke-width="{n(w)}" stroke-dasharray="{n(L + w)} {n(L + 3 * w)}" stroke-dashoffset="{n(L + 2 * w)}">'
            + animate("stroke-dashoffset", off, n) + "</path>")


def crack_set(cx, cy, R, count, seed, span=(0, 2 * math.pi), yscale=0.72, rings=(), t_show=0.0,
              prop=0.1, width=1.0, colour="fg", alpha=1.0):
    radials = []
    for i in range(count):
        base = span[0] + (span[1] - span[0]) * (i + 0.5) / count + (rnd(seed + i) - 0.5) * 0.25
        L = R * (0.6 + 0.4 * rnd(seed * 3 + i))
        pts, ang = [(cx, cy)], base
        for k in range(1, 6):
            ang += (rnd(seed * 7 + i * 5 + k) - 0.5) * 0.4
            r = L * k / 5
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang) * yscale))
        radials.append(pts)
    paths = []
    for i, pts in enumerate(radials):
        L = polyline_len(pts)
        paths.append(grow(path_d(pts), L, width, t_show, prop))
        thick = pts[:3]
        paths.append(grow(path_d(thick), polyline_len(thick), width * 2.1, t_show, prop * 0.5))
        if rnd(seed * 11 + i) < 0.65:
            bx, by = pts[3]
            ang = math.atan2((pts[4][1] - by) / yscale, pts[4][0] - bx) + (0.8 if i % 2 else -0.8)
            fl = L * 0.28
            fork = [(bx, by), (bx + fl * 0.5 * math.cos(ang), by + fl * 0.5 * math.sin(ang) * yscale),
                    (bx + fl * math.cos(ang + 0.3), by + fl * math.sin(ang + 0.3) * yscale)]
            paths.append(grow(path_d(fork), polyline_len(fork), width * 0.8, t_show + prop * 0.6, prop * 0.5))
    ring_paths = []
    full = (span[1] - span[0]) > 6
    for f in rings:
        for i in range(len(radials)):
            if not full and i == len(radials) - 1:
                continue
            if rnd(seed * 13 + i + f * 100) < 0.22:
                continue
            a, b = radials[i], radials[(i + 1) % len(radials)]
            fa = min(0.98, f + (rnd(seed + i * 2) - 0.5) * 0.12)
            fb = min(0.98, f + (rnd(seed + i * 2 + 1) - 0.5) * 0.12)
            pa, pb = point_along(a, fa), point_along(b, fb)
            mx = (pa[0] + pb[0]) / 2 + (rnd(i * 9 + seed) - 0.5) * 6
            my = (pa[1] + pb[1]) / 2 + (rnd(i * 4 + seed) - 0.5) * 4
            ring_paths.append(f'<path d="{path_d([pa, (mx, my), pb])}" stroke-width="{n(width * 0.75)}"/>')

    def svg(p):
        op = Track(alpha)
        op.hold(FADE[0])
        op.add(FADE[1], 0, "in")
        rop = Track(0)
        rop.set(t_show + prop, 0.8 * alpha)
        rop.hold(FADE[0])
        rop.add(FADE[1], 0, "in")
        out = (f'<g fill="none" stroke="{p[colour]}" stroke-linecap="round" stroke-linejoin="round" opacity="{alpha}">'
               + animate("opacity", op, str) + "".join(paths) + "</g>")
        if ring_paths:
            out += (f'<g fill="none" stroke="{p[colour]}" stroke-linecap="round" opacity="0">'
                    + animate("opacity", rop, str) + "".join(ring_paths) + "</g>")
        return out
    return svg, radials


def spark(x, y, t, size, kind="spark", dur=0.26, lay="fx_high"):
    """Impact: a thin shockwave ring that expands and fades, and a few sharp lines that shoot
    outward and shrink. Ink only, no fill. kind="white" is a glint (sword, blocks): a small cross."""
    def svg(p):
        col = p["fg"] if kind != "bg" else p["bg"]
        op = Track(0)
        op.set(t, 1)
        op.hold(t + dur * 0.35)
        op.add(t + dur, 0, "in")
        out = [f'<g transform="translate({n(x)},{n(y)})"><g opacity="0">', animate("opacity", op, str)]
        if kind == "white":
            sc = Track(0.2)
            sc.hold(t)
            sc.add(t + dur * 0.35, 1.0, "out")
            sc.add(t + dur, 0.5, "in")
            rot = Track(0.0)
            rot.hold(t)
            rot.add(t + dur, 40.0, "out")
            L = size * 1.6
            out.append("<g>" + animate_tf("rotate", rot, lambda a: f"{n(a)} 0 0") + "<g>" + animate_tf("scale", sc, f_ss)
                       + f'<path d="M{n(-L)},0 H{n(L)} M0,{n(-L)} V{n(L)} M{n(-L * .45)},{n(-L * .45)} L{n(L * .45)},{n(L * .45)} M{n(-L * .45)},{n(L * .45)} L{n(L * .45)},{n(-L * .45)}" '
                       f'stroke="{col}" stroke-width="1.3" stroke-linecap="round"/></g></g>')
        else:
            rr = Track(size * 0.3)
            rr.hold(t)
            rr.add(t + dur, size * 2.6, "out")
            sw = Track(2.4)
            sw.hold(t)
            sw.add(t + dur, 0.3, "out")
            out.append(f'<circle r="{n(size * .3)}" fill="none" stroke="{col}" stroke-width="2.4">' + animate("r", rr, n) + animate("stroke-width", sw, n) + "</circle>")
            cnt = 7
            for i in range(cnt):
                a = i * 2 * math.pi / cnt + rnd(i * 3 + size) * 0.5
                r0, L = size * 0.6, size * (1.0 + 0.9 * rnd(i + size))
                push = size * (2.2 + 1.2 * rnd(i * 7 + size))
                ux, uy = math.cos(a), math.sin(a)
                pts = Track((r0, r0 + L))
                pts.hold(t)
                pts.add(t + dur * 0.9, (r0 + push, r0 + push + L * 0.15), "out")
                out.append(f'<polyline fill="none" stroke="{col}" stroke-width="{n(1.0 + 0.8 * rnd(i + 2))}" stroke-linecap="round" points="{n(r0 * ux)},{n(r0 * uy)} {n((r0 + L) * ux)},{n((r0 + L) * uy)}">'
                           + animate("points", pts, lambda v, ux=ux, uy=uy: f"{n(v[0] * ux)},{n(v[0] * uy)} {n(v[1] * ux)},{n(v[1] * uy)}") + "</polyline>")
        out.append("</g></g>")
        return "".join(out)
    layer(lay, svg)


def dust(x, y, t, big=False, up=False):
    def svg(p):
        out = []
        if up:
            pts = [(-3, -14), (2, -17), (-1, -22)]
        else:
            pts = [(-18, -6), (-10, -13), (-2, -16), (6, -15), (14, -11), (20, -5)] if big else [(-12, -5), (-5, -10), (5, -10), (12, -5)]
        for i, (dx, dy) in enumerate(pts):
            tr = Track((0.0, 0.0))
            tr.set(t, (0.0, 0.0))
            tr.add(t + 0.32, (dx * 1.3, dy * 1.2), "out")
            op = Track(0)
            op.set(t, 0.75)
            op.add(t + 0.32, 0, "in")
            r = 1.8 + 0.6 * rnd(i + t)
            out.append(f'<g transform="translate({n(x)},{n(y)})"><circle r="{n(r)}" fill="{p["smoke"]}" opacity="0">'
                       + animate("opacity", op, str) + animate_tf("translate", tr, f_xy) + "</circle></g>")
        return "".join(out)
    layer("fx_low", svg)


def poof(x, y, t, size=1.0):
    def svg(p):
        out = []
        for i in range(7):
            a = i * 2 * math.pi / 7 + rnd(i + t) * 0.5
            d = (9 + 7 * rnd(i * 3 + t)) * size
            tr = Track((0.0, 0.0))
            tr.set(t, (0.0, 0.0))
            tr.add(t + 0.36, (d * math.cos(a), d * math.sin(a) * 0.7 - 4), "out")
            op = Track(0)
            op.set(t, 0.9)
            op.hold(t + 0.12)
            op.add(t + 0.36, 0, "in")
            sc = Track(0.4)
            sc.hold(t)
            sc.add(t + 0.15, 1.0, "out")
            sc.add(t + 0.36, 1.3)
            r = (4 + 2.5 * rnd(i * 5 + t)) * size
            out.append(f'<g transform="translate({n(x)},{n(y)})"><g opacity="0">' + animate("opacity", op, str)
                       + animate_tf("translate", tr, f_xy) + "<g>" + animate_tf("scale", sc, f_ss)
                       + f'<circle r="{n(r)}" fill="{p["smoke"]}"/></g></g></g>')
        return "".join(out)
    layer("fx_mid", svg)


def speed_lines(x, t0, t1, y0=-6, y1=36, horizontal=False):
    def svg(p):
        op = Track(0)
        op.set(t0, 0.55)
        op.hold(t0 + (t1 - t0) * 0.5)
        op.add(t1, 0, "in")
        if horizontal:
            lines = "".join(f'<path d="M{n(x + dx)},{n(y0 + dy)} h{n(ln)}"/>' for dx, dy, ln in [(0, -24, -40), (-8, -16, -60), (2, -8, -46)])
        else:
            lines = "".join(f'<path d="M{n(x + dx)},{n(a)} V{n(b)}"/>' for dx, a, b in [(-8, y0 + 4, y1 - 10), (0, y0, y1), (8, y0 + 6, y1 - 12)])
        return f'<g opacity="0" stroke="{p["fg"]}" stroke-width="2" stroke-linecap="round">' + animate("opacity", op, str) + lines + "</g>"
    layer("fx_low", svg)


def crescent(cx, cy, r_out, a0, a1, t, dur=0.1):
    r_in = r_out * 0.55

    def svg(p):
        op = Track(0)
        op.set(t, 0.45)
        op.add(t + dur, 0, "in")
        sc = Track(0.8)
        sc.hold(t)
        sc.add(t + dur, 1.1, "out")
        A0, A1 = math.radians(a0), math.radians(a1)
        big = 1 if abs(A1 - A0) > math.pi else 0
        sweep = 1 if A1 > A0 else 0
        d = (f"M{n(r_out * math.cos(A0))},{n(r_out * math.sin(A0))} A{n(r_out)},{n(r_out)} 0 {big} {sweep} "
             f"{n(r_out * math.cos(A1))},{n(r_out * math.sin(A1))} L{n(r_in * math.cos(A1))},{n(r_in * math.sin(A1))} "
             f"A{n(r_in)},{n(r_in)} 0 {big} {1 - sweep} {n(r_in * math.cos(A0))},{n(r_in * math.sin(A0))} Z")
        return (f'<g transform="translate({n(cx)},{n(cy)})"><g opacity="0">' + animate("opacity", op, str)
                + animate_tf("scale", sc, f_ss) + f'<path d="{d}" fill="{p["fg"]}"/></g></g>')
    layer("fx_high", svg)


def smear_line(x0, y0, x1, y1, t, width=5, dur=0.07, colour="fg"):
    def svg(p):
        op = Track(0)
        op.set(t, 0.5)
        op.add(t + dur, 0, "in")
        return (f'<path d="M{n(x0)},{n(y0)} L{n(x1)},{n(y1)}" stroke="{p[colour]}" stroke-width="{width}" stroke-linecap="round" opacity="0">'
                + animate("opacity", op, str) + "</path>")
    layer("fx_high", svg)


def impact_lines(x, y, t, big=True, colour="fg"):
    """The impact frame: thin radial speed lines from the hit point to the edges, for two frames."""
    if not big:
        return

    def svg(p):
        op = Track(0)
        op.set(t, 0.75)
        op.hold(t + 0.04)
        op.add(t + 0.1, 0, "in")
        lines = []
        for i in range(22):
            a = i * 2 * math.pi / 22 + rnd(i + t) * 0.22
            r0 = 34 + 26 * rnd(i * 2 + t)
            r1 = r0 + 90 + 160 * rnd(i * 3 + t)
            lines.append(f'<path d="M{n(x + r0 * math.cos(a))},{n(y + r0 * math.sin(a))} L{n(x + r1 * math.cos(a))},{n(y + r1 * math.sin(a))}" stroke-width="{n(0.6 + 1.0 * rnd(i + 9))}"/>')
        return f'<g opacity="0" stroke="{p[colour]}" stroke-linecap="round">' + animate("opacity", op, str) + "".join(lines) + "</g>"
    layer("fx_high", svg)


def flash(t, dur=0.06, amount=0.7, colour="flash"):
    def svg(p):
        op = Track(0)
        op.set(t, amount)
        op.hold(t + dur * 0.5)
        op.add(t + dur, 0, "in")
        return f'<rect width="{W}" height="{H}" fill="{p[colour]}" opacity="0">' + animate("opacity", op, str) + "</rect>"
    layer("top", svg)


def mark(txt, x, y, t, dur=0.5):
    def svg(p):
        op = Track(0)
        op.set(t, 1)
        op.hold(t + dur * 0.7)
        op.add(t + dur, 0, "in")
        sc = Track(0.3)
        sc.hold(t)
        sc.add(t + 0.1, 1.25, "out")
        sc.add(t + 0.2, 1.0, "inout")
        return (f'<g transform="translate({n(x)},{n(y)})"><g opacity="0">' + animate("opacity", op, str)
                + animate_tf("scale", sc, f_ss)
                + f'<text text-anchor="middle" font-size="15" font-weight="700" fill="{p["fg"]}" y="5">{html.escape(txt)}</text></g></g>')
    layer("marks", svg)


def blink(x, y, t):
    def svg(p):
        op = Track(0)
        op.set(t, 0.9)
        op.add(t + 0.14, 0, "in")
        sc = Track((1.0, 0.2))
        sc.hold(t)
        sc.add(t + 0.06, (1.0, 1.0), "out")
        sc.add(t + 0.14, (0.1, 1.1), "in")
        return (f'<g transform="translate({n(x)},{n(y - 18)})"><g opacity="0">' + animate("opacity", op, str)
                + animate_tf("scale", sc, lambda v: f"{f_s(v[0])} {f_s(v[1])}")
                + f'<ellipse rx="5" ry="26" fill="{p["void_fg"]}" stroke="{p["fg"]}" stroke-width="1.2"/></g></g>')
    layer("fx_high", svg)


def ghost(P, x, y, face, t, colour_key, dur=0.18, drift=(0, 0), alpha=0.45, rot=0.0):
    def svg(p):
        op = Track(0)
        op.set(t, alpha)
        op.add(t + dur, 0, "in")
        tr = Track((0.0, 0.0))
        tr.set(t, (0.0, 0.0))
        tr.add(t + dur, drift, "out")
        return (f'<g transform="translate({n(x)},{n(y)})"><g opacity="0">' + animate("opacity", op, str)
                + animate_tf("translate", tr, f_xy) + f'<g transform="rotate({n(rot)} 0 {BODY_Y}) scale({face},1)">'
                + figure_static(P, p[colour_key]) + "</g></g></g>")
    layer("fx_mid", svg)


def teleport(c, t, x1, y1, face1, colour_key):
    P = c.pose_at(t - 0.01)
    x0, y0 = eval_num(c.pos, t - 0.01)
    face0 = eval_step(c.sx, t - 0.01)
    for k in range(1, 4):
        s = k / 4
        ghost(P, x0 + (x1 - x0) * s, y0 + (y1 - y0) * s, face0, t + 0.025 * k, colour_key,
              drift=((x1 - x0) * 0.06, (y1 - y0) * 0.06), alpha=0.5 - 0.1 * k)
    blink(x0, y0, t)
    c.hide(t)
    blink(x1, y1, t + 0.1)
    c.put(t + 0.12, x1, y1)
    c.face(t + 0.12, face1)
    c.show(t + 0.12)


def trail(c, t0, t1, colour_key, k=4):
    """Afterimages left behind a fast move between t0 and t1."""
    for i in range(k):
        tt = t0 + (t1 - t0) * (i + 1) / (k + 1)
        x, y = eval_num(c.pos, tt)
        P = c.pose_at(tt)
        ghost(P, x, y, eval_step(c.sx, tt), tt, colour_key, dur=0.2, alpha=0.35, rot=eval_num(c.rot, tt)[0])


FRAME = Track((0.0, 0.0))


def jolt(t, amp):
    FRAME.hold(t - EPS)
    for dt, fx, fy in [(0.03, 1, -0.6), (0.07, -0.7, 0.5), (0.11, 0.4, -0.3), (0.16, 0, 0)]:
        FRAME.add(t + dt, (amp * fx, amp * fy), "out")


def rumble(t0, t1, amp0, amp1):
    FRAME.hold(t0)
    t, i = t0, 0
    while t < t1 - 0.04:
        t += 0.04
        i += 1
        a = amp0 + (amp1 - amp0) * (t - t0) / (t1 - t0)
        FRAME.add(t, (a * (rnd(i * 5.3) - 0.5) * 2, a * (rnd(i * 9.1) - 0.5) * 2))
    FRAME.add(t1, (0.0, 0.0))


def hit(t, x, y, size, *chars, big=False, dur=None, shake=None):
    dur = dur or (0.09 if big else 0.06)
    spark(x, y, t, size)
    for c in chars:
        c.hitstop(t, dur)
    if big:
        impact_lines(x, y, t)
        flash(t, 0.07, 0.75)
    jolt(t, shake if shake is not None else (3 if big else 1.5))
    return t + dur


def heavy_slash(c, t_contact, big=True):
    """A committed overhead cut. Wind-up (slow), raise, cut (snap), carry through, slow recovery.
    Returns nothing; the caller places the crescent and the cut at t_contact."""
    c.pose(t_contact - 0.30, "sw_wind", 0.16, "inout")
    c.pose(t_contact - 0.09, "sw_up", 0.13, "in")
    c.pose(t_contact, "sw_down", 0.045, "snap")
    c.pose(t_contact + 0.07, "sw_thru", 0.07, "out")
    c.sq.hold(t_contact - 0.001)
    c.sq.add(t_contact + 0.05, (1.08, 0.94), "out")      # weight drops into the cut
    c.sq.add(t_contact + 0.22, (1.0, 1.0), "inout")
    c.pose(t_contact + 0.3, "sw_rec", 0.2, "inout")
    c.pose(t_contact + 0.55, "sw_idle", 0.22, "inout")
    if big:
        jolt(t_contact, 1.2)


def heavy_upswing(c, t_contact):
    """A rising cut. Blade low and back, then it sweeps up and forward through the target and ends
    high overhead, which is exactly the wind-up of the next overhead cut. Contact lands mid-sweep."""
    c.pose(t_contact - 0.28, "sw_low", 0.16, "inout")
    c.pose(t_contact + 0.04, "sw_upcut", 0.1, "snap")
    c.pose(t_contact + 0.14, "sw_upthru", 0.1, "out")
    c.sq.hold(t_contact - 0.001)
    c.sq.add(t_contact + 0.05, (0.94, 1.08), "out")       # he rises into it
    c.sq.add(t_contact + 0.22, (1.0, 1.0), "inout")
    jolt(t_contact, 1.2)


def blade_cut_point(c, t, wd):
    """Where the blade's line (hand -> tip) crosses the word's centre height at time t."""
    (hx, hy), (tx, ty) = c.world(t, "RH"), c.world(t, "WT")
    if abs(ty - hy) < 1e-6:
        return (tx, wd.cy)
    k = (wd.cy - hy) / (ty - hy)
    return (hx + (tx - hx) * k, wd.cy)


def hop(c, t0, t1, x, y, h=14, land_amt=0.22):
    c.pose(t0 - 0.06, "crouch", 0.06)
    c.takeoff(t0)
    c.jump(t0, t1, x, y, h)
    c.pose(t0 + 0.05, "tuck", 0.05)
    c.pose(t1 - 0.06, "fall", 0.06)
    c.land(t1, land_amt)


# ================================================================ cast
ink = Char("fall", (400, -45))
red = Char("stand", (0, 0))
crawl = Char("stand", (0, 0))     # Red while he is climbing out through the hole
c1, c2, c3 = Char("stand", (0, 0)), Char("stand", (0, 0)), Char("stand", (0, 0))

# ================================================================ ACT 1  break-in  (0.9 - 4.6)
stage1, _ = crack_set(IX, IY, 16, 3, seed=2, t_show=0.9, prop=0.12, width=0.9, alpha=0.8)
stage2, _ = crack_set(IX, IY, 34, 6, seed=5, t_show=1.3, prop=0.14, width=1.0, alpha=0.8)
stage3, RADS = crack_set(IX, IY, 84, 12, seed=9, rings=(0.62, 0.86), t_show=1.7, prop=0.1, width=1.0, alpha=0.8)
for fn in (stage1, stage2, stage3):
    layer("cracks", fn)
RD.shake(0.9, 1.1, 0.8)
RD.shake(1.3, 1.65, 1.4)
for L in NL:
    L.shake(1.35, 1.65, 0.8)
jolt(0.9, 0.6)
jolt(1.3, 1.0)

HOLE_PTS = [point_along(pts, 0.5 + 0.07 * rnd(i + 40)) for i, pts in enumerate(RADS)]
HX = sum(x for x, _ in HOLE_PTS) / len(HOLE_PTS)
HY = sum(y for _, y in HOLE_PTS) / len(HOLE_PTS)
HT, HB, HR = min(y for _, y in HOLE_PTS), max(y for _, y in HOLE_PTS), max(x for x, _ in HOLE_PTS)
HOLE_SCALE = Track(0.0)
HOLE_SCALE.hold(1.7 - EPS)
HOLE_SCALE.add(1.7, 0.5)
HOLE_SCALE.add(1.76, 1.15, "out")
HOLE_SCALE.add(1.84, 0.96)
HOLE_SCALE.add(1.9, 1.0)
HOLE_SCALE.hold(FADE[0] + 0.2)
HOLE_SCALE.add(FADE[1] + 0.25, 0.0, "in")


def hole_svg(p, edge_only=False):
    pts = " ".join(f"{n(x - HX)},{n(y - HY)}" for x, y in HOLE_PTS)
    paint = 'fill="none"' if edge_only else 'fill="url(#holeg)"'
    return (f'<g transform="translate({n(HX)},{n(HY)})"><g>' + animate_tf("scale", HOLE_SCALE, f_ss)
            + f'<polygon points="{pts}" {paint} stroke="{p["fg"]}" stroke-opacity="0.3" stroke-width="0.8" stroke-linejoin="round"/></g></g>')


def shards_svg(p):
    out = []
    for i in range(len(RADS)):
        a, b = RADS[i], RADS[(i + 1) % len(RADS)]
        f0, f1 = 0.5 + 0.07 * rnd(i + 40), 0.5 + 0.07 * rnd(i + 41)
        quad = [point_along(a, f0), point_along(a, min(0.95, f0 + 0.24 + 0.1 * rnd(i))),
                point_along(b, min(0.95, f1 + 0.2 + 0.1 * rnd(i + 3))), point_along(b, f1)]
        cx = sum(x for x, _ in quad) / 4
        cy = sum(y for _, y in quad) / 4
        ang = math.atan2(cy - IY, cx - IX)
        ux, uy = math.cos(ang), math.sin(ang)
        t = 1.7
        tr, rt, op = Track((0.0, 0.0)), Track(0.0), Track(0)
        tr.set(t, (0.0, 0.0))
        rt.set(t, 0.0)
        op.set(t, 1)
        spd = 70 + 60 * rnd(i * 5 + 1)
        vx, vy = ux * spd, uy * spd * 0.8 - 45
        if i in (1, 4, 7, 10):
            g = 260
            s_land = (-vy + math.sqrt(vy * vy + 4 * g * (FLOOR - 5 - cy))) / (2 * g)
            for j in range(1, 11):
                s = s_land * j / 10
                tr.add(t + s, (vx * s, vy * s + g * s * s))
                rt.add(t + s, (250 if i % 2 else -200) * s / s_land * 0.6)
            x_end = vx * s_land
            tr.add(t + s_land + 0.12, (x_end + 6, FLOOR - 5 - cy - 5), "out")
            rt.add(t + s_land + 0.12, rt.v + 25)
            tr.add(t + s_land + 0.24, (x_end + 10, FLOOR - 5 - cy), "in")
            rt.add(t + s_land + 0.24, rt.v + 10)
            op.hold(FADE[0])
            op.add(FADE[1], 0, "in")
        else:
            for j in range(1, 10):
                s = 0.6 * j / 9
                tr.add(t + s, (vx * s * 1.2, vy * s + 200 * s * s))
                rt.add(t + s, (300 if i % 2 else -260) * s)
            op.hold(t + 0.35)
            op.add(t + 0.6, 0, "in")
        pts = " ".join(f"{n(x)},{n(y)}" for x, y in quad)
        out.append('<g opacity="0">' + animate("opacity", op, str) + animate_tf("translate", tr, f_xy) + "<g>"
                   + animate_tf("rotate", rt, lambda a, cx=cx, cy=cy: f"{n(a)} {n(cx)} {n(cy)}")
                   + f'<polygon points="{pts}" fill="{p["bg"]}" stroke="{p["fg"]}" stroke-width="0.9" stroke-linejoin="round" opacity="0.95"/></g></g>')
    return "".join(out)


layer("debris", shards_svg)
jolt(1.7, 3)
flash(1.7, 0.08, 0.5)
RD.fly(1.7, 2.4, 640, FLOOR - 6, 165, 70, bounce=(16, 0.2, 8))

# Red climbs out of the hole. `peek` is clipped to the hole polygon, so he is only ever seen
# THROUGH the opening. He comes up from deep inside (small and low), looks around, crouches, and at
# that instant the unclipped `red` takes over, entirely inside the hole, and leaps out over the rim.
# 1.9  Red rises up out of the dark, seen through the hole, and climbs out of it like a manhole.
#      `crawl` is drawn twice: clipped to the hole (seen THROUGH the opening) and clipped to the page around
#      it, limb by limb as each limb comes up over the top rim. The page really occludes him.
RIM_X, RIM_Y = HX + 4, HT + 1                 # a point on the flat top rim of the hole
crawl.put(0, RIM_X, RIM_Y + 70)
crawl.sq.set(1.9, (0.5, 0.5))
crawl.show(1.9)
crawl.stay(1.9)
# he swims up out of the dark and grabs the rim with both hands
crawl.pose(2.1, "fall", 0.08)
crawl.at(2.32, RIM_X, RIM_Y, "out")
crawl.sq.add(2.32, (1.0, 1.0), "out")
crawl.pose(2.32, "mh_hang", 0.16, "out")
crawl.limbs_out(2.3, ("LA", "RA"))           # hands on the page
crawl.at(2.42, RIM_X, RIM_Y + 3, "out")      # settles under his weight
crawl.at(2.56, RIM_X, RIM_Y, "inout")
# pull-up. Chin to the rim. A beat of effort.
crawl.pose(2.92, "mh_pull", 0.34, "inout")
crawl.jitter(2.9, 3.02, 0.4, 20)
# press-up. Arms lock, chest comes up above the rim onto the page.
crawl.pose(3.24, "mh_press", 0.28, "inout")
crawl.limbs_out(3.0, ("H", "torso"))
jolt(3.24, 0.4)
# a knee swings up onto the page
crawl.pose(3.56, "mh_knee", 0.3, "inout")
crawl.at(3.56, RIM_X + 4, RIM_Y, "inout")
crawl.limbs_out(3.4, ("RL",))
# and the other leg follows. He is crouched on the page past the rim.
crawl.pose(3.86, "mh_crouch", 0.28, "inout")
crawl.at(3.86, RIM_X + 10, RIM_Y, "inout")
crawl.limbs_out(3.72, ("LL",))
# hand-off to the real character at the exact same spot and pose
crawl.hide(3.86)
red.put(0, RIM_X + 10, RIM_Y)
red.pose(3.86, "mh_crouch", EPS)
red.show(3.86)
# stand up slow, a quick look around, then he hops down off the rim to the floor
red.stay(3.86)
red.at(4.1, RIM_X + 14, RIM_Y, "inout")
red.pose(4.1, "stand", 0.24, "inout")
red.face(4.18, -1)
red.face(4.36, 1)
red.face(4.5, -1)
red.pose(4.56, "crouch", 0.08)
red.takeoff(4.62)
red.jump(4.62, 4.96, HX - 60, FLOOR, 30)
red.pose(4.68, "tuck", 0.05)
red.pose(4.86, "fall", 0.06)
red.land(4.96, 0.26)
dust(HX - 60, FLOOR, 4.96)
# dust off, hands on hips, a breath
red.pose(5.08, "stand", 0.1)
red.pose(5.16, "dust", 0.08)
red.pose(5.26, "dust2", 0.06)
red.pose(5.36, "hips", 0.1)
red.idle(5.36, 5.46, "hips")
# Red jump-kicks "called"
REDX1 = NL[0].x - 8
red.pose(5.46, "crouch", 0.05)
red.takeoff(5.5)
red.jump(5.5, 5.76, REDX1, FLOOR, 40)
red.pose(5.54, "tuck", 0.05)
red.pose(5.62, "kick", 0.05)
KX, KY = red.world(5.64, "RF")
spark(KX, KY, 5.64, 9)
impact_lines(KX, KY, 5.64, big=False)
jolt(5.64, 1)
for L, (lx, rot, dur, h, bounce) in zip(NL, [(110, -200, 0.55, 40, (10, 0.15, 5)), (55, -400, 0.70, 60, (14, 0.20, 8)),
                                               (140, 120, 0.45, 25, None), (85, -90, 0.60, 45, (8, 0.15, 4)),
                                               (170, 60, 0.40, 20, None), (200, 250, 0.50, 50, (6, 0.12, 4))]):
    L.fly(5.64, 5.64 + dur, lx, FLOOR - 6, rot, h, bounce)
red.pose(5.7, "fall", 0.06)
red.land(5.76)
dust(REDX1, FLOOR, 5.76)
red.pose(5.88, "hips", 0.1)
red.idle(5.88, 5.98, "hips")

# ================================================================ ACT 2  Ink, katana, teleport  (5.43 - 7.98)
speed_lines(400, 5.78, 6.08)
ink.show(5.78)
ink.stay(5.78)
ink.at(5.98, 400, RULE_Y, "in")
ink.land(5.98, 0.3)
dust(400, RULE_Y, 5.98)
jolt(5.98, 2)
ink.pose(6.13, "stand", 0.1)
ink.face(6.13, -1)
ink.pose(6.2, "point", 0.08)

red.face(6.02, 1)
red.pose(6.02, "fall", 0.05)
mark("!", *red.head_mark(6.07), 6.04, 0.45)
red.pose(6.15, "guard", 0.1)
red.pose(6.24, "sw_draw", 0.1)
red.pose(6.31, "sw_draw", 0.02)
red.weapon(6.34, True)
red.pose(6.41, "sw_idle", 0.07, "snap")
_rh = red.world(6.41, "RH")
crescent(_rh[0] - 8, _rh[1] - 4, 32, -150, -20, 6.35, 0.12)
spark(*red.world(6.42, "WT"), 6.36, 7, kind="white")
red.idle(6.44, 6.73, "sw_idle", 0.3)

ink.pose(6.28, "crack", 0.1)
ink.pose(6.4, "crack2", 0.07)
ink.pose(6.5, "crack", 0.07)
ink.pose(6.6, "stand", 0.08)
ink.pose(6.68, "crouch", 0.06)
TPX = REDX1 - 30
teleport(ink, 6.76, TPX, FLOOR, 1, "fg")
ink.pose(6.88, "stand", 0.02)

heavy_slash(red, 6.98)
_c = red.world(6.96, "N")
crescent(_c[0] + 6, _c[1] + 2, 40, -120, 60, 6.97, 0.13)
ink.pose(7.12, "tap", 0.08)
ink.pose(7.22, "tap2", 0.05)
ink.pose(7.3, "tap", 0.05)
ink.pose(7.38, "tap2", 0.05)
ink.pose(7.48, "stand", 0.08)
mark("?", *red.head_mark(7.28), 7.26, 0.45)
red.face(7.53, -1)
_hm = red.head_mark(7.58)
mark("!", _hm[0] + 2, _hm[1], 7.56, 0.4)
heavy_upswing(red, 7.84)
red.pose(8.2, "sw_rec", 0.2, "inout")
red.pose(8.45, "sw_idle", 0.2, "inout")
_c = red.world(7.82, "N")
crescent(_c[0] - 6, _c[1] + 4, 40, 150, 250, 7.83, 0.13)
ink.pose(7.76, "lean", 0.06)
ink.rot_to(7.74, 7.82, -58, "out", pivot=(0, 0))
ink.rot_to(7.92, 8.06, 0, "out")
ink.rot_pivot(8.06)
ink.pose(8.06, "stand", 0.08)

# ================================================================ ACT 3  chase, slicing, stuck katana  (8.08 - 11.68)
# the chase. Cut 1 is a RISING cut on the way up to "teddy" (blade turned over), which leaves the blade
# high: cut 2 comes straight down out of that onto "Engineering", which leaves it low: cut 3 rises
# again through "README,". One continuous figure-eight of steel.
red.face(8.16, 1)
hop(ink, 8.16, 8.41, S1.cx, P_Y[3] + 1)
S1.dip(8.41)
# cut 1: rising. He jumps from below the line and the blade sweeps up through the word as he rises.
red.pose(8.34, "crouch", 0.08)
red.pose(8.48, "sw_low", 0.12, "inout")
red.takeoff(8.52)
red.jump(8.52, 8.8, S1.x + 26, P_Y[3] + 1, 46)
red.land(8.8, 0.16, pose=None)
red.pose(8.88, "sw_upcut", 0.1, "snap")
red.pose(9.0, "sw_upthru", 0.1, "out")
_c = red.world(8.84, "N")
crescent(_c[0] + 10, _c[1] + 6, 44, 150, 250, 8.83, 0.13)
S1.slice(8.84, -32, fall=((-20, 60), (26, -110)), through=blade_cut_point(red, 8.84, S1))
jolt(8.84, 1.2)
hop(ink, 8.58, 8.83, S2.cx, P_Y[2] + 1)
S2.dip(8.83)
# cut 2: the blade is already overhead. He jumps and brings it straight down onto the next word.
red.pose(8.98, "sw_up", 0.14, "inout")
red.takeoff(9.1)
red.jump(9.1, 9.42, S2.x + 10, P_Y[2] + 1, 54)
red.pose(9.46, "sw_down", 0.045, "snap")
red.land(9.46, 0.18, pose=None)
red.pose(9.53, "sw_thru", 0.07, "out")
_c = red.world(9.44, "N")
crescent(_c[0] + 8, _c[1] + 2, 42, -120, 60, 9.45, 0.13)
S2.slice(9.46, 35, fall=((-26, 70), (24, -120)), through=blade_cut_point(red, 9.46, S2))
jolt(9.46, 1.2)
hop(ink, 9.1, 9.35, S3.cx, P_Y[1] + 1)
S3.dip(9.35)
# cut 3: the blade is low after the follow-through. He turns it over and rises through "README,".
red.pose(9.8, "sw_low", 0.2, "inout")
red.takeoff(9.9)
red.jump(9.9, 10.18, S3.x + 42, P_Y[1] + 1, 46)
red.land(10.18, 0.16, pose=None)
red.pose(10.26, "sw_upcut", 0.1, "snap")
red.pose(10.38, "sw_upthru", 0.1, "out")
_c = red.world(10.22, "N")
crescent(_c[0] + 10, _c[1] + 6, 44, 150, 250, 10.21, 0.13)
S3.slice(10.22, -32, fall=((-20, 60), (26, -110)), through=blade_cut_point(red, 10.22, S3))
jolt(10.22, 1.2)
red.pose(10.6, "sw_rec", 0.18, "inout")
red.pose(10.68, "sw_idle", 0.12)

ink.pose(9.78, "crouch", 0.06)
ink.takeoff(9.83)
ink.jump(9.83, 10.18, 560, FLOOR, 18)
ink.pose(9.88, "tuck", 0.05)
ink.pose(10.08, "fall", 0.06)
ink.land(10.18, 0.32)
dust(560, FLOOR, 10.18, big=True)
jolt(10.18, 1.2)
ink.pose(10.33, "stand", 0.1)
ink.face(10.33, 1)
ink.idle(10.33, 10.56, "stand", 0.25)
# Red dives off the line with the katana, Ink rolls, the katana sticks in the floor
ink.idle(10.56, 10.78, "stand", 0.22)
red.pose(10.78, "crouch", 0.08)
red.takeoff(10.84)
red.jump(10.84, 11.12, 560, FLOOR, 10)
red.pose(10.88, "sw_wind", 0.06)
red.pose(10.98, "sw_stab", 0.08, "in")
ink.pose(10.9, "crouch", 0.05)
ink.takeoff(10.93)
ink.stay(10.93)
ink.at(11.12, 620, FLOOR, "out")
ink.pose(10.95, "tuck", 0.04)
ink.spin(10.93, 11.12, 360, "out")
ink.land(11.12, 0.2)
SWX = 560
STUCK_HILT, STUCK_TIP = (SWX + 12, FLOOR - 24), (SWX + 26, FLOOR + 7)
dust(SWX + 22, FLOOR, 11.12, big=True)
jolt(11.12, 2.2)
impact_lines(SWX + 24, FLOOR, 11.12, big=False)
red.weapon(11.12, False)
red.land(11.12, 0.22, pose="tug1")
red.pose(11.28, "tug2", 0.1, "inout")
red.pose(11.42, "tug1", 0.1, "inout")
red.pose(11.56, "tug2", 0.1, "inout")
red.pose(11.68, "tug1", 0.1, "inout")
red.idle(11.68, 11.88, "tug1", 0.2)


def stuck_katana(hilt, tip, t_in, t_out, tugs=(), seed=1):
    """A katana buried in the floor from t_in to t_out. Entry cracks grow on impact, a few chips of
    floor spray out, and each tug time makes it wobble without coming loose."""
    (hx, hy), (tx, ty) = hilt, tip
    wob = Track(0.0)
    wob.hold(t_in - EPS)
    wob.add(t_in + 0.05, -5.0, "out")       # it bites and shivers
    wob.add(t_in + 0.13, 3.0, "inout")
    wob.add(t_in + 0.22, 0.0, "inout")
    for tt in tugs:
        wob.hold(tt - EPS)
        wob.add(tt + 0.04, -7.0, "out")
        wob.add(tt + 0.12, 4.0, "inout")
        wob.add(tt + 0.2, 0.0, "inout")
    op = Track(0)
    op.set(t_in, 1)
    op.hold(t_out[0])
    op.add(t_out[1], 0, "in")
    ex, ey = (tx + hx) / 2 + (tx - hx) * 0.42, FLOOR          # where the blade enters the floor
    cracks = []
    for i, (ang, L) in enumerate(((-150, 13), (-118, 9), (-62, 10), (-28, 14), (-95, 6))):
        a = math.radians(ang + (rnd(seed * 3 + i) - 0.5) * 16)
        pts = [(ex, ey), (ex + L * 0.5 * math.cos(a) + (rnd(i + seed) - 0.5) * 2, ey + L * 0.5 * math.sin(a)),
               (ex + L * math.cos(a), ey + L * math.sin(a))]
        cracks.append(grow(path_d(pts), polyline_len(pts), 1.1 if i < 4 else 0.7, t_in, 0.12))

    cid = f"floor{int(hx)}"

    def svg(p):
        return ('<g opacity="0">' + animate("opacity", op, str)
                + f'<clipPath id="{cid}"><rect x="{n(hx - 60)}" y="-20" width="140" height="{n(FLOOR + 20)}"/></clipPath>'
                + f'<g clip-path="url(#{cid})"><g>' + animate_tf("rotate", wob, lambda a: f"{n(a)} {n(ex)} {n(ey)}")
                + katana_svg(katana_parts(dict(RH=(hx, hy), WT=(tx, ty))), p) + "</g></g>"
                # the entry slit, a short dark gash the blade disappears into
                + f'<path d="M{n(ex - 4.5)},{n(ey - 0.6)} L{n(ex + 4.5)},{n(ey + 0.6)}" stroke="{p["fg"]}" stroke-width="2.2" stroke-linecap="round" opacity="0.85"/>'
                + f'<g fill="none" stroke="{p["fg"]}" stroke-linecap="round" stroke-linejoin="round" opacity="0.8">' + "".join(cracks) + "</g>"
                + "</g>")
    layer("props", svg)
    # chips of floor
    def chips(p):
        out = []
        for i in range(5):
            vx, vy = (rnd(i * 7 + seed) - 0.5) * 70, -(30 + 40 * rnd(i * 3 + seed))
            tr = Track((0.0, 0.0))
            tr.set(t_in, (0.0, 0.0))
            for j in range(1, 7):
                s_ = 0.4 * j / 6
                tr.add(t_in + s_, (vx * s_, vy * s_ + 240 * s_ * s_))
            o = Track(0)
            o.set(t_in, 1)
            o.hold(t_in + 0.3)
            o.add(t_in + 0.42, 0, "in")
            out.append(f'<g transform="translate({n(ex)},{n(ey)})"><rect x="-1.2" y="-1.2" width="2.4" height="2.4" fill="{p["fg"]}" opacity="0">'
                       + animate("opacity", o, str) + animate_tf("translate", tr, f_xy) + "</rect></g>")
        return "".join(out)
    layer("fx_low", chips)


stuck_katana(STUCK_HILT, STUCK_TIP, 11.12, (16.12, 16.14), tugs=(11.12, 11.28, 11.56))

ink.pose(11.24, "stand", 0.1)
ink.face(11.24, -1)
ink.pose(11.34, "hips", 0.1)
ink.idle(11.34, 11.68, "hips", 0.34)
ink.run(11.68, 11.82, 596)
ink.pose(11.88, "kick", 0.06, "snap")
_f = ink.world(11.9, "RF")
red.pose(11.9, "hit", EPS)
tt = hit(11.9, _f[0] - 4, _f[1], 10, ink, red)
red.jump(tt, 12.26, 470, FLOOR, 30)
red.spin(tt, 12.26, -360, "out")
red.land(12.26, 0.2, pose="lying")
jolt(12.26, 1)
dust(470, FLOOR, 12.26)
ink.pose(12.04, "stand", 0.1)

# ================================================================ ACT 4  Ted, clones, laser  (12.08 - 16.88)
ink.pose(12.14, "whistle", 0.1)
RD.shake(12.18, 12.48, 1.2)
poof(640, FLOOR - 8, 12.48, 0.8)
ink.pose(12.58, "hips", 0.1)
ink.idle(12.58, 13.43, "hips", 0.45)


class Bear:
    def __init__(self):
        self.pos, self.sx, self.sc, self.op, self.rot = Track((640.0, float(FLOOR))), Track(-1), Track(0.0), Track(0), Track(0.0)

    def hop(self, t0, t1, x, y, h):
        self.pos.hold(t0)
        x0, y0 = self.pos.v
        for i in range(1, 7):
            s = i / 6
            self.pos.add(t0 + (t1 - t0) * s, (x0 + (x - x0) * s, y0 + (y - y0) * s - 4 * h * s * (1 - s)))

    def scurry(self, t0, t1, x1, bounce=3):
        self.pos.hold(t0)
        x0, y0 = self.pos.v
        k = max(4, int((t1 - t0) / 0.05))
        for i in range(1, k + 1):
            s = i / k
            self.pos.add(t0 + (t1 - t0) * s, (x0 + (x1 - x0) * s, y0 - abs(math.sin(s * k * math.pi)) * bounce))

    def svg(self, p):
        times = sorted({k[0] for k in self.sx.keys} | {k[0] for k in self.sc.keys})
        sc = Track((0.0, 0.0))
        for tt in times:
            if tt == 0:
                continue
            s, q = eval_step(self.sx, tt), eval_num(self.sc, tt)
            sc.add(tt, (s * q, q))
        body = (f'<circle cx="-3.6" cy="-10.5" r="1.9" fill="{BEAR_COL}"/><circle cx="3.6" cy="-10.5" r="1.9" fill="{BEAR_COL}"/>'
                f'<circle cx="0" cy="-8" r="4.4" fill="{BEAR_COL}"/><ellipse cx="0" cy="-2.8" rx="4.6" ry="3.2" fill="{BEAR_COL}"/>'
                f'<circle cx="-1.6" cy="-9.58" r="0.7" fill="{p["bg"]}"/><circle cx="1.6" cy="-9.58" r="0.7" fill="{p["bg"]}"/>'
                f'<circle cx="0" cy="-6.6" r="0.8" fill="{p["bg"]}"/>'
                f'<path d="M-2.5,-1 L-3,0.5 M2.5,-1 L3,0.5" stroke="{BEAR_COL}" stroke-width="2" stroke-linecap="round"/>')
        return ('<g opacity="0">' + animate("opacity", self.op, str) + animate_tf("translate", self.pos, f_xy) + "<g>"
                + animate_tf("rotate", self.rot, lambda a: f"{n(a)} 0 -6") + "<g>"
                + animate_tf("scale", sc, lambda v: f"{f_s(v[0])} {f_s(v[1])}") + body + "</g></g></g>")


bear = Bear()
bear.op.set(12.48, 1)
bear.sc.hold(12.48 - EPS)
bear.sc.add(12.48, 0.0)
bear.sc.add(12.6, 1.7, "out")
bear.sc.add(12.7, 1.35, "inout")
bear.hop(12.74, 12.88, 616, FLOOR, 12)          # a little excited hop first
bear.scurry(12.92, 13.28, 470 + 14)
bear.rot.hold(12.92)
for i in range(1, 8):
    bear.rot.add(12.92 + 0.05 * i, (8 if i % 2 else -8))
bear.rot.add(13.28, 0.0)

red.pose(12.43, "crouch", 0.15, "inout")
red.pose(12.68, "stand", 0.12)
red.face(12.68, 1)
red.idle(12.68, 13.03, "stand", 0.35)
red.pose(13.06, "fall", 0.06)
mark("!", *red.head_mark(13.11), 13.08, 0.4)
# the bite: the bear hangs on Red's front foot while he hops around
red.pose(13.28, "hit", 0.05)
red.stay(13.28)
for i in range(3):
    red.jump(13.28 + 0.14 * i, 13.42 + 0.14 * i, 470 + (6 if i % 2 else -6), FLOOR, 7)
red.face(13.43, -1)
red.face(13.58, 1)
bear.pos.hold(13.28)
for tt in [13.28 + 0.02 * i for i in range(1, 22)]:
    rx, ry = eval_num(red.pos, tt)
    bear.pos.add(tt, (rx + 12, ry))
bear.rot.add(13.29, -25, "out")
for i in range(1, 6):
    bear.rot.add(13.29 + 0.08 * i, -25 + (12 if i % 2 else -12))
red.pose(13.72, "kick", 0.06, "snap")
bear.rot.add(13.74, 0.0, "out")
bear.hop(13.74, 13.98, 622, FLOOR, 50)
bear.rot.add(13.98, 40, "in")
bear.rot.add(14.06, -15, "out")
bear.rot.add(14.12, 0, "inout")
dust(622, FLOOR, 13.98)
poof(622, FLOOR - 6, 14.1, 0.9)
bear.op.set(14.12, 0)
red.pose(13.84, "guard", 0.1)

# shadow clones
red.pose(13.96, "sign", 0.12)
red.jitter(13.96, 14.14, 0.5)
for cl, x, fc in ((c1, 520, 1), (c2, 690, -1), (c3, 760, -1)):
    cl.put(0, x, FLOOR)
    cl.sx.set(0, fc)
    cl.show(14.16)
    poof(x, FLOOR - 14, 14.14, 1.2)
jolt(14.14, 1)
red.pose(14.28, "guard", 0.12)
c1.pose(14.22, "crouch", 0.06)
c1.run(14.28, 14.48, 580)
c1.pose(14.54, "punch", 0.05, "snap")
c2.pose(14.22, "crouch", 0.06)
c2.takeoff(14.28)
c2.jump(14.28, 14.54, 614, FLOOR - 8, 28)
c2.pose(14.34, "fkick", 0.06)
ink.pose(14.42, "crouch", 0.06)
tt = hit(14.54, 598, 262 - 17, 12, c1, c2, big=True, shake=2.5)
c1.pose(tt + 0.01, "hit", 0.03)
c2.pose(tt + 0.01, "hit", 0.03)
c1.jump(tt, 14.82, 500, FLOOR, 18)
c2.jump(tt, 14.82, 700, FLOOR, 18)
c1.spin(tt, 14.82, -180, "out")
c2.spin(tt, 14.82, 180, "out")
poof(500, FLOOR - 14, 14.82, 1.1)
poof(700, FLOOR - 14, 14.82, 1.1)
c1.hide(14.84)
c2.hide(14.84)
ink.pose(14.72, "stand", 0.1)
ink.face(14.77, 1)
# the late clone
c3.run(14.24, 14.82, 660, frame=0.08)
c3.land(14.82, 0.15, pose="stand")
dust(660, FLOOR, 14.82)
c3.pose(14.92, "stand", 0.08)
c3.pose(15.04, "scratch", 0.12)
mark("...", 660, FLOOR - 44, 15.1, 0.45)
c3.pose(15.28, "shrug", 0.12, "inout")
c3.pose(15.4, "wave1", 0.08)
c3.pose(15.48, "wave2", 0.06)
c3.pose(15.56, "wave1", 0.06)
poof(660, FLOOR - 14, 15.6, 1.1)
c3.hide(15.62)

# the real Red charges; Ink leaps up and left and hovers; his eyes light up.
# Red grabs the katana out of the floor, slams it into the ground in front of him: WINDWALL.
# The laser hits the wall and is swallowed. Ink dives in a flying kick straight through the wall,
# which bursts, and the kick carries Red into the right wall.
red.pose(15.23, "crouch", 0.08)
red.face(15.28, 1)
red.takeoff(15.33)
red.run(15.33, 15.62, 548, frame=0.06)
red.land(15.62, 0.2, pose="stand")
dust(548, FLOOR, 15.62)
red.pose(15.72, "fall", 0.1)
mark("?", *red.head_mark(15.77), 15.76, 0.4)
INK_AIR = (300.0, 118.0)
ink.pose(15.28, "crouch", 0.08)
ink.takeoff(15.36, 0.18)
ink.stay(15.36)
ink.jump(15.36, 15.66, INK_AIR[0], INK_AIR[1], 40)
ink.face(15.4, 1)
ink.pose(15.4, "fly", 0.1)
trail(ink, 15.37, 15.63, "fg", 4)
dust(596, FLOOR, 15.36)
ink.idle(15.66, 16.5, "fly", 0.14)
EYE_X, EYE_Y = ink.world(15.85, "H")
EYE_X += 3.2
EYE_Y -= 0.8
EYES_OP = Track(0)
EYES_OP.set(15.78, 1)
EYES_OP.hold(16.5)
EYES_OP.add(16.62, 0, "in")
spark(EYE_X, EYE_Y, 15.86, 9, kind="white")
impact_lines(EYE_X, EYE_Y, 15.86, big=True, colour="laser")
jolt(15.86, 0.8)
# Red sees it coming: sprint to the katana, yank it out, plant it. WINDWALL.
red.pose(15.86, "crouch", 0.06)
red.face(15.86, 1)
red.run(15.9, 16.02, SWX + 2, frame=0.06)
red.face(16.02, -1)
red.pose(16.06, "tug1", 0.06)
red.weapon(16.14, True)
red.pose(16.16, "sw_up", 0.1, "snap")
spark(STUCK_HILT[0], STUCK_HILT[1], 16.12, 7, kind="white")
dust(STUCK_TIP[0] - 4, FLOOR, 16.12)
T_WW = 16.3
red.pose(T_WW, "ww_cast", 0.12, "snap")
red.sq.hold(T_WW - 0.001)
red.sq.add(T_WW + 0.05, (1.08, 0.94), "out")
red.sq.add(T_WW + 0.2, (1.0, 1.0), "inout")
jolt(T_WW, 1.6)
WW_X = SWX - 62          # centre of the wall, out in front of Red
WW_T0, WW_T1 = T_WW, 17.06
LASER_T0, LASER_T1 = 16.42, 16.72
LASER_END = Track((EYE_X, EYE_Y))
LASER_END.hold(LASER_T0 - EPS)
LASER_END.add(LASER_T0, (EYE_X + 40.0, EYE_Y + 30.0))
LASER_END.add(LASER_T0 + 0.06, (WW_X - 46.0, float(FLOOR) - 30), "out")
LASER_END.hold(LASER_T1)
LASER_OP = Track(0)
LASER_OP.set(LASER_T0, 1)
LASER_OP.hold(LASER_T1)
LASER_OP.add(LASER_T1 + 0.06, 0, "in")
flash(LASER_T0, 0.05, 0.35, colour="void_fg")
jolt(LASER_T0, 1.5)
rumble(LASER_T0 + 0.08, LASER_T1, 0.5, 0.9)


def laser_svg(p):
    pts = lambda v: f"{n(EYE_X)},{n(EYE_Y)} {n(v[0])},{n(v[1])}"
    beams = ""
    for w, col, alpha in ((16, "laser", 0.18), (7, "laser", 0.6), (2.6, "void_fg", 1.0)):
        beams += (f'<polyline fill="none" stroke="{p[col]}" stroke-width="{w}" stroke-linecap="round" opacity="{alpha}" points="{pts((EYE_X, EYE_Y))}">'
                  + animate("points", LASER_END, pts) + "</polyline>")
    tip_sc = Track(1.0)
    t = LASER_T0
    k = 0
    while t < LASER_T1:
        tip_sc.add(t, 1.3 if k % 2 else 0.8)
        t += 0.045
        k += 1
    tip = ('<g>' + animate_tf("translate", LASER_END, f_xy) + "<g>" + animate_tf("scale", tip_sc, f_ss)
           + f'<circle r="7" fill="{p["laser"]}" opacity="0.5"/><circle r="3.5" fill="{p["void_fg"]}"/></g></g>')
    eyes = (f'<g opacity="0">' + animate("opacity", EYES_OP, str)
            + f'<circle cx="{n(EYE_X - 1.6)}" cy="{n(EYE_Y)}" r="1.5" fill="{p["void_fg"]}" stroke="{p["laser"]}" stroke-width="0.8"/>'
            + f'<circle cx="{n(EYE_X + 1.8)}" cy="{n(EYE_Y + 0.4)}" r="1.5" fill="{p["void_fg"]}" stroke="{p["laser"]}" stroke-width="0.8"/></g>')
    return '<g opacity="0">' + animate("opacity", LASER_OP, str) + beams + tip + "</g>" + eyes


layer("fx_high", laser_svg)


def windwall_svg(p):
    """Yasuo's Wind Wall. A WIDE, low wall of glowing cyan wind that shoots out from the blade tip over
    0.25 s and then drifts slowly forward. It is built from horizontal bands of wind, sheared into a
    forward-leaning crest, with a bright inner core and a soft outer glow. Bands scroll upward and
    the crest curls over. It tears apart when Ink kicks through."""
    WALL_H, HALF = 58, 42
    wind, hi = p["wind"], p["wind_hi"]
    # travel: launches from the blade tip, shoots to its stand-off, then drifts
    x0 = red.world(T_WW, "WT")[0]
    travel = Track((x0 - WW_X, 0.0))
    travel.hold(WW_T0)
    travel.add(WW_T0 + 0.25, (0.0, 0.0), "out")
    travel.add(WW_T1, (-10.0, 0.0), "lin")
    # the wall grows out of the floor: scaleY 0 -> 1 fast, with a little overshoot. scaleX bursts on break.
    shape = Track((0.15, 0.0))
    shape.hold(WW_T0)
    shape.add(WW_T0 + 0.1, (1.0, 1.15), "out")
    shape.add(WW_T0 + 0.2, (1.0, 0.95), "inout")
    shape.add(WW_T0 + 0.3, (1.0, 1.0), "inout")
    shape.hold(WW_T1)
    shape.add(WW_T1 + 0.1, (1.3, 1.25), "out")
    op = Track(0)
    op.set(WW_T0, 1)
    op.hold(WW_T1)
    op.add(WW_T1 + 0.12, 0, "in")
    out = [f'<g transform="translate({n(WW_X)},{n(FLOOR)})"><g opacity="0">', animate("opacity", op, str),
           "<g>", animate_tf("translate", travel, f_xy), "<g>", animate_tf("scale", shape, lambda v: f"{f_s(v[0])} {f_s(v[1])}")]
    # the silhouette: a wide wave that leans forward (toward -x, where the beam comes from) and curls at the crest
    LEAN = -14
    sil = (f"M{-HALF},0 C{-HALF - 6},{n(-WALL_H * .45)} {-HALF + LEAN - 10},{n(-WALL_H * .8)} {-HALF + LEAN + 6},{n(-WALL_H)} "
           f"C{-HALF + LEAN + 14},{n(-WALL_H - 9)} {-HALF + LEAN + 24},{n(-WALL_H - 6)} {-HALF + LEAN + 26},{n(-WALL_H + 2)} "
           f"L{HALF + LEAN - 4},{n(-WALL_H + 2)} C{HALF + LEAN + 10},{n(-WALL_H * .7)} {HALF + 4},{n(-WALL_H * .3)} {HALF},0 Z")
    # soft outer glow, body, bright core (thin, nearer the front face)
    out.append(f'<path d="{sil}" fill="{wind}" opacity="0.07" transform="scale(1.06 1.05)"/>')
    out.append(f'<path d="{sil}" fill="{wind}" opacity="0.13"/>')
    # a torn crest: tongues of wind curling forward off the top edge
    for i in range(7):
        tx_ = -HALF + LEAN + 10 + i * 12 + (rnd(i * 3 + 8) - 0.5) * 5
        th_ = 7 + 7 * rnd(i * 5 + 2)
        tongue = f"M{n(tx_)},{n(-WALL_H + 3)} C{n(tx_ - 3)},{n(-WALL_H - th_ * .5)} {n(tx_ - 9)},{n(-WALL_H - th_)} {n(tx_ - 12)},{n(-WALL_H - th_ * .7)}"
        flick = Track(0.0)
        t_ = WW_T0
        k = 0
        while t_ < WW_T1:
            flick.add(t_, (0.0 if k % 2 == 0 else -4.0), "inout")
            t_ += 0.11 + 0.04 * rnd(i + k)
            k += 1
        out.append(f'<path d="{tongue}" fill="none" stroke="{hi}" stroke-width="{n(1.4 + rnd(i) * 1.2)}" stroke-linecap="round" opacity="0.9">'
                   + animate_tf("translate", flick, lambda v: f"{n(v)} 0") + "</path>")
    # the leading face: a crisp bright edge the beam slams into
    face = (f"M{-HALF},0 C{-HALF - 6},{n(-WALL_H * .45)} {-HALF + LEAN - 10},{n(-WALL_H * .8)} {-HALF + LEAN + 6},{n(-WALL_H)}")
    out.append(f'<path d="{face}" fill="none" stroke="{hi}" stroke-width="2.2" stroke-linecap="round" opacity="0.95"/>')
    out.append(f'<path d="{face}" fill="none" stroke="{wind}" stroke-width="5" stroke-linecap="round" opacity="0.35"/>')
    # horizontal wind bands that rise through the wall and shear forward as they climb; they loop on their own clocks
    BANDS = 14
    PERIOD = 0.46
    for i in range(BANDS):
        phase = rnd(i * 7 + 3)
        L0 = HALF * (1.3 + 0.5 * rnd(i * 3 + 1))
        w = 1.1 + 1.6 * rnd(i * 5 + 2)
        tr, o, sx = Track((0.0, 0.0)), Track(0.0), Track(1.0)
        t = WW_T0 - PERIOD * phase
        k = 0
        while t < WW_T1 + 0.2:
            for j in range(0, 6):
                s_ = j / 5
                tt = t + PERIOD * s_
                if tt < WW_T0 or (j == 0 and k > 0):
                    continue
                y = -WALL_H * (0.04 + 0.92 * s_)
                x = LEAN * s_ + (rnd(i + k) - 0.5) * 6
                tr.add(tt, (x, y), "lin")
                o.add(tt, (0.45 + 0.5 * rnd(i * 9 + k)) * (min(1.0, s_ * 3) if s_ < 0.75 else (1 - s_) / 0.25), "lin")
                sx.add(tt, 0.7 + 0.3 * s_, "lin")
            t += PERIOD
            k += 1
        out.append('<g opacity="0">' + animate("opacity", o, f_s) + animate_tf("translate", tr, f_xy) + "<g>"
                   + animate_tf("scale", sx, lambda v: f"{f_s(v)} 1")
                   + f'<path d="M{n(-L0 / 2)},0 Q{n(-L0 / 4)},{n(-w * 1.5)} 0,0 T{n(L0 / 2)},0" fill="none" stroke="{hi if i % 3 else wind}" stroke-width="{n(w)}" stroke-linecap="round"/></g></g>')
    # crest curls: three spirals rolling over the top edge, forward
    for i in range(3):
        cx_ = -HALF + LEAN + 14 + i * 26
        rot = Track(0.0)
        rot.hold(WW_T0)
        rot.add(WW_T1 + 0.2, -(900 + 300 * i), "lin")
        out.append(f'<g transform="translate({n(cx_)},{n(-WALL_H - 2)})"><g>' + animate_tf("rotate", rot, lambda a: f"{n(a)} 0 0")
                   + f'<path d="M0,0 C5,-2 7,-7 3,-9 C-2,-11 -7,-7 -5,-2" fill="none" stroke="{hi}" stroke-width="1.6" stroke-linecap="round" opacity="0.9"/></g></g>')
    # the ground line: a glow where the wall meets the floor
    out.append(f'<ellipse rx="{HALF + 6}" ry="2.0" fill="{wind}" opacity="0.28"/>')
    out.append("</g></g></g></g>")
    return "".join(out)


layer("fx_mid", windwall_svg)
dust(WW_X, FLOOR, WW_T0, big=True)
# the wall tearing: streaks fly outward
for i in range(10):
    a = math.radians(-150 + 30 * i)
    r0 = 10 + 8 * rnd(i + 30)
    smear_line(WW_X - 10 + r0 * math.cos(a), FLOOR - 30 + r0 * math.sin(a) * 1.2, WW_X - 10 + (r0 + 40) * math.cos(a), FLOOR - 30 + (r0 + 40) * math.sin(a) * 1.2, WW_T1 + 0.01, 1.6 + rnd(i) * 1.2, 0.16, colour="wind")
# the beam hits the wall: it churns, nothing gets through
for i in range(6):
    spark(WW_X - 46 + (rnd(i * 5) - 0.5) * 8, FLOOR - 30 + (rnd(i * 9) - 0.5) * 20, LASER_T0 + 0.06 + 0.05 * i, 5, kind="white", dur=0.16)
red.idle(T_WW + 0.2, 17.0, "ww_cast", 0.3)
# Ink stops the beam, dives through the wall with a flying kick. The wall bursts.
ink.pose(16.74, "crouch", 0.1)
ink.takeoff(16.82, 0.2)
ink.stay(16.82)
ink.at(17.06, WW_X - 30, FLOOR - 30, "in")
ink.pose(16.86, "fkick", 0.08)
trail(ink, 16.84, 17.05, "fg", 4)
ink.at(17.18, SWX + 2 - 18, FLOOR - 24, "lin")
for i in range(8):
    a = i * math.pi / 4 + 0.2
    spark(WW_X + 14 * math.cos(a), FLOOR - 46 + 40 * math.sin(a), WW_T1 + 0.02 + 0.02 * (i % 3), 6, kind="white", dur=0.2)
flash(WW_T1, 0.05, 0.3)
jolt(WW_T1, 1.4)
_f = ink.world(17.18, "RF")
red.pose(17.18, "hit", EPS)
red.weapon(17.18, False)
tt = hit(17.18, _f[0] + 2, _f[1], 12, ink, red, big=True, shake=3)
# the katana flies out of Red's hand on the kick, tumbles once, and spears into the floor behind him
K2_HILT, K2_TIP = (SWX + 58, FLOOR - 25), (SWX + 70, FLOOR + 7)
T_K2 = 17.5


def thrown_katana_svg(p):
    """From Red's hand at the kick to the lodge point: a parabola with a 1.5-turn tumble."""
    x0, y0 = red.world(17.17, "RH")
    tx, ty = K2_HILT
    tr, rot, op = Track((x0, y0)), Track(0.0), Track(0)
    op.set(17.18, 1)
    for i in range(1, 11):
        s_ = i / 10
        tr.add(17.18 + (T_K2 - 17.18) * s_, (x0 + (tx - x0) * s_, y0 + (ty - y0) * s_ - 4 * 42 * s_ * (1 - s_)))
        rot.add(17.18 + (T_K2 - 17.18) * s_, 540 * s_)
    op.hold(T_K2)
    op.add(T_K2 + EPS, 0)
    # the blade drawn hilt-at-origin, tip pointing where the lodged one will point
    dx, dy = K2_TIP[0] - K2_HILT[0], K2_TIP[1] - K2_HILT[1]
    parts = katana_parts(dict(RH=(0, 0), WT=(dx, dy)))
    return ('<g opacity="0">' + animate("opacity", op, str) + animate_tf("translate", tr, f_xy) + "<g>"
            + animate_tf("rotate", rot, lambda a: f"{n(a)} 0 0") + katana_svg(parts, p) + "</g></g>")


layer("props", thrown_katana_svg)
stuck_katana(K2_HILT, K2_TIP, T_K2, FADE, seed=4)
dust(K2_TIP[0] - 4, FLOOR, T_K2, big=True)
impact_lines(K2_TIP[0], FLOOR, T_K2, big=False)
jolt(T_K2, 1.2)
T_WALL = tt + 0.36
red.jump(tt, T_WALL, 818, FLOOR - 42, 10)
red.spin(tt, T_WALL, 360, "out")
wallR, _ = crack_set(W, FLOOR - 42, 70, 7, seed=21, span=(math.pi * 0.55, math.pi * 1.45), yscale=1.0,
                     rings=(0.5, 0.8), t_show=T_WALL, prop=0.08, width=1.0, colour="crack")
layer("cracks", wallR)
spark(822, FLOOR - 42, T_WALL, 11)
impact_lines(824, FLOOR - 42, T_WALL, big=False)
jolt(T_WALL, 3)
red.stay(T_WALL + 0.17)
red.at(T_WALL + 0.47, 818, FLOOR, "in")
red.pose(T_WALL + 0.47, "lying", 0.06)
# Ink lands, smoke curling off his eyes
ink.at(17.46, 596, FLOOR, "in")
ink.land(17.46, 0.3)
dust(596, FLOOR, 17.46)
_hd = ink.world(17.62, "H")
for i in range(3):
    dust(_hd[0] + 3, _hd[1] - 2, 17.52 + 0.14 * i, up=True)
ink.pose(17.62, "stand", 0.1)
ink.face(17.62, 1)
ink.pose(17.72, "hips", 0.1)
ink.idle(17.72, 18.33, "hips", 0.3)

# ================================================================ ACT 5  charm, the long wind-up, the wall  (17.08 - 25.48)
red.pose(17.13, "crouch", 0.15, "inout")
red.pose(17.38, "dizzy", 0.12)
red.wobble(17.38, 17.68, 6, 0.15)
red.pose(17.58, "stand", 0.1)
red.face(17.58, -1)
red.run(17.6, 17.76, 790, frame=0.055)
red.pose(17.78, "whistle", 0.1)
red.pose(17.96, "kiss2", 0.06, "snap")
HEART_PATH = "M0,-3.2 C-1.6,-6.4 -6.4,-5.6 -6.4,-1.6 C-6.4,1.6 -2.4,4 0,6.4 C2.4,4 6.4,1.6 6.4,-1.6 C6.4,-5.6 1.6,-6.4 0,-3.2 Z"
_h0 = red.world(17.98, "RH")
_h1 = (ink.x(17.98), FLOOR - 26)
HEART = dict(tr=Track(_h0), op=Track(0), sc=Track(0.6))
HEART["op"].set(17.98, 1)
for i in range(1, 17):
    s = i / 16
    HEART["tr"].add(17.98 + 0.4 * s, (_h0[0] + (_h1[0] - _h0[0]) * s,
                                     _h0[1] + (_h1[1] - _h0[1]) * s - math.sin(s * math.pi * 3) * 9 - 10 * math.sin(s * math.pi)))
    HEART["sc"].add(17.98 + 0.4 * s, 1.0 + 0.25 * math.sin(s * 14))
HEART["op"].hold(18.38)
HEART["op"].add(18.44, 0, "in")
HEART["sc"].add(18.44, 2.2, "out")


def heart_svg(p):
    return ('<g opacity="0">' + animate("opacity", HEART["op"], str) + animate_tf("translate", HEART["tr"], f_xy) + "<g>"
            + animate_tf("scale", HEART["sc"], f_ss) + f'<path d="{HEART_PATH}" fill="{p["pink"]}"/></g></g>')


layer("fx_high", heart_svg)
spark(_h1[0], _h1[1], 18.38, 8, kind="white")
# Ink is smitten: he goes limp, tips onto his back and floats toward Red
ink.pose(18.4, "hit", 0.04)
ink.pose(18.58, "fall", 0.1)
ink.face(18.66, -1)
ink.pose(18.73, "float", 0.22, "inout")
ink.rot_to(18.68, 18.98, 62, "inout", pivot=(0, -13))
ink.stay(18.68)
ink.at(18.98, 596, FLOOR - 14, "out")
ink.takeoff(18.73, 0.06)
T_DRIFT0, T_DRIFT1 = 19.03, 20.48
for i in range(1, 30):
    s = i / 29
    tt_ = T_DRIFT0 + (T_DRIFT1 - T_DRIFT0) * s
    ink.pos.add(tt_, (596 + (722 - 596) * (0.5 - 0.5 * math.cos(s * math.pi)), FLOOR - 14 - 4 * math.sin(s * 9)))
ink.wobble(19.03, 20.48, 4, 0.5, base=62)
FLOAT_HEARTS = []
for j, (ox, oy, ph) in enumerate(((-10, -12, 0.0), (0, -20, 1.0), (10, -14, 2.0))):
    tr, op, sc = Track((0.0, 0.0)), Track(0), Track(1.0)
    t0 = 18.42 + 0.05 * j
    op.set(t0, 1)
    tr.set(t0, (ink.x(t0) + ox, FLOOR - 30 + oy))
    t_ = t0
    while t_ < 20.58:
        t_ += 0.05
        ix, iy = eval_num(ink.pos, t_)
        hx_ = ix + 17 + ox            # the head leads, tilted up
        tr.add(t_, (hx_, iy - 20 + oy + 2.5 * math.sin(t_ * 9 + ph)))
    sc.hold(20.58)
    sc.add(20.7, 1.8, "out")
    op.hold(20.58)
    op.add(20.7, 0, "in")
    FLOAT_HEARTS.append((tr, op, sc))


def float_hearts_svg(p):
    return "".join('<g opacity="0">' + animate("opacity", op, str) + animate_tf("translate", tr, f_xy) + "<g>"
                   + animate_tf("scale", sc, lambda s: f_ss(s * 0.8))
                   + f'<path d="{HEART_PATH}" fill="{p["pink"]}"/></g></g>' for tr, op, sc in FLOAT_HEARTS)


layer("fx_high", float_hearts_svg)
# the wind-up. And the wind-up. The page starts to rumble.
red.pose(18.08, "guard", 0.1)
red.pose(18.93, "windup", 0.16, "inout")
red.pose(19.58, "windup2", 0.4, "inout")
red.jitter(19.23, 19.88, 0.35, 24, amp1=0.7)
red.jitter(19.88, 20.56, 0.7, 26, amp1=1.4)
FIST_X, FIST_Y = red.world(20.18, "RH")
T_CH0, T_CH1 = 19.53, 20.56


def charge_svg(p):
    out = [f'<g transform="translate({n(FIST_X)},{n(FIST_Y)})">']
    for r, phase in ((12, 0.0), (6, 0.15)):
        sc, op = Track(1.0), Track(0)
        op.set(T_CH0 + phase, 0.6)
        t_ = T_CH0 + phase
        k = 0
        while t_ < T_CH1:
            sc.add(t_, 1.0 if k % 2 == 0 else 0.45, "in")
            t_ += 0.15
            k += 1
        op.hold(T_CH1)
        op.add(T_CH1 + 0.04, 0)
        out.append('<g opacity="0">' + animate("opacity", op, str) + animate_tf("scale", sc, f_ss)
                   + f'<circle r="{r}" fill="none" stroke="{p["red"]}" stroke-width="1.6"/></g>')
    for i in range(8):
        a = i * math.pi / 4 + 0.3
        r0, r1 = 17 + 4 * rnd(i), 24 + 6 * rnd(i + 7)
        fl = Track(0)
        fl.hold(T_CH0 + 0.3)
        t_ = T_CH0 + 0.3 + 0.07 * rnd(i * 3)
        k = 0
        while t_ < T_CH1:
            fl.add(t_, 0.9 if k % 2 == 0 else 0.1)
            t_ += 0.06 + 0.05 * rnd(i + k)
            k += 1
        fl.add(T_CH1 + 0.02, 0)
        out.append(f'<path d="M{n(r0 * math.cos(a))},{n(r0 * math.sin(a))} L{n(r1 * math.cos(a))},{n(r1 * math.sin(a))}" '
                   f'stroke="{p["red"]}" stroke-width="1.8" stroke-linecap="round" opacity="0">' + animate("opacity", fl, f_s) + "</path>")
    out.append("</g>")
    return "".join(out)


layer("fx_high", charge_svg)
rumble(19.98, 20.56, 0.3, 1.1)
dust(790 - 12, FLOOR, 19.93)
dust(790 - 12, FLOOR, 20.28)
# MEGA PUNCH. Red lunges a full step into it.
red.pose(20.58, "mega", 0.04, "snap")
red.stay(20.56)
red.at(20.6, 790 - 22, FLOOR, "snap")
_a, _b = red.world(20.55, "RH"), red.world(20.61, "RH")
smear_line(_a[0] - 6, _a[1], _b[0] - 4, _b[1], 20.58, 8, 0.09)
trail(red, 20.565, 20.595, "red", 2)
ink.pose(20.6, "hit", EPS)
tt = hit(20.6, _b[0] - 6, _b[1] + 1, 17, ink, red, big=True, dur=0.12, shake=5)
flash(tt - 0.02, 0.05, 0.4, colour="void_fg")
red.pose(20.74, "mega2", 0.06, "out")
red.pose(20.96, "guard", 0.14, "inout")
red.stay(20.96)
red.at(21.08, 790, FLOOR, "inout")
ink.rot_pivot(tt - 0.001)
ink.jump(tt, 21.12, 14, FLOOR - 40, 8)
ink.spin(tt, 21.12, -782)        # 62 - 782 = -720: lands upright
wallL, _ = crack_set(0, FLOOR - 40, 70, 7, seed=31, span=(-math.pi * 0.45, math.pi * 0.45), yscale=1.0,
                     rings=(0.5, 0.8), t_show=21.12, prop=0.08, width=1.0, colour="crack")
layer("cracks", wallL)
spark(8, FLOOR - 40, 21.12, 11)
impact_lines(6, FLOOR - 40, 21.12, big=False)
jolt(21.12, 3)
ink.stay(21.3)
ink.at(21.6, 14, FLOOR, "in")
ink.pose(21.6, "lying", 0.06)
ink.face(21.6, -1)

# Ink gets up angry; Red builds a wall
ink.pose(21.96, "crouch", 0.15, "inout")
ink.pose(22.16, "stand", 0.1)
ink.face(22.16, 1)
ink.pose(22.23, "guard", 0.08)
ink.jitter(22.23, 22.46, 0.6)
red.pose(22.06, "fall", 0.06)
mark("!", *red.head_mark(22.11), 22.08, 0.4)
red.run(22.16, 22.29, 800, frame=0.065)
red.pose(22.33, "place_lo", 0.08)
BLOCKS = [(748 + col * 16, FLOOR - 8 - row * 16, 22.37 + 0.1 * i)
          for i, (col, row) in enumerate(((0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)))]
for bx, by, bt in BLOCKS:
    red.pose(bt - 0.02, "place_hi" if by < FLOOR - 24 else "place_lo", 0.07, "snap")
red.pose(23.01, "cover", 0.12, "inout")
red.idle(23.01, 24.38, "cover", 0.5)
WALL_ROT = Track((0.0, 772.0, float(FLOOR)))
WALL_OP = Track(1)


def block_svg(p, seed):
    out = []
    for r in range(8):
        for c in range(8):
            if r < 2:
                col = BLOCK_GREEN[int(rnd(seed * 17 + r * 8 + c) * 3)]
            elif r == 2 and rnd(seed * 5 + c) < 0.45:
                col = BLOCK_GREEN[2]
            else:
                col = BLOCK_BROWN[int(rnd(seed * 23 + r * 8 + c) * 4)]
            out.append(f'<rect x="{-8 + c * 2}" y="{-8 + r * 2}" width="2" height="2" fill="{col}"/>')
    out.append('<rect x="-8" y="-8" width="16" height="16" fill="none" stroke="#3b2414" stroke-width="0.8" opacity="0.6"/>')
    return "".join(out)


def wall_svg(p):
    out = ['<g opacity="1">' + animate("opacity", WALL_OP, str) + "<g>" + animate_tf("rotate", WALL_ROT, f_rot)]
    for i, (bx, by, bt) in enumerate(BLOCKS):
        sc = Track(0.0)
        sc.hold(bt - EPS)
        sc.add(bt, 0.2)
        sc.add(bt + 0.07, 1.18, "out")
        sc.add(bt + 0.14, 1.0, "inout")
        out.append(f'<g transform="translate({n(bx)},{n(by)})"><g>' + animate_tf("scale", sc, f_ss) + block_svg(p, i + 1) + "</g></g>")
    out.append("</g></g>")
    return "".join(out)


layer("props", wall_svg)
for i, (bx, by, bt) in enumerate(BLOCKS):
    spark(bx, by, bt, 5, kind="white", dur=0.16)

# FLASH STEP. Ink lifts his front foot, sets it down slowly... and the moment it touches he is gone.
# A gust of wind where he stood, afterimages across the page, and he is standing at the wall.
ink.pose(22.5, "plant", 0.2, "inout")
ink.pose(22.92, "plant2", 0.4, "inout")           # the foot comes down slowly
ink.stay(22.92)
T_FLASH = 22.95
dust(14 - 5, FLOOR, T_FLASH, big=True)
ink.at(T_FLASH + 0.07, 724, FLOOR, "snap")
ink.pose(T_FLASH, "dash", 0.03)
trail(ink, T_FLASH + 0.005, T_FLASH + 0.065, "fg", 5)
ink.pose(T_FLASH + 0.08, "stand", 0.02)
dust(724 - 8, FLOOR, T_FLASH + 0.07)
mark("?", *red.head_mark(T_FLASH + 0.3), T_FLASH + 0.25, 0.5)        # Red, behind the wall, lost him


def gust_svg(p):
    """Wind streaks that whip across the page in Ink's wake, left to right, and fade."""
    out = []
    for i, (y, L, delay) in enumerate(((FLOOR - 24, 150, 0.0), (FLOOR - 14, 220, 0.02), (FLOOR - 30, 110, 0.04), (FLOOR - 8, 170, 0.01), (FLOOR - 19, 90, 0.06))):
        t0 = T_FLASH + delay
        tr = Track((0.0, 0.0))
        tr.set(t0, (0.0, 0.0))
        tr.add(t0 + 0.26, (560.0, 0.0), "out")
        op = Track(0)
        op.set(t0, 0.55)
        op.hold(t0 + 0.12)
        op.add(t0 + 0.26, 0, "in")
        sx = Track(0.3)
        sx.hold(t0)
        sx.add(t0 + 0.08, 1.0, "out")
        sx.add(t0 + 0.26, 0.4, "in")
        out.append(f'<g transform="translate(20,{n(y)})"><g opacity="0">' + animate("opacity", op, str) + animate_tf("translate", tr, f_xy)
                   + "<g>" + animate_tf("scale", sx, lambda v: f"{f_s(v)} 1")
                   + f'<path d="M0,0 h{L}" stroke="{p["fg"]}" stroke-width="{n(1.6 + 0.6 * rnd(i))}" stroke-linecap="round"/></g></g></g>')
    return "".join(out)


layer("fx_low", gust_svg)
ink.pose(23.3, "hips", 0.12)
ink.idle(23.3, 23.6, "hips", 0.3)
# knock knock. The wall wobbles. He leans in with both hands and pushes it over.
ink.pose(23.64, "tap", 0.08)
ink.pose(23.76, "tap2", 0.05)
ink.pose(23.88, "tap", 0.05)
ink.pose(24.0, "stand", 0.1)
ink.pose(24.12, "push", 0.1, "inout")
ink.stay(24.1)
ink.at(24.44, 724 + 6, FLOOR, "in")               # he leans a step into it as it goes
WALL_ROT.hold(23.66)
for i, a in enumerate((-1.2, 1.4, -1.0, 1.2, -0.6, 0)):
    WALL_ROT.add(23.69 + 0.06 * i, (a, 772.0, float(FLOOR)))
WALL_ROT.hold(24.12)
WALL_ROT.add(24.2, (3.0, 772.0, float(FLOOR)), "out")       # it starts to go
WALL_ROT.add(24.44, (90.0, 772.0, float(FLOOR)), "in")
T_BURY = 24.44
WALL_OP.set(T_BURY, 0)
jolt(T_BURY, 2.4)
dust(796, FLOOR, T_BURY, big=True)
impact_lines(796, FLOOR - 8, T_BURY, big=False)
red.pose(T_BURY, "lying", 0.04)
red.face(T_BURY, 1)
PILE_TR = Track((0.0, 0.0))
PILE_TR.hold(24.7)
for i in range(1, 9):
    PILE_TR.add(24.7 + 0.03 * i, (1.6 * (rnd(i * 2.3) - 0.5) * 2, 1.2 * (rnd(i * 4.1) - 0.5) * 2))
PILE_TR.add(24.96, (0.0, 0.0))
# fallen positions: block i turned 90 degrees about (772, FLOOR)
LOOSE = []
for i, (bx, by, bt) in enumerate(BLOCKS):
    dx, dy = bx - 772, by - FLOOR
    lx, ly = 772 - dy, FLOOR + dx
    tr, rt, op = Track((lx, ly)), Track(90.0), Track(0)
    op.set(T_BURY, 1)
    LOOSE.append([tr, rt, op, i, lx, ly])


def throw_block(i, t, x1, y1, h, drot, dur=0.3):
    tr, rt, op, _, lx, ly = LOOSE[i]
    tr.hold(t)
    rt.hold(t)
    x0, y0 = tr.v
    r0 = rt.v
    for j in range(1, 8):
        s = j / 7
        tr.add(t + dur * s, (x0 + (x1 - x0) * s, y0 + (y1 - y0) * s - 4 * h * s * (1 - s)))
        rt.add(t + dur * s, r0 + drot * s)
    tr.add(t + dur + 0.1, (x1 + 4, y1 - 3), "out")
    rt.add(t + dur + 0.1, rt.v + 8, "out")
    tr.add(t + dur + 0.18, (x1 + 6, y1), "in")


# the pile shakes, the top block pops off, Red stands up out of it with a pickaxe
throw_block(2, 24.96, 712, FLOOR - 8, 34, -140, 0.32)
red.pose(24.93, "crouch", 0.1)
red.pose(25.06, "dig_hold", 0.12)
red.pick(25, True)
red.face(24.98, -1)
red.pose(25.2, "dig_up", 0.1)
red.pose(25.32, "dig_down", 0.05, "snap")
_pk = red.world(25.33, "WT")
spark(_pk[0], _pk[1], 25.33, 7)
dust(_pk[0], FLOOR - 6, 25.33)
jolt(25.33, 1)
throw_block(0, 25.33, 684, FLOOR - 8, 40, -220, 0.34)
throw_block(1, 25.34, 660, FLOOR - 8, 26, 160, 0.3)
red.pose(25.48, "dig_up", 0.1)
red.pose(25.6, "dig_down", 0.05, "snap")
_pk = red.world(25.61, "WT")
spark(_pk[0], _pk[1], 25.61, 7)
dust(_pk[0], FLOOR - 6, 25.61)
jolt(25.61, 1)
throw_block(3, 25.61, 826, FLOOR - 8, 30, 200, 0.3)
throw_block(4, 25.62, 760, FLOOR - 8, 44, -260, 0.36)
for i in range(6):
    LOOSE[i][2].hold(FADE[0] + 0.2)
    LOOSE[i][2].add(FADE[1] + 0.2, 0, "in")


def loose_svg(p):
    return ('<g>' + animate_tf("translate", PILE_TR, f_xy)
            + "".join('<g opacity="0">' + animate("opacity", op, str) + animate_tf("translate", tr, f_xy) + "<g>"
                      + animate_tf("rotate", rt, lambda a: f"{n(a)} 0 0") + block_svg(p, i + 1) + "</g></g>"
                      for tr, rt, op, i, _, _ in LOOSE) + "</g>")


layer("over_red", loose_svg)
red.pose(25.73, "dig_hold", 0.1)
red.run(25.78, 25.98, 744, frame=0.065)
red.pose(25.98, "dig_hold", 0.08)
red.pose(26.1, "dust", 0.1)
red.pick(26.1, False)
red.pose(26.22, "dust2", 0.06)
red.pose(26.34, "guard", 0.1)
red.idle(26.34, 26.73, "guard", 0.3)
ink.pose(24.48, "dust", 0.1)
ink.pose(24.6, "dust2", 0.06)
ink.pose(24.72, "stand", 0.08)

# ================================================================ ACT 6  domain expansion  (24.88 - 29.48)
# the pile starts to shake. Ink backflips away from it: crouch, spring, a full backward somersault
# across the page, land in a crouch facing Red, and stand up slow.
ink.pose(24.9, "crouch", 0.12, "inout")
ink.takeoff(25.0, 0.2)
ink.stay(25.0)
ink.jump(25.0, 25.52, 480, FLOOR, 78)
ink.pose(25.06, "fall", 0.06)
ink.pose(25.14, "tuck", 0.08)
ink.pose(25.42, "fall", 0.1)
ink.spin(25.02, 25.5, -360, "inout")
trail(ink, 25.1, 25.4, "fg", 3)
ink.land(25.52, 0.3)
dust(480, FLOOR, 25.52, big=True)
jolt(25.52, 1)
ink.pose(25.64, "sign", 0.16, "inout")
SIGN_X, SIGN_Y = ink.world(25.84, "RH")
SIGN_Y -= 2
HEAD_X, HEAD_Y = ink.world(25.84, "H")
T_CHARGE, T_EXPAND, T_FULL, T_COLLAPSE, T_GONE = 25.7, 26.38, 26.83, 29.08, 29.48
GLOW = Track(0)
GLOW.hold(T_CHARGE)
for i in range(1, 9):
    GLOW.add(T_CHARGE + 0.08 * i, 0.9 if i % 2 else 0.35, "inout")
GLOW.add(T_EXPAND + 0.01, 1.0)
GLOW.add(T_EXPAND + 0.07, 0)
BUBBLE_OP = Track(0)
BUBBLE_OP.set(T_CHARGE + 0.18, 1)
BUBBLE_OP.hold(T_EXPAND - 0.05)
BUBBLE_OP.add(T_EXPAND, 0, "in")
BUBBLE_SC = Track(0.3)
BUBBLE_SC.hold(T_CHARGE + 0.18)
BUBBLE_SC.add(T_CHARGE + 0.3, 1.12, "out")
BUBBLE_SC.add(T_CHARGE + 0.4, 1.0, "inout")
BUBBLE_SC.hold(T_EXPAND - 0.05)
BUBBLE_SC.add(T_EXPAND, 1.4, "in")
jolt(T_CHARGE + 0.18, 0.8)
VOID_R = Track(0.0)
VOID_R.hold(T_EXPAND)
VOID_R.add(T_FULL, 740.0, "in")
VOID_R.hold(T_COLLAPSE)
VOID_R.add(T_GONE, 0.0, "in")
RING_OP = Track(0)
RING_OP.set(T_EXPAND, 0.9)
RING_OP.hold(T_GONE)
RING_OP.add(T_GONE + 0.05, 0)
STARS_OP = Track(0)
STARS_OP.hold(T_FULL - 0.1)
STARS_OP.add(T_FULL + 0.3, 1, "out")
STARS_OP.hold(T_COLLAPSE - 0.15)
STARS_OP.add(T_COLLAPSE + 0.05, 0, "in")
SHOCK = Track(0.0)
SHOCK.hold(T_EXPAND)
SHOCK.add(T_EXPAND + 0.3, 170.0, "out")
SHOCK_OP = Track(0)
SHOCK_OP.set(T_EXPAND, 0.9)
SHOCK_OP.add(T_EXPAND + 0.3, 0, "in")
jolt(T_EXPAND + 0.03, 2)
flash(T_EXPAND + 0.05, 0.07, 0.6, colour="void_fg")
VOID_WIN = Track(0)
VOID_WIN.set(T_EXPAND + 0.07, 1)
VOID_WIN.hold(T_GONE - 0.2)
VOID_WIN.add(T_GONE + 0.06, 0, "in")
ink.hide(T_EXPAND + 0.07)
ink.idle(25.98, 28.68, "sign", 0.6)
ink.pose(28.83, "clap", 0.14, "inout")
# Red is swallowed
red.pose(T_EXPAND + 0.07, "fall", 0.05)
red.stay(T_EXPAND + 0.2)
red.pose(T_EXPAND + 0.25, "hit", 0.06)
red.jitter(T_EXPAND + 0.25, T_EXPAND + 0.35, 0.5)
red.hitstop(T_EXPAND + 0.35, 0.08)
x0, y0 = 744, FLOOR
for i in range(1, 21):
    s_ = i / 20
    red.pos.add(T_FULL + 1.9 * s_, (x0 - 40 * s_ + 12 * math.sin(s_ * 6), y0 - 190 * s_ * s_))
red.rot_to(T_FULL, T_FULL + 1.9, -330, "lin")
red.sq.hold(T_FULL)
red.sq.add(T_FULL + 1.9, (0.12, 0.12), "in")
red.op.hold(T_FULL + 1.3)
red.op.add(T_FULL + 1.9, 0, "in")
# the void collapses into Ink's palm and takes him with it
ink.sq.hold(T_GONE - 0.25)
ink.sq.add(T_GONE + 0.05, (0.04, 0.04), "in")
spark(SIGN_X, SIGN_Y, T_GONE + 0.02, 11, kind="white")
flash(T_GONE + 0.03, 0.06, 0.5)

# the page heals while it is covered
for i, wd in enumerate([RD] + NL):
    wd.restore(RESTORE[0] + 0.03 * i, RESTORE[1] - 0.3 + 0.03 * i)
for wd in (S1, S2, S3):
    for hw in wd.halves:
        hw.restore(RESTORE[0], RESTORE[1] - 0.3)
        hw.op.set(RESTORE[1] - 0.25, 0)
    wd.op.set(RESTORE[1] - 0.25, 1)


def bubble_svg(p):
    bx, by, w, h = 20, -50, 136, 36
    body = (f'<rect x="{bx}" y="{by}" width="{w}" height="{h}" rx="7" fill="{p["bg"]}" stroke="{p["fg"]}" stroke-width="1.4"/>'
            f'<polygon points="{bx + 10},{by + h - 1} {bx + 26},{by + h - 1} {bx - 4},{by + h + 12}" fill="{p["bg"]}" stroke="{p["fg"]}" stroke-width="1.4" stroke-linejoin="round"/>'
            f'<rect x="{bx + 11}" y="{by + h - 3}" width="14" height="4" fill="{p["bg"]}"/>')
    text = (f'<text x="{bx + w / 2}" y="{by + 15}" text-anchor="middle" font-size="12.48" font-weight="700" fill="{p["fg"]}">Domain Expansion.</text>'
            f'<text x="{bx + w / 2}" y="{by + 29}" text-anchor="middle" font-size="12.48" font-weight="700" fill="{VOID_RIM}">Infinite Void.</text>')
    return (f'<g transform="translate({n(HEAD_X)},{n(HEAD_Y)})"><g opacity="0">' + animate("opacity", BUBBLE_OP, str)
            + animate_tf("scale", BUBBLE_SC, f_ss) + body + text + "</g></g>")


# ================================================================ render
def stars_svg(p):
    out = ['<g opacity="0">', animate("opacity", STARS_OP, str)]
    for i in range(52):
        x, y = rnd(i * 7 + 1) * W, rnd(i * 13 + 2) * H
        r = 0.5 + 1.2 * rnd(i * 3 + 5)
        tw = Track(0.35 + 0.5 * rnd(i))
        period = 0.5 + 0.9 * rnd(i * 17)
        t = T_FULL - 0.1 + rnd(i * 19) * period
        tw.hold(T_FULL - 0.1)
        k = 0
        while t < T_COLLAPSE:
            tw.add(t, 1.0 if k % 2 == 0 else 0.25, "inout")
            t += period / 2
            k += 1
        out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="#ffffff">' + animate("opacity", tw, f_s) + "</circle>")
    out.append("</g>")
    return "".join(out)


def ghost_text_svg(p):
    op = Track(0)
    op.hold(T_FULL)
    op.add(T_FULL + 0.35, 0.22, "out")
    op.hold(T_COLLAPSE - 0.2)
    op.add(T_COLLAPSE, 0, "in")
    out = ['<g opacity="0">', animate("opacity", op, str),
           f'<text x="0" y="{H1_Y}" font-size="32" font-weight="600" fill="#ffffff">{html.escape(H1_TEXT)}</text>',
           f'<path d="M0,{RULE_Y} H{W}" stroke="#ffffff" stroke-width="1"/>']
    for wd in ALL_WORDS:
        out.append(wd.plain("#ffffff"))
    out.append("</g>")
    return "".join(out)


def void_svg(p):
    return ('<g>'
            + f'<circle cx="{n(SIGN_X)}" cy="{n(SIGN_Y)}" r="0" fill="url(#voidg)">' + animate("r", VOID_R, n) + "</circle>"
            + ghost_text_svg(p) + stars_svg(p)
            + f'<circle cx="{n(SIGN_X)}" cy="{n(SIGN_Y)}" r="0" fill="none" stroke="{VOID_RIM}" stroke-width="2.5" opacity="0">'
            + animate("r", VOID_R, n) + animate("opacity", RING_OP, str) + "</circle>"
            + f'<circle cx="{n(SIGN_X)}" cy="{n(SIGN_Y)}" r="0" fill="none" stroke="{VOID_RIM}" stroke-width="3" opacity="0">'
            + animate("r", SHOCK, n) + animate("opacity", SHOCK_OP, str) + "</circle>"
            + "</g>")


def glow_svg(p):
    return (f'<g transform="translate({n(SIGN_X)},{n(SIGN_Y)})"><circle r="6" fill="{VOID_RIM}" opacity="0">'
            + animate("opacity", GLOW, str) + "</circle></g>")


def render(theme):
    p = PALETTES[theme]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT_STACK}">',
           '<defs><radialGradient id="holeg"><stop offset="0" stop-color="#000000"/><stop offset="0.72" stop-color="#07061a"/>'
           '<stop offset="1" stop-color="#2a2654"/></radialGradient>'
           '<radialGradient id="voidg"><stop offset="0" stop-color="#05050e"/><stop offset="0.82" stop-color="#0c0b24"/>'
           '<stop offset="1" stop-color="#2b2466"/></radialGradient>'
           f'<clipPath id="holeclip"><polygon points="{" ".join(f"{n(x)},{n(y)}" for x, y in HOLE_PTS)}"/></clipPath>'
           f'<clipPath id="pageclip"><path clip-rule="evenodd" d="M-20,-20 H{W + 20} V{H + 20} H-20 Z M{" L".join(f"{n(x)},{n(y)}" for x, y in HOLE_PTS)} Z"/></clipPath></defs>',
           f'<rect width="{W}" height="{H}" fill="{p["bg"]}"/>',
           "<g>", animate_tf("translate", FRAME, f_xy),
           f'<text x="0" y="{H1_Y}" font-size="32" font-weight="600" fill="{p["fg"]}">{html.escape(H1_TEXT)}</text>',
           f'<path d="M0,{RULE_Y} H{W}" stroke="{p["rule"]}" stroke-width="1"/>']
    for line in LINES:
        for wd in line:
            out.append(wd.all_svg(p["fg"]))
    for L in NL:
        out.append(L.svg(p["fg"]))
    out.append(hole_svg(p))
    out.extend(fn(p) for fn in LAYERS["cracks"])
    out.append('<g clip-path="url(#holeclip)">' + crawl.svg(p["red"]) + "</g>")
    out.append(RD.svg(p["fg"]))
    for name in ("debris", "props", "fx_low"):
        out.extend(fn(p) for fn in LAYERS[name])
    out.append(glow_svg(p))
    for cl in (c1, c2, c3):
        out.append(cl.svg(p["red"]))
    out.append(ink.svg(p["fg"]))
    out.extend(fn(p) for fn in LAYERS["fx_mid"])
    out.append(void_svg(p))
    out.append('<g clip-path="url(#pageclip)">' + crawl.svg(p["red"], limb_ops=True, halo=p["bg"]) + "</g>")
    out.append(hole_svg(p, edge_only=True))
    out.append(red.svg(p["red"], weapons=p, katana_win=(6.0, 17.4), pick_win=(24.8, 26.4)))
    out.extend(fn(p) for fn in LAYERS["over_red"])
    out.append(bear.svg(p))
    out.append(ink.svg(p["void_fg"], op_track=VOID_WIN))
    for name in ("fx_high", "marks", "top"):
        out.extend(fn(p) for fn in LAYERS[name])
    out.append("</g></svg>")
    return "".join(out)


if __name__ == "__main__":
    for theme in ("light", "dark"):
        svg = render(theme)
        with open(f"fight-{theme}.svg", "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"fight-{theme}.svg  {len(svg.encode()) / 1024:.0f} KB")
    print("hole:", round(HX), round(HY), "top", round(HT), "bottom", round(HB), "right", round(HR))

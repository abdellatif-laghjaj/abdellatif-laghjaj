"""Turn out/frames/*.png into the README images.

  python scripts/assemble.py            # city/commit-city.webp (the loop) + city/commit-city.png (poster)
  python scripts/assemble.py --gif      # also a smaller GIF, for people who want one

The animated WebP is what the README shows: full motion at a few MB.
A GIF of a moving camera is 5 to 10 times bigger, so it is optional.
"""
import argparse, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def run(cmd):
    subprocess.run(cmd, check=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--frames', default='out/frames')
    ap.add_argument('--fps', type=int, default=15, help='frames per second the frames were planned for')
    ap.add_argument('--webp-fps', type=int, default=12)
    ap.add_argument('--quality', type=int, default=60)
    ap.add_argument('--poster', type=int, default=90, help='frame index used as the still fallback')
    ap.add_argument('--gif', action='store_true')
    ap.add_argument('--out', default='city/commit-city')
    a = ap.parse_args()
    frames = ROOT / a.frames
    pattern = str(frames / 'frame_%04d.png')
    out = ROOT / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    base = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-framerate', str(a.fps), '-i', pattern]
    run(base + ['-vf', f'fps={a.webp_fps}', '-c:v', 'libwebp_anim', '-lossless', '0', '-q:v', str(a.quality), '-compression_level', '6', '-loop', '0', '-preset', 'picture', str(out) + '.webp'])
    shutil.copyfile(frames / f'frame_{a.poster:04d}.png', str(out) + '.png')
    if a.gif:
        palette = str(frames / 'palette.png')
        run(base + ['-vf', 'fps=10,scale=640:-1:flags=lanczos,palettegen=max_colors=192:stats_mode=full', palette])
        run(base + ['-i', palette, '-lavfi', 'fps=10,scale=640:-1:flags=lanczos [x]; [x][1:v] paletteuse=dither=none:diff_mode=rectangle', '-loop', '0', str(out) + '.gif'])
    for ext in ('.webp', '.png', '.gif'):
        p = Path(str(out) + ext)
        if p.exists():
            print(f'{p.name}: {p.stat().st_size / 1e6:.2f} MB')

if __name__ == '__main__':
    main()

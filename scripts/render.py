"""Render Commit City to PNG frames with headless Chromium, then assemble.

  python scripts/render.py --frames 1 --out out/test        # one frame, to look
  python scripts/render.py --frames 144 --out out/frames    # the loop

Frames are rendered at 1.5x and downscaled for antialiasing.
"""
import argparse, base64, http.server, io, os, socketserver, sys, threading, time
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent

def serve():
    handler = http.server.SimpleHTTPRequestHandler
    class Quiet(handler):
        def log_message(self, *a): pass
    os.chdir(ROOT)
    srv = socketserver.TCPServer(('127.0.0.1', 0), Quiet)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--frames', type=int, default=144)
    ap.add_argument('--out', default='out/frames')
    ap.add_argument('--width', type=int, default=832)
    ap.add_argument('--height', type=int, default=432)
    ap.add_argument('--scale', type=float, default=1.5)
    ap.add_argument('--start', type=float, default=0.0, help='loop position of the first frame (0..1)')
    ap.add_argument('--single', type=float, default=None, help='render one frame at this loop position')
    a = ap.parse_args()
    out = ROOT / a.out; out.mkdir(parents=True, exist_ok=True)
    srv, port = serve()
    rw, rh = int(a.width * a.scale), int(a.height * a.scale)
    with sync_playwright() as p:
        browser = p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-gpu-vsync'])
        page = browser.new_page(viewport={'width': rw, 'height': rh})
        page.on('console', lambda m: print('  [browser]', m.text) if m.type in ('error', 'warning') else None)
        page.on('pageerror', lambda e: print('  [pageerror]', e))
        page.goto(f'http://127.0.0.1:{port}/city/index.html?w={rw}&h={rh}')
        t0 = time.time()
        page.evaluate('() => window.cityReady')
        print(f'scene built in {time.time() - t0:.1f}s')
        ts = [a.single] if a.single is not None else [(a.start + i / a.frames) % 1.0 for i in range(a.frames)]
        for i, t in enumerate(ts):
            t1 = time.time()
            data = page.evaluate('t => window.cityRender(t)', t)
            png = base64.b64decode(data.split(',', 1)[1])
            im = Image.open(io.BytesIO(png)).convert('RGB')
            if a.scale != 1:
                im = im.resize((a.width, a.height), Image.LANCZOS)
            im.save(out / f'frame_{i:04d}.png', optimize=False)
            print(f'frame {i + 1}/{len(ts)} t={t:.3f} {time.time() - t1:.1f}s', flush=True)
        browser.close()
    srv.shutdown()

if __name__ == '__main__':
    main()

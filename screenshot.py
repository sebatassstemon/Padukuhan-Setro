# -*- coding: utf-8 -*-
"""Screenshot halaman dari localhost. Pemakaian: python screenshot.py http://localhost:3000 [label]"""
import sys, os, re, io
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000"
label = sys.argv[2] if len(sys.argv) > 2 else ""
lebar = int(sys.argv[3]) if len(sys.argv) > 3 else 1440

OUT = "temporary screenshots"
os.makedirs(OUT, exist_ok=True)
n = 1
for f in os.listdir(OUT):
    m = re.match(r"screenshot-(\d+)", f)
    if m:
        n = max(n, int(m.group(1)) + 1)
nama = f"screenshot-{n}{('-' + label) if label else ''}.png"
path = os.path.join(OUT, nama)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": lebar, "height": 1000}, device_scale_factor=1)
    pesan = []
    pg.on("console", lambda m: pesan.append(f"[{m.type}] {m.text}") if m.type in ("error", "warning") else None)
    pg.on("pageerror", lambda e: pesan.append(f"[pageerror] {e}"))
    pg.goto(url, wait_until="networkidle", timeout=45000)
    # gulung penuh supaya semua reveal & count-up terpicu
    pg.evaluate("""async () => {
        if (window.__lenis) { window.__lenis.destroy(); window.__lenis = null; }  // Lenis bentrok dgn scrollTo
        const html = document.documentElement;
        const asli = html.style.scrollBehavior;
        html.style.scrollBehavior = 'auto';           // smooth scroll bikin scrollTo saling menyela
        const langkah = window.innerHeight * 0.7;
        for (let y = 0; y < document.body.scrollHeight; y += langkah) {
            window.scrollTo(0, y); await new Promise(r => setTimeout(r, 120));
        }
        window.scrollTo(0, document.body.scrollHeight);
        await new Promise(r => setTimeout(r, 400));
        window.scrollTo(0, 0);
        await new Promise(r => setTimeout(r, 500));
        html.style.scrollBehavior = asli;
    }""")
    pg.wait_for_timeout(900)
    pg.screenshot(path=path, full_page=True)
    tinggi = pg.evaluate("document.body.scrollHeight")
    b.close()

print(f"tersimpan: {path}  (lebar {lebar}px, tinggi halaman {tinggi}px)")
if pesan:
    print("--- pesan konsol ---")
    for m in pesan[:25]:
        print(" ", m)
else:
    print("konsol bersih: tidak ada error/warning")

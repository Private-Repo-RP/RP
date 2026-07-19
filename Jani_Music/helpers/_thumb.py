# © @BabiesIQ — Ultra Premium Glassmorphic Thumbnail v3

import asyncio
import os
import random
import re
import textwrap
import time
from io import BytesIO

from PIL import (
    Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
)

# ── Cache dir ──────────────────────────────────────────────────────────
_CACHE_DIR = "/tmp/babiesiq_thumbs"
os.makedirs(_CACHE_DIR, exist_ok=True)

# ── Canvas size ────────────────────────────────────────────────────────
_W, _H = 1280, 720

# ── Color palette ──────────────────────────────────────────────────────
_VIOLET  = (138,  43, 226)
_MAGENTA = (255,   0, 180)
_CYAN    = (  0, 210, 255)
_PINK    = (255,  80, 160)
_WHITE   = (255, 255, 255)
_DARK    = (  6,   4,  18)
_GOLD    = (255, 210,  80)

# ── Font discovery (direct paths, no glob) ─────────────────────────────
def _find_font(bold: bool = True) -> str | None:
    candidates = (
        [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        ] if bold else [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        ]
    )
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None

_FONT_BOLD = _find_font(True)
_FONT_REG  = _find_font(False)

def _font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    path = _FONT_BOLD if bold else _FONT_REG
    try:
        if path:
            return ImageFont.truetype(path, size)
    except Exception:
        pass
    return ImageFont.load_default()

def _strip(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()

def _text_width(draw, text, font):
    try:
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[2] - bb[0]
    except Exception:
        return len(text) * (font.size if hasattr(font, "size") else 12)


# ═══════════════════════════════════════════════════════════════════════
#  BACKGROUND — deep space gradient
# ═══════════════════════════════════════════════════════════════════════

def _make_bg_gradient() -> Image.Image:
    bg = Image.new("RGBA", (_W, _H), (0, 0, 0, 255))
    d  = ImageDraw.Draw(bg)
    for y in range(_H):
        t  = y / _H
        # Deep purple → near-black indigo
        r  = int(8  + 30  * (1 - t))
        g  = int(4  + 8   * t)
        b  = int(28 + 50  * (1 - t))
        d.line([(0, y), (_W, y)], fill=(r, g, b, 255))
    return bg


# ═══════════════════════════════════════════════════════════════════════
#  FLOATING GLASS BUBBLES
# ═══════════════════════════════════════════════════════════════════════

def _draw_bubbles(canvas: Image.Image, seed: int = 42) -> Image.Image:
    """
    Draw random glass bubbles scattered across the canvas.
    Mix of large (200-320px), medium (80-160px), small (30-70px).
    Each bubble: semi-transparent fill + bright rim + inner specular highlight.
    """
    rng = random.Random(seed)
    overlay = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # Bubble definitions: (size_range, count, fill_alpha, rim_alpha, colors)
    groups = [
        # Big background bubbles
        ((220, 340), 5,  18, 55,  [_VIOLET, _CYAN, _MAGENTA, _PINK]),
        # Medium bubbles
        ((80,  160), 10, 22, 70,  [_CYAN, _VIOLET, _GOLD, _PINK, _MAGENTA]),
        # Small accent bubbles
        ((28,  65),  18, 30, 100, [_CYAN, _WHITE, _GOLD, _MAGENTA, _PINK]),
    ]

    for (smin, smax), count, fill_a, rim_a, colors in groups:
        for _ in range(count):
            r    = rng.randint(smin, smax) // 2
            cx   = rng.randint(r, _W - r)
            cy   = rng.randint(r, _H - r)
            col  = rng.choice(colors)
            box  = [cx - r, cy - r, cx + r, cy + r]

            # Soft glow behind big bubbles
            if r > 80:
                for gi in range(20, 0, -1):
                    ga = int(8 * (gi / 20) ** 1.8)
                    gbox = [cx - r - gi*2, cy - r - gi*2,
                            cx + r + gi*2, cy + r + gi*2]
                    d.ellipse(gbox, fill=(*col, ga))

            # Fill
            d.ellipse(box, fill=(*col, fill_a))

            # Rim (multiple strokes for soft glow rim)
            for w, wa in [(3, rim_a), (2, int(rim_a*0.6)), (1, int(rim_a*1.2))]:
                d.ellipse(box, outline=(*col, wa), width=w)

            # Inner specular highlight (white glint top-left)
            glint_r = max(4, r // 5)
            gx = cx - r // 3
            gy = cy - r // 3
            for gi in range(glint_r, 0, -1):
                ga = int(180 * (gi / glint_r) ** 0.7)
                gbox2 = [gx - gi, gy - gi, gx + gi, gy + gi]
                d.ellipse(gbox2, fill=(255, 255, 255, ga))

            # Second smaller specular dot
            if r > 40:
                sx, sy = cx + r // 4, cy - r // 3
                sr = max(2, r // 9)
                for si in range(sr, 0, -1):
                    sa = int(120 * (si / sr) ** 0.8)
                    d.ellipse([sx-si, sy-si, sx+si, sy+si],
                               fill=(255, 255, 255, sa))

    return Image.alpha_composite(canvas, overlay)


# ═══════════════════════════════════════════════════════════════════════
#  VIGNETTE & DEPTH
# ═══════════════════════════════════════════════════════════════════════

def _vignette(w, h, strength=180, steps=100) -> Image.Image:
    img  = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d    = ImageDraw.Draw(img)
    maxm = min(w, h) // 2 - 1
    for i in range(steps):
        t = i / steps
        a = int(strength * (1 - t) ** 1.8)
        m = min(i * 4, maxm)
        if w - 2*m <= 0 or h - 2*m <= 0:
            break
        d.rectangle([m, m, w - m - 1, h - m - 1], outline=(0, 0, 0, a), width=1)
    return img


def _left_shadow(w, h) -> Image.Image:
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d   = ImageDraw.Draw(img)
    end = int(w * 0.62)
    for x in range(end):
        a = int(195 * (1 - x / end) ** 0.48)
        d.line([(x, 0), (x, h)], fill=(0, 0, 0, a))
    return img


# ═══════════════════════════════════════════════════════════════════════
#  GLASS PANEL (main card)
# ═══════════════════════════════════════════════════════════════════════

def _rounded_mask(size, radius) -> Image.Image:
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle(
        [0, 0, size[0]-1, size[1]-1], radius=radius, fill=255
    )
    return m


def _glass_panel(bg: Image.Image, box, radius=32) -> Image.Image:
    x1, y1, x2, y2 = box
    pw, ph = x2 - x1, y2 - y1

    # Frosted crop
    region  = bg.crop((x1, y1, x2, y2)).convert("RGBA")
    blurred = region.filter(ImageFilter.GaussianBlur(radius=28))
    blurred = ImageEnhance.Brightness(blurred).enhance(0.35)

    # Colour tints
    for tint, alpha in [
        ((255, 255, 255), 18),
        (_VIOLET,          10),
        (_CYAN,             6),
    ]:
        t = Image.new("RGBA", (pw, ph), (*tint, alpha))
        blurred = Image.alpha_composite(blurred, t)

    # Gradient sweep (left bright → right dim)
    sweep = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    sd    = ImageDraw.Draw(sweep)
    for x in range(pw):
        t = x / pw
        a = int(28 * (1 - t) ** 1.2)
        sd.line([(x, 0), (x, ph)], fill=(255, 255, 255, a))
    blurred = Image.alpha_composite(blurred, sweep)

    # Clip to rounded rect
    mask = _rounded_mask((pw, ph), radius)
    blurred.putalpha(mask)

    # Compose onto full canvas
    out = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    out.paste(blurred, (x1, y1), blurred)
    d = ImageDraw.Draw(out)

    # Outer border glow (multi-layer)
    for shrink, col, width, alpha in [
        (0,  _CYAN,   3, 80),
        (3,  _WHITE,  1, 50),
        (5,  _VIOLET, 1, 35),
    ]:
        d.rounded_rectangle(
            [x1+shrink, y1+shrink, x2-shrink, y2-shrink],
            radius=radius - shrink,
            outline=(*col, alpha), width=width
        )

    # Top edge highlight (bright shimmer)
    shimmer = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    sd2 = ImageDraw.Draw(shimmer)
    sd2.line([(x1+radius, y1+1), (x2-radius, y1+1)],
              fill=(255, 255, 255, 90), width=2)
    out = Image.alpha_composite(out, shimmer)

    return out


# ═══════════════════════════════════════════════════════════════════════
#  CIRCLE ART with glow ring
# ═══════════════════════════════════════════════════════════════════════

def _circle_crop(img: Image.Image, size: int) -> Image.Image:
    w, h = img.size
    s    = min(w, h)
    img  = img.crop(((w-s)//2, (h-s)//2, (w+s)//2, (h+s)//2))
    img  = img.resize((size, size), Image.LANCZOS).convert("RGBA")

    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size-1, size-1], fill=255)
    out  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(img, mask=mask)

    # Gradient ring (violet → cyan → magenta)
    ring = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    rd   = ImageDraw.Draw(ring)
    colors = [_VIOLET, _CYAN, _MAGENTA, _VIOLET]
    for i in range(10):
        t  = i / 9
        ci = int(t * (len(colors) - 1))
        cn = min(ci + 1, len(colors) - 1)
        ft = t * (len(colors)-1) - ci
        c1, c2 = colors[ci], colors[cn]
        r_ = int(c1[0] + (c2[0]-c1[0]) * ft)
        g_ = int(c1[1] + (c2[1]-c1[1]) * ft)
        b_ = int(c1[2] + (c2[2]-c1[2]) * ft)
        rd.ellipse(
            [i, i, size-1-i, size-1-i],
            outline=(r_, g_, b_, max(0, 255-i*18)), width=1,
        )
    return Image.alpha_composite(out, ring)


def _halo(w, h, cx, cy, r) -> Image.Image:
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d   = ImageDraw.Draw(img)
    for step, col, strength in [
        (60, _VIOLET,  70),
        (40, _CYAN,    40),
        (20, _MAGENTA, 25),
    ]:
        for i in range(step, 0, -1):
            a = int(strength * (i/step)**2)
            d.ellipse([cx-r-i, cy-r-i, cx+r+i, cy+r+i], fill=(*col, a))
    return img


# ═══════════════════════════════════════════════════════════════════════
#  GRADIENT DIVIDER
# ═══════════════════════════════════════════════════════════════════════

def _gradient_line(canvas, x, y, w, h_px=2):
    bar = Image.new("RGBA", (w, h_px), (0,0,0,0))
    d   = ImageDraw.Draw(bar)
    cols = [_VIOLET, _CYAN, _MAGENTA, _CYAN]
    for px in range(w):
        t  = px / w
        ci = int(t * (len(cols)-1))
        cn = min(ci+1, len(cols)-1)
        ft = t*(len(cols)-1) - ci
        c1, c2 = cols[ci], cols[cn]
        r_ = int(c1[0]+(c2[0]-c1[0])*ft)
        g_ = int(c1[1]+(c2[1]-c1[1])*ft)
        b_ = int(c1[2]+(c2[2]-c1[2])*ft)
        a  = int(220 * (1 - abs(t-0.5)*0.5))
        d.line([(px,0),(px,h_px-1)], fill=(r_,g_,b_,a))
    canvas.paste(bar, (x, y), bar)


# ═══════════════════════════════════════════════════════════════════════
#  EQUALIZER BARS
# ═══════════════════════════════════════════════════════════════════════

def _eq_bars(draw, x, y, n=14):
    heights = [18, 38, 28, 52, 32, 62, 24, 48, 36, 56, 30, 44, 20, 42][:n]
    bw, gap = 7, 4
    cols = [_VIOLET, _CYAN, _MAGENTA, _PINK]
    for i, bh in enumerate(heights):
        t   = i / (n-1)
        ci  = int(t * (len(cols)-1))
        cn  = min(ci+1, len(cols)-1)
        ft  = t*(len(cols)-1) - ci
        c1, c2 = cols[ci], cols[cn]
        r_  = int(c1[0]+(c2[0]-c1[0])*ft)
        g_  = int(c1[1]+(c2[1]-c1[1])*ft)
        b_  = int(c1[2]+(c2[2]-c1[2])*ft)
        bx  = x + i*(bw+gap)

        # Glow shadow behind bar
        for gi in range(5, 0, -1):
            ga = int(30 * gi/5)
            draw.rectangle([bx-gi, y-bh-gi, bx+bw+gi, y+gi],
                            fill=(r_, g_, b_, ga))
        draw.rectangle([bx, y-bh, bx+bw, y], fill=(r_, g_, b_, 220))
        # Top cap
        draw.rectangle([bx, y-bh-4, bx+bw, y-bh-1],
                        fill=(255, 255, 255, 120))


# ═══════════════════════════════════════════════════════════════════════
#  NETWORK HELPERS
# ═══════════════════════════════════════════════════════════════════════

async def _fetch_thumbnail(videoid: str) -> Image.Image | None:
    try:
        import aiohttp
        urls = [
            f"https://i.ytimg.com/vi/{videoid}/maxresdefault.jpg",
            f"https://i.ytimg.com/vi/{videoid}/hqdefault.jpg",
            f"https://i.ytimg.com/vi/{videoid}/mqdefault.jpg",
        ]
        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                        if r.status != 200:
                            continue
                        data = await r.read()
                        img  = Image.open(BytesIO(data)).convert("RGBA")
                        if img.size[0] < 200:
                            continue
                        return img
                except Exception:
                    continue
    except Exception:
        pass
    return None


async def _fetch_video_info(videoid: str):
    try:
        from py_yt import VideosSearch
        res = await VideosSearch(f"https://youtu.be/{videoid}", limit=1).next()
        r   = res["result"][0]
        title   = _strip(r.get("title", "")) or "Unknown Title"
        dur     = r.get("duration", "") or "00:00"
        ch_raw  = r.get("channel", {})
        channel = ch_raw.get("name", "YouTube") if isinstance(ch_raw, dict) else "YouTube"
        return title, dur, channel
    except Exception:
        return "Unknown Title", "00:00", "YouTube"


# ═══════════════════════════════════════════════════════════════════════
#  TITLE FIT — auto-shrink to stay inside card
# ═══════════════════════════════════════════════════════════════════════

def _fit_title(draw, text: str, max_w: int, max_lines: int = 2):
    """
    Returns list of (line_text, font) pairs that fit within max_w.
    Starts at size 58, shrinks down to 28 if needed.
    """
    for size in range(58, 26, -4):
        f = _font(size)
        wrapped = textwrap.wrap(text, width=max(8, int(max_w / (size * 0.52))))
        lines   = wrapped[:max_lines]
        if not lines:
            lines = [text[:16]]
        fits = all(_text_width(draw, l, f) <= max_w for l in lines)
        if fits:
            return [(l, f) for l in lines]
    # Last resort: single truncated line
    f = _font(28)
    t = text
    while _text_width(draw, t, f) > max_w and len(t) > 4:
        t = t[:-2] + "…"
    return [(t, f)]


# ═══════════════════════════════════════════════════════════════════════
#  NOISE GRAIN
# ═══════════════════════════════════════════════════════════════════════

def _noise(w, h, intensity=18, alpha=22) -> Image.Image:
    T   = 256
    raw = bytearray(random.randint(max(0,128-intensity), min(255,128+intensity)) for _ in range(T*T))
    tile = Image.frombytes("L", (T,T), bytes(raw))
    full = Image.new("L", (w,h))
    for y in range(0,h,T):
        for x in range(0,w,T):
            full.paste(tile,(x,y))
    rgba = full.convert("RGBA")
    r_,g_,b_,_ = rgba.split()
    a_ = Image.new("L",(w,h),alpha)
    return Image.merge("RGBA",(r_,g_,b_,a_))


# ═══════════════════════════════════════════════════════════════════════
#  MAIN GENERATOR
# ═══════════════════════════════════════════════════════════════════════

async def get_thumb(
    videoid:   str,
    title:     str = "",
    duration:  str = "",
    requester: str = "",
) -> str:
    out = os.path.join(_CACHE_DIR, f"{videoid}.jpg")
    if os.path.exists(out) and time.time() - os.path.getmtime(out) < 600:
        return out

    (yt_title, yt_dur, channel), original = await asyncio.gather(
        _fetch_video_info(videoid),
        _fetch_thumbnail(videoid),
    )

    title    = _strip(title) or yt_title
    duration = duration or yt_dur

    # ── 1. Base background ────────────────────────────────────────────
    if original:
        bw, bh = original.size
        ratio  = _W / _H
        if bw/bh > ratio:
            nw = int(bh * ratio)
            bg = original.crop(((bw-nw)//2, 0, (bw-nw)//2+nw, bh))
        else:
            nh = int(bw / ratio)
            bg = original.crop((0, (bh-nh)//2, bw, (bh-nh)//2+nh))
        bg = bg.resize((_W, _H), Image.LANCZOS).convert("RGBA")
        bg = bg.filter(ImageFilter.GaussianBlur(radius=6))
        bg = ImageEnhance.Brightness(bg).enhance(0.28)
        # Blend with gradient overlay for depth
        grad = _make_bg_gradient()
        grad.putalpha(Image.new("L", (_W,_H), 120))
        bg = Image.alpha_composite(bg, grad)
    else:
        bg = _make_bg_gradient()

    # ── 2. Glass bubbles ──────────────────────────────────────────────
    seed = sum(ord(c) for c in videoid) % 9999
    bg = _draw_bubbles(bg, seed=seed)

    # ── 3. Left shadow for text legibility ───────────────────────────
    bg = Image.alpha_composite(bg, _left_shadow(_W, _H))

    # ── 4. Vignette ───────────────────────────────────────────────────
    bg = Image.alpha_composite(bg, _vignette(_W, _H, strength=150))

    # ── 5. Glass card ─────────────────────────────────────────────────
    CARD = (38, 44, 660, 676)
    bg = Image.alpha_composite(bg, _glass_panel(bg, CARD, radius=36))

    # ── 6. Circle art + halo ──────────────────────────────────────────
    CS    = 360
    ART_CX = _W - 68 - CS//2
    ART_CY = _H//2
    if original:
        bg = Image.alpha_composite(bg, _halo(_W, _H, ART_CX, ART_CY, CS//2))
        circle = _circle_crop(original, CS)
        bg.paste(circle, (ART_CX - CS//2, ART_CY - CS//2), circle)

    # ── 7. Film grain ─────────────────────────────────────────────────
    bg = Image.alpha_composite(bg, _noise(_W, _H))

    # ── 8. Card content ───────────────────────────────────────────────
    draw = ImageDraw.Draw(bg)
    PAD  = CARD[0] + 42       # left text margin
    TW   = CARD[2] - PAD - 36 # usable width ≈ 580px
    TY   = CARD[1] + 44

    # ▸ "◈ NOW PLAYING" badge
    badge_txt = "◈  NOW PLAYING"
    f_badge   = _font(19)
    pill_w, pill_h = 210, 32

    # Badge glow
    glow_layer = Image.new("RGBA", bg.size, (0,0,0,0))
    gd = ImageDraw.Draw(glow_layer)
    for gi in range(12,0,-1):
        ga = int(30 * gi/12)
        gd.rounded_rectangle(
            [PAD-gi, TY-gi, PAD+pill_w+gi, TY+pill_h+gi],
            radius=12+gi, fill=(*_VIOLET, ga)
        )
    bg = Image.alpha_composite(bg, glow_layer)
    draw = ImageDraw.Draw(bg)

    draw.rounded_rectangle(
        [PAD, TY, PAD+pill_w, TY+pill_h],
        radius=12, fill=(*_VIOLET, 210)
    )
    draw.rounded_rectangle(
        [PAD, TY, PAD+pill_w, TY+pill_h],
        radius=12, outline=(*_CYAN, 120), width=1
    )
    draw.text((PAD+12, TY+6), badge_txt, font=f_badge, fill=(*_WHITE, 255))
    TY += pill_h + 16

    # ▸ Channel
    ch_clean = _strip(channel)[:38]
    draw.text(
        (PAD, TY), f"♪  {ch_clean}",
        font=_font(23, bold=False), fill=(180, 180, 255, 200),
    )
    TY += 40

    # ▸ Divider
    _gradient_line(bg, PAD, TY, TW, 2)
    draw = ImageDraw.Draw(bg)
    TY += 18

    # ▸ Song title — auto-fit, always inside card
    title_lines = _fit_title(draw, title or "Unknown Title", TW, max_lines=2)
    line_spacing = 12
    for i, (line, fnt) in enumerate(title_lines):
        # Glow effect under each line
        for goff in [(3,3),(2,2),(1,1)]:
            draw.text(
                (PAD + goff[0], TY + goff[1]), line,
                font=fnt, fill=(*_VIOLET, 60)
            )
        # Drop shadow
        draw.text((PAD+2, TY+2), line, font=fnt, fill=(0,0,0,120))
        # Main text
        draw.text((PAD, TY), line, font=fnt, fill=(*_WHITE, 255))
        try:
            lh = draw.textbbox((0,0), line, font=fnt)[3]
        except Exception:
            lh = fnt.size if hasattr(fnt,"size") else 40
        TY += lh + line_spacing
    TY += 10

    # ▸ Divider
    _gradient_line(bg, PAD, TY, TW, 2)
    draw = ImageDraw.Draw(bg)
    TY += 18

    # ▸ Duration + requester
    draw.text(
        (PAD, TY), f"Time Minu... {duration}",
        font=_font(27), fill=(*_CYAN, 240),
    )
    req = _strip(requester)
    if req:
        req_text = f"▸  {req[:26]}"
        draw.text(
            (PAD + 190, TY + 4), req_text,
            font=_font(22, bold=False), fill=(200, 180, 255, 185),
        )

    # ▸ Equalizer (bottom of card, with some breathing room)
    EQ_Y = CARD[3] - 58
    _eq_bars(draw, PAD, EQ_Y, n=14)

    # ▸ Branding
    brand = "♪ @Oramusicbot"
    f_br  = _font(30, bold=False)
    bw_px = _text_width(draw, brand, f_br)
    draw.text(
        (PAD + (TW - bw_px)//2, EQ_Y - 34), brand,
        font=f_br, fill=(*_CYAN, 200),
    )

    # ── 9. Save ───────────────────────────────────────────────────────
    bg.convert("RGB").save(out, "JPEG", quality=96, optimize=True)
    return out

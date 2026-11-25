"""Stylesheets and icons for the reel-recut graphics. Data only — no logic.

Every graphic is an HTML page that headless Chrome screenshots onto a
transparent 1080x1920 canvas, so the type is set by a browser: real kerning,
wrapping and rounded boxes that ffmpeg's drawtext cannot do.

`string.Template` placeholders: $accent $second $ink $display $text
$display_url $text_url $stack_y $panel_h.

Sizes are tuned for a phone: nothing a viewer has to read is under 40 px.
"""

ICONS = {
    "ok": '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "warn": '<svg viewBox="0 0 24 24"><path d="M12 5v9" stroke="currentColor" stroke-width="3.4" stroke-linecap="round"/><circle cx="12" cy="19" r="2" fill="currentColor"/></svg>',
    "cross": '<svg viewBox="0 0 24 24"><path d="M6.5 6.5l11 11M17.5 6.5l-11 11" stroke="currentColor" stroke-width="3.2" stroke-linecap="round"/></svg>',
    "loc": '<svg viewBox="0 0 24 24"><path d="M12 22s7-6.6 7-12.2A7 7 0 005 9.8C5 15.4 12 22 12 22z" fill="currentColor"/><circle cx="12" cy="9.6" r="2.7" fill="#0a1413"/></svg>',
    "save": '<svg viewBox="0 0 24 24"><path d="M6 3.5h12v17.5l-6-4.6-6 4.6z" fill="currentColor"/></svg>',
    "comment": '<svg viewBox="0 0 24 24"><path d="M4 5h16v11H10l-5 4v-4H4z" fill="currentColor"/></svg>',
    "ask": '<svg viewBox="0 0 24 24"><path d="M8.2 8.6a3.9 3.9 0 117 2.4c-1.2 1.2-3 1.7-3 3.9" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round"/><circle cx="12.1" cy="19.4" r="1.9" fill="currentColor"/></svg>',
    "flag": '<svg viewBox="0 0 24 24"><path d="M6 3v18" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"/><path d="M7 4h11l-2.6 4L18 12H7z" fill="currentColor"/></svg>',
    "lock": '<svg viewBox="0 0 24 24"><rect x="5" y="10.5" width="14" height="10" rx="2.4" fill="currentColor"/><path d="M8.3 10.5V8a3.7 3.7 0 017.4 0v2.5" fill="none" stroke="currentColor" stroke-width="2.6"/></svg>',
    "tg": '<svg viewBox="0 0 24 24"><path d="M21 3L3 10.5l7 2.5 2.5 7L21 3z" fill="currentColor"/></svg>',
    "link": '<svg viewBox="0 0 24 24"><path d="M10 14a4 4 0 005.7 0l3-3a4 4 0 00-5.7-5.7l-1 1M14 10a4 4 0 00-5.7 0l-3 3a4 4 0 005.7 5.7l1-1" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg>',
}

# Which icon a chip style carries. `quote` has none.
CHIP_ICON = {"plain": "ok", "warn": "warn", "ok": "ok", "loc": "loc", "save": "save",
             "comment": "comment", "ask": "ask", "quote": None}
PANEL_ICON = {"check": "ok", "cross": "cross", "flag": "flag"}

BASE_CSS = """
@font-face{font-family:RecutText;font-weight:100 900;src:url('$text_url') format('truetype')}
@font-face{font-family:RecutDisplay;font-weight:100 900;src:url('$display_url') format('truetype')}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1920px;background:transparent;overflow:hidden;font-family:RecutText,sans-serif;color:#fff}
.row{position:absolute;left:90px;width:900px;display:flex;justify-content:center;transform:translateY(-50%)}
svg{display:block}
.hid{visibility:hidden}
.chip{display:inline-flex;align-items:center;gap:20px;max-width:900px;padding:22px 34px 22px 24px;border-radius:34px;
  font:700 56px/1.13 RecutText;letter-spacing:-.01em;background:rgba(10,20,19,.93);color:#fff;
  box-shadow:0 14px 40px rgba(0,0,0,.42),inset 0 0 0 2px rgba(255,255,255,.09)}
.chip .ic{flex:none;width:62px;height:62px;border-radius:50%;display:grid;place-items:center;background:$second;color:$ink}
.chip .ic svg{width:36px;height:36px}
.chip.warn{background:$accent;color:#fff;box-shadow:0 14px 40px rgba(0,0,0,.4)}
.chip.warn .ic{background:#fff;color:$accent}
.chip.ok{background:$ink;box-shadow:0 14px 40px rgba(0,0,0,.42),inset 0 0 0 3px $second}
.chip.quote{background:#fff;color:$ink;font-weight:600;font-style:italic;padding-left:34px}
.chip.ask .ic{background:#ffd166;color:$ink}
.chip.loc .ic,.chip.save .ic,.chip.comment .ic{background:$accent;color:#fff}
.chip.tag{padding:20px 34px;font-size:50px;border-radius:999px;background:#fff;color:$ink}
.tags{gap:16px;flex-wrap:wrap}
.big{flex-direction:column;align-items:center;gap:14px}
.big .num{font:800 168px/1 RecutDisplay;letter-spacing:-.04em;color:#fff;padding:6px 40px 16px;border-radius:44px;
  background:rgba(10,20,19,.93);box-shadow:0 18px 50px rgba(0,0,0,.45),inset 0 0 0 3px rgba(255,255,255,.1)}
.big.warn .num{background:$accent} .big.ok .num{color:$second}
.big .sub{font:700 42px/1.15 RecutText;background:#fff;color:$ink;padding:14px 28px;border-radius:22px;max-width:860px;text-align:center}
.url{flex-direction:column;align-items:center;gap:16px}
.url .bar{display:flex;align-items:center;gap:20px;background:#fff;color:$ink;border-radius:999px;padding:24px 50px 24px 34px;
  font:800 76px/1 RecutText;box-shadow:0 18px 50px rgba(0,0,0,.45)}
.url .bar .lk{width:66px;height:66px;border-radius:50%;background:#1faa59;color:#fff;display:grid;place-items:center}
.url .bar .lk svg{width:40px;height:40px} .url .bar small{font:600 54px RecutText;color:#8a9795}
.url .sub{font:700 40px/1.15 RecutText;background:rgba(10,20,19,.93);padding:14px 28px;border-radius:22px;max-width:860px;text-align:center}
.hook{position:absolute;left:70px;top:286px;width:940px;display:flex;flex-direction:column;align-items:flex-start;gap:12px}
.hook .l1{font:800 64px/1.08 RecutDisplay;letter-spacing:-.03em;background:#fff;color:$ink;padding:16px 26px 20px;border-radius:22px;max-width:940px}
.hook .l2{font:700 50px/1.1 RecutDisplay;letter-spacing:-.02em;background:$accent;color:#fff;padding:14px 24px 18px;border-radius:20px}
.brand{position:absolute;left:56px;top:204px;font:700 34px/1 RecutDisplay;letter-spacing:-.03em;color:#fff;padding:12px 20px 14px;
  border-radius:999px;background:rgba(10,20,19,.55)} .brand em{font-style:normal;color:$second}
.panel{position:absolute;left:0;top:${stack_y}px;width:1080px;height:${panel_h}px;background:$ink;border-radius:46px 46px 0 0;
  padding:140px 64px 0;box-shadow:0 -18px 50px rgba(0,0,0,.4)}
.panel:before{content:"";position:absolute;left:0;right:0;top:0;height:8px;border-radius:46px 46px 0 0;
  background:linear-gradient(90deg,$accent,$second)}
.panel h2{font:700 56px/1.12 RecutDisplay;letter-spacing:-.03em;margin-bottom:40px;max-width:940px}
.panel li{list-style:none;display:flex;align-items:flex-start;gap:26px;font:650 54px/1.16 RecutText;margin-bottom:30px;max-width:940px}
.panel li .b{flex:none;width:72px;height:72px;border-radius:50%;display:grid;place-items:center;font:800 36px/1 RecutDisplay;
  background:$accent;color:#fff;margin-top:-5px}
.panel.dense{padding-top:112px} .panel.dense h2{font-size:50px;margin-bottom:30px}
.panel.dense li{font-size:48px;margin-bottom:22px;gap:22px} .panel.dense li .b{width:62px;height:62px;font-size:30px;margin-top:-6px}
.panel li .b svg{width:38px;height:38px}
.panel.check li .b{background:$second;color:$ink} .panel.cross li .b{background:#fff;color:$accent}
.panel li span{padding-top:2px}
"""

END_CSS = """
.end{position:absolute;inset:0;background:linear-gradient(180deg,$ink 0%,$ink 100%)}
.end:before{content:"";position:absolute;inset:0;background:radial-gradient(circle at 50% 18%,$second 0%,rgba(0,0,0,0) 60%);opacity:.28}
.art{position:absolute;left:0;top:0;width:1080px;height:760px;background:$art center/cover}
.art:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,0) 45%,$ink 100%)}
.logo{position:absolute;left:0;width:1080px;top:740px;text-align:center;font:800 112px/1 RecutDisplay;letter-spacing:-.045em}
.logo em{font-style:normal;color:$second}
.tagl{position:absolute;left:70px;width:940px;top:900px;text-align:center;font:600 44px/1.28 RecutText;color:#cfe0de}
.btns{position:absolute;left:0;width:1080px;top:1150px;display:flex;flex-direction:column;align-items:center;gap:26px}
.btn{display:flex;align-items:center;gap:18px;font:700 50px/1 RecutText;padding:26px 44px;border-radius:999px;background:#fff;color:$ink}
.btn.first{background:$accent;color:#fff} .btn svg{width:44px;height:44px}
"""

COVER_CSS = """
.bgi{position:absolute;inset:0;background:url('$frame') center/cover}
.sc{position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,20,19,.55) 0%,rgba(10,20,19,0) 22%,rgba(10,20,19,0) 44%,
  rgba(10,20,19,.9) 66%,$ink 86%)}
.num{position:absolute;left:70px;top:300px;display:flex;align-items:center;gap:18px}
.num b{font:800 54px/1 RecutDisplay;background:$accent;color:#fff;padding:16px 26px 20px;border-radius:22px;letter-spacing:-.03em}
.num span{font:700 34px/1.15 RecutDisplay;letter-spacing:-.02em;background:rgba(10,20,19,.82);padding:16px 22px 18px;border-radius:20px}
.ttl{position:absolute;left:70px;right:70px;top:1010px;display:flex;flex-direction:column;align-items:flex-start;gap:12px}
.ttl .ln{font:800 92px/1.04 RecutDisplay;letter-spacing:-.04em;color:#fff;text-shadow:0 6px 30px rgba(0,0,0,.5)}
.ttl .hl{font:800 80px/1.04 RecutDisplay;letter-spacing:-.04em;background:$accent;color:#fff;padding:12px 26px 20px;
  border-radius:24px;margin:6px 0 0 -6px}
.site{position:absolute;left:70px;top:1500px;font:700 44px/1 RecutDisplay;letter-spacing:-.03em} .site em{font-style:normal;color:$second}
"""

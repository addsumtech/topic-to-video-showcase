#!/usr/bin/env python3
"""Build index.html (English) and cn/index.html (Chinese) from FILMS below.

Run from anywhere: python3 tools/build.py. Every film listed must have films/<id>.mp4 and posters/<id>.jpg;
the build stops if one is missing, so a page never links a film that is not in the repo.
"""
import html
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://video.addsum.top'
REPO = 'https://github.com/addsumtech/topic-to-video'

FILMS = [
    # tier, id, language of the film, then en/zh title and note. Notes state only what the film shows.
    dict(tier='remotion', id='workbuddy-promo', lang='en',
         title=('WorkBuddy product film', 'WorkBuddy 产品宣传片'),
         kind=('Product promo', '产品宣传'),
         note=('Tencent WorkBuddy’s desktop app rebuilt from its official screenshots, with six shots rendered in '
               'Blender: the desk companion, a pile of files, a MacBook Air, and the app itself on a MacBook screen. Unofficial, not affiliated with Tencent.',
               '照官网截图重建腾讯 WorkBuddy 的桌面端界面，另有六个镜头用 Blender 渲染：桌面小伙伴、一叠文件、MacBook Air，以及显示在 MacBook 屏幕上的应用界面。'
               '非官方作品，与腾讯无关。')),
    dict(tier='remotion', id='topic-to-video-promo', lang='en',
         title=('topic-to-video launch film', 'topic-to-video 发布短片'),
         kind=('Launch film', '发布短片'),
         note=('The skill’s own launch film. It plays real clips from other films on this page and shows the request '
               'each one started from.',
               '这个 skill 自己的发布片。片中播放的是本页其他影片的真实片段，也展示了每部片最初的那句请求。')),
    dict(tier='remotion', id='slide-maker-promo', lang='en',
         title=('slide-maker launch film', 'slide-maker 发布短片'),
         kind=('Launch film', '发布短片'),
         note=('A launch film for slide-maker, cut to its music. Every deck page on screen is a real page the tool '
               'made, not a mock-up.',
               '为 slide-maker 做的发布片，按配乐剪辑。画面里的每一页幻灯片都是这个工具真实做出来的，不是示意图。')),
    dict(tier='remotion', id='grok-bot-explainer', lang='en',
         title=('Grok Bot explained', 'Grok Bot 介绍'),
         kind=('Product explainer', '产品介绍'),
         note=('What Grok Bot does and where it stops, in 36 beats under three minutes. An independent explainer, '
               'not affiliated with xAI.',
               '用 36 个镜头、不到三分钟讲清 Grok Bot 能做什么、在哪里停手。独立制作的介绍片，与 xAI 无关。')),
    dict(tier='remotion', id='anc-headphones', lang='en',
         title=('How noise cancelling works', '主动降噪是怎么回事'),
         kind=('Explainer', '科普讲解'),
         note=('Sound as squeezed and stretched air, the flipped wave that cancels it, the two microphones in an '
               'earbud and the tiny window of time they have to work in.',
               '声音是被挤压又拉开的空气；反相的波把它抵消；耳机里的两只麦克风，以及它们只有极短的时间窗口。')),
    dict(tier='remotion', id='job-hunt-promo', lang='zh',
         title=('job-hunt product film', 'job-hunt 产品宣传片'),
         kind=('Product promo', '产品宣传'),
         note=('A promo for the job-hunt skill: finding roles, judging fit, tailoring a CV and rehearsing interviews. '
               'The CV and reports on screen are a fictional example.',
               '求职 skill job-hunt 的宣传片：找岗位、判断值不值得投、改简历、练面试。片中的简历和报告都是虚构示例。')),
    dict(tier='html', id='qr-code-explainer', lang='zh',
         title=('How a QR code is read', '二维码是怎么被读出来的'),
         kind=('Explainer', '科普讲解'),
         note=('Why tearing off one corner still scans and tearing the wrong spot does not. Every code on screen was '
               'generated for the film and checked with an independent decoder.',
               '为什么撕掉一角照样能扫，撕错地方就扫不出。片中每个二维码都是为这部片真实生成的，并用独立的解码器验证过。')),
    dict(tier='html', id='mri-explainer', lang='en',
         title=('How MRI makes an image', 'MRI 是怎么成像的'),
         kind=('Explainer', '科普讲解'),
         note=('An MRI scanner never takes a photograph: precession, relaxation, gradients and k-space. The k-space on '
               'screen is a Fourier transform computed for the film.',
               '磁共振从不拍照：进动、弛豫、梯度场和 k 空间。画面里的 k 空间是为这部片实际计算出的傅里叶变换。')),
]

T = {
    'en': dict(
        htmllang='en', path='/', other='/cn/', other_label='中文',
        title='topic-to-video films',
        desc='Eight short films made by topic-to-video, an AI skill that turns a topic into a narrated video.',
        h1='Films made from a single request',
        lede=('Each film began as one request in a chat. topic-to-video researched the subject, wrote and voiced the '
              'script, designed every shot and rendered the video. No frame was animated by hand.'),
        github='View on GitHub',
        tiers={
            'remotion': ('Remotion films',
                         'Each shot is a React component rendered frame by frame with Remotion, picked from a library '
                         'of 225 shot designs or built for the film. Heavier 3D shots are rendered in Blender.'),
            'html': ('HTML films',
                     'Each beat is a web page built for the film, animated in headless Chrome and captured frame by '
                     'frame. Chrome is all it needs.'),
        },
        langname={'en': 'English', 'zh': 'Chinese'},
        play='Play', close='Close',
        make_h='Make one', make_p='Install the skill in Claude Code, then ask it for a video about your topic.',
        copy='Copy', copied='Copied',
        foot='Every film here was made with topic-to-video. Product names belong to their owners.',
    ),
    'zh': dict(
        htmllang='zh-CN', path='/cn/', other='/', other_label='English',
        title='topic-to-video 影片集',
        desc='topic-to-video 做的八部短片。它是一个把任意主题做成配音讲解视频的 AI skill。',
        h1='一句话请求做成的影片',
        lede='每部片都从聊天里的一句请求开始。topic-to-video 查资料、写稿、配音、设计每个镜头并渲染成片，没有一帧是手工做动画。',
        github='在 GitHub 查看',
        tiers={
            'remotion': ('Remotion 分支',
                         '每个镜头是一个 React 组件，用 Remotion 逐帧渲染；从 225 个镜头设计里挑选，或者为这部片新做。'
                         '较重的 3D 镜头交给 Blender 渲染。'),
            'html': ('HTML 分支', '每一段是为这部片写的网页，在无头 Chrome 里播放动画并逐帧截取。只需要 Chrome。'),
        },
        langname={'en': '英文', 'zh': '中文'},
        play='播放', close='关闭',
        make_h='自己做一部', make_p='把这个 skill 装进 Claude Code，然后告诉它你想讲的主题。',
        copy='复制', copied='已复制',
        foot='本页影片均由 topic-to-video 制作。产品名称归各自所有者。',
    ),
}

INSTALL = 'git clone --depth 1 https://github.com/addsumtech/topic-to-video.git ~/.claude/skills/topic-to-video'


def duration(p: Path) -> str:
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)],
                         capture_output=True, text=True, check=True).stdout.strip()
    s = int(float(out))
    return f'{s // 60}:{s % 60:02d}'


def page(lang: str, lengths: dict) -> str:
    t = T[lang]
    i = 0 if lang == 'en' else 1
    e = html.escape
    up = '' if lang == 'en' else '../'

    def film_title(f):
        return f['title'][i]

    strip = '\n'.join(
        f'<a class="frame {f["tier"]}" href="#{f["id"]}" data-film="{f["id"]}" aria-label="{e(t["play"])}: {e(film_title(f))}">'
        f'<img src="{up}posters/{f["id"]}.jpg" alt="" width="1280" height="720" loading="eager"></a>'
        for f in FILMS)

    sections = []
    for tier in ('remotion', 'html'):
        name, blurb = t['tiers'][tier]
        cards = []
        for f in FILMS:
            if f['tier'] != tier:
                continue
            meta = f'{e(f["kind"][i])}, {e(t["langname"][f["lang"]])}, {lengths[f["id"]]}'
            cards.append(
                f'<article class="film" id="{f["id"]}">'
                f'<button class="poster" type="button" data-film="{f["id"]}" aria-label="{e(t["play"])}: {e(film_title(f))}">'
                f'<img src="{up}posters/{f["id"]}.jpg" alt="" width="1280" height="720" loading="lazy">'
                f'<span class="play" aria-hidden="true"></span></button>'
                f'<h3>{e(film_title(f))}</h3><p class="meta">{meta}</p><p class="note">{e(f["note"][i])}</p></article>')
        sections.append(
            f'<section class="tier {tier}" id="{tier}" aria-labelledby="{tier}-h">'
            f'<div class="tier-head"><h2 id="{tier}-h">{e(name)}</h2><p>{e(blurb)}</p></div>'
            f'<div class="films">{"".join(cards)}</div></section>')

    data = {f['id']: dict(title=film_title(f), note=f['note'][i], src=f'{up}films/{f["id"]}.mp4',
                          poster=f'{up}posters/{f["id"]}.jpg') for f in FILMS}

    return f'''<!doctype html>
<html lang="{t["htmllang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(t["title"])}</title>
<meta name="description" content="{e(t["desc"])}">
<link rel="canonical" href="{SITE}{t["path"]}">
<link rel="alternate" hreflang="en" href="{SITE}/">
<link rel="alternate" hreflang="zh-CN" href="{SITE}/cn/">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(t["title"])}">
<meta property="og:description" content="{e(t["desc"])}">
<meta property="og:image" content="{SITE}/posters/{FILMS[0]["id"]}.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{up}favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}site.css">
</head>
<body>
<header class="bar wrap">
  <a class="brand" href="{t["path"]}"><img src="{up}favicon.svg" alt="" width="28" height="28"><span>topic-to-video</span></a>
  <nav>
    <a href="#remotion">Remotion</a><a href="#html">HTML</a>
    <a class="lang" href="{up if lang == "zh" else ""}{t["other"].lstrip("/")}" hreflang="{"zh-CN" if lang == "en" else "en"}">{t["other_label"]}</a>
    <a class="gh" href="{REPO}">{e(t["github"])}</a>
  </nav>
</header>
<main>
  <div class="intro wrap">
    <h1>{e(t["h1"])}</h1>
    <p class="lede">{e(t["lede"])}</p>
  </div>
  <nav class="strip" aria-label="Films">{strip}</nav>
  <div class="wrap">{"".join(sections)}</div>
  <section class="make wrap" aria-labelledby="make-h">
    <h2 id="make-h">{e(t["make_h"])}</h2>
    <p>{e(t["make_p"])}</p>
    <div class="cmd"><code>{e(INSTALL)}</code><button type="button" class="copy" data-done="{e(t["copied"])}">{e(t["copy"])}</button></div>
  </section>
</main>
<footer class="wrap"><p>{e(t["foot"])} <a href="{REPO}">GitHub</a> · MIT</p></footer>
<dialog class="player" aria-labelledby="player-title">
  <div class="screen"><video controls playsinline preload="none"></video></div>
  <div class="caption"><h2 id="player-title"></h2><p></p>
  <button type="button" class="close">{e(t["close"])}</button></div>
</dialog>
<script>window.FILMS = {json.dumps(data, ensure_ascii=False)};</script>
<script src="{up}site.js"></script>
</body>
</html>
'''


def main():
    missing = [p for f in FILMS for p in (ROOT / 'films' / f'{f["id"]}.mp4', ROOT / 'posters' / f'{f["id"]}.jpg')
               if not p.exists()]
    if missing:
        sys.exit('missing: ' + ', '.join(str(p.relative_to(ROOT)) for p in missing))
    lengths = {f['id']: duration(ROOT / 'films' / f'{f["id"]}.mp4') for f in FILMS}
    (ROOT / 'index.html').write_text(page('en', lengths), encoding='utf-8')
    (ROOT / 'cn').mkdir(exist_ok=True)
    (ROOT / 'cn' / 'index.html').write_text(page('zh', lengths), encoding='utf-8')
    print('built index.html, cn/index.html:', ', '.join(f'{k} {v}' for k, v in lengths.items()))


if __name__ == '__main__':
    main()

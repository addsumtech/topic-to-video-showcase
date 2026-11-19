#!/usr/bin/env python3
"""Build index.html (English) and cn/index.html (Chinese) from FILMS below.

Run from anywhere: python3 tools/build.py. Every film listed must have films/<id>.mp4 and posters/<id>.jpg;
the build stops if one is missing, so a page never links a film that is not in the repo.
"""
import hashlib
import html
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://video.addsum.top'
REPO = 'https://github.com/addsumtech/topic-to-video'

FILMS = [
    # cat: 'explainer' | 'product'; how: 'director' | 'director3d' | 'remotion' | 'html'; lang of the film; en/zh title,
    # kind and note. Notes state only what the film shows. Within a category, newest work first.
    dict(cat='explainer', how='director3d', id='diamond-sparkle-3d', lang='zh',
         title=('Why a diamond sparkles', '钻石为什么会闪闪发光'),
         kind=('Explainer', '科普讲解'),
         note=('Light bends as it enters the stone, a critical angle of about 24° traps it, two reflections off the back '
               'facets send it out the top, and dispersion splits it into colour. Every stone is rendered in Blender; '
               'the coloured fire is real dispersion: the colour shots are each rendered three times, at diamond’s red, green '
               'and blue refractive indices.',
               '光进入钻石时拐弯，约 24° 的临界角把它困住，背面两次反射把它从顶面送回，色散再把它拆成彩色。每颗钻石都用 '
               'Blender 渲染；画面里的火彩是真实的色散：彩色镜头都按钻石对红、绿、蓝光的三个折射率各渲染一遍再合成。')),
    dict(cat='explainer', how='director', id='falling-cat', lang='zh',
         title=('Why a falling cat lands on its feet', '猫为什么总能四脚着地'),
         kind=('Explainer', '科普讲解'),
         note=('A cat has nothing to push against in the air, yet it turns over: it folds into two halves and twists them '
               'in turn, so its total rotation stays zero (the 1969 two-cylinder model). Drawn as a risograph print: spot inks, '
               'halftone and paper grain.',
               '猫在空中无处借力，却能翻过身来：它把身体折成前后两半，轮流收腿伸腿，总转动始终为零（1969 年的两节圆柱模型）。'
               '画面是孔版印刷（risograph）风格：专色油墨、网点和纸张纹理。')),
    dict(cat='explainer', how='director', id='sky-blue-sunset', lang='zh',
         title=('Why the sky is blue and sunsets are red', '天空为什么是蓝的，晚霞为什么是红的'),
         kind=('Explainer', '科普讲解'),
         note=('Rayleigh scattering sends short wavelengths across the whole sky; why the sky is not violet; and why the '
               'long, slanting path of evening light leaves only orange and red.',
               '瑞利散射把短波长的光撒满整片天空；天为什么不是紫色；傍晚的阳光斜穿过长得多的大气，最后只剩下橙光和红光。')),
    dict(cat='explainer', how='director', id='camera-lens', lang='en',
         title=('How a lens makes a sharp image', '镜头怎样拍出清晰的照片'),
         kind=('Explainer', '科普讲解'),
         note=('One point of light, a pinhole, glass that slows one side of a beam, a cone of rays meeting again behind the '
               'lens, and why only one distance can be exactly sharp.',
               '从一个光点讲起：小孔成像、玻璃让光束一侧变慢而拐弯、一锥光线在镜头后重新会聚，以及为什么只有一个距离能完全清晰。')),
    dict(cat='explainer', how='director', id='qr-torn-corner', lang='zh',
         title=('Why a torn QR code still scans', '二维码撕掉一角为什么还能扫'),
         kind=('Explainer', '科普讲解'),
         note=('Codewords, Reed–Solomon error correction and the finder marks, shown on one real version-2 code built '
               'for the film. Every tear it shows, the one that still scans and the ones that do not, was checked with '
               'a real decoder.',
               '码字、里德-所罗门纠错和定位标记，全部演示在一张为本片真实生成的 2 版二维码上。片中每一种撕法，'
               '扫得出的和扫不出的，都用真实的解码器验证过。')),
    dict(cat='explainer', how='html', id='mri-explainer', lang='en',
         title=('How MRI makes an image', 'MRI 是怎么成像的'),
         kind=('Explainer', '科普讲解'),
         note=('An MRI scanner never takes a photograph: precession, relaxation, gradients and k-space. The k-space on '
               'screen is a Fourier transform computed for the film.',
               '磁共振从不拍照：进动、弛豫、梯度场和 k 空间。画面里的 k 空间是为这部片实际计算出的傅里叶变换。')),
    dict(cat='explainer', how='remotion', id='anc-headphones', lang='en',
         title=('How noise cancelling works', '主动降噪是怎么回事'),
         kind=('Explainer', '科普讲解'),
         note=('Sound as squeezed and stretched air, the flipped wave that cancels it, the two microphones in an '
               'earbud and the tiny window of time they have to work in.',
               '声音是被挤压又拉开的空气；反相的波把它抵消；耳机里的两只麦克风，以及它们只有极短的时间窗口。')),
    dict(cat='product', how='director', id='workbuddy-promo', lang='en',
         title=('WorkBuddy launch film', 'WorkBuddy 发布短片'),
         kind=('Product launch', '产品发布'),
         note=('Tencent WorkBuddy’s desktop app, from its official screenshots: the underscore at the end of its '
               'wordmark becomes the film’s cursor, types one sentence, and the finished files come back — a '
               'spreadsheet, a report, a dashboard. Unofficial, not affiliated with Tencent.',
               '用官网截图展示腾讯 WorkBuddy 桌面端：字标末尾的下划线变成全片的光标，打出一句话任务，做好的文件随即交回——'
               '表格、报告、仪表盘。非官方作品，与腾讯无关。')),
    dict(cat='product', how='remotion', id='topic-to-video-promo', lang='en',
         title=('topic-to-video launch film', 'topic-to-video 发布短片'),
         kind=('Launch film', '发布短片'),
         note=('The skill’s own launch film. It plays real clips from other films on this page and shows the request '
               'each one started from.',
               '这个 skill 自己的发布片。片中播放的是本页其他影片的真实片段，也展示了每部片最初的那句请求。')),
    dict(cat='product', how='remotion', id='slide-maker-promo', lang='en',
         title=('slide-maker launch film', 'slide-maker 发布短片'),
         kind=('Launch film', '发布短片'),
         note=('A launch film for slide-maker, cut to its music. Every deck page on screen is a real page the tool '
               'made, not a mock-up.',
               '为 slide-maker 做的发布片，按配乐剪辑。画面里的每一页幻灯片都是这个工具真实做出来的，不是示意图。')),
    dict(cat='product', how='director', id='grok-bot-explainer', lang='en',
         title=('Grok Bot launch film', 'Grok Bot 发布短片'),
         kind=('Product launch', '产品发布'),
         note=('You close the lid and Grok Bot’s Bots keep working through the night on their own cloud computer; at '
               '7:58 AM the work is waiting on your phone. The phone and app screens follow the official screenshots; '
               'the files and emails on them are demo content. Independent, not affiliated with xAI.',
               '合上笔记本，Grok Bot 的 Bot 们在自己的云端电脑上通宵干活；早上 7:58，做好的事已经在手机上等你。'
               '手机和应用界面按官方截图还原，界面里的文件和邮件是示例内容。独立制作，与 xAI 无关。')),
    dict(cat='product', how='remotion', id='job-hunt-promo', lang='zh',
         title=('job-hunt product film', 'job-hunt 产品宣传片'),
         kind=('Product promo', '产品宣传'),
         note=('A promo for the job-hunt skill: finding roles, judging fit, tailoring a CV and rehearsing interviews. '
               'The CV and reports on screen are a fictional example.',
               '求职 skill job-hunt 的宣传片：找岗位、判断值不值得投、改简历、练面试。片中的简历和报告都是虚构示例。')),
]

ZH_NUM = '零一二三四五六七八九十'


def zh_count(n: int) -> str:
    return ZH_NUM[n] if n <= 10 else ('十' + ZH_NUM[n - 10] if n < 20 else str(n))


T = {
    'en': dict(
        htmllang='en', path='/', other='/cn/', other_label='中文',
        title='topic-to-video films',
        desc=f'{len(FILMS)} short films made by topic-to-video, an AI skill that turns a topic into a narrated video.',
        h1='Films made from a single request',
        lede=('Each film began as one request in a chat. topic-to-video researched the subject, wrote and voiced the '
              'script, designed every shot and rendered the video. No frame was animated by hand.'),
        how_h='How they are made',
        how=[('Director', 'The default: research and script first, the voice recorded before any picture, one look '
                          'chosen for the whole film, built sequence by sequence as web pages captured in headless '
                          'Chrome, with real 3D from Blender where the subject needs it.'),
             ('Remotion', 'Each shot is a React component rendered frame by frame, picked from a library of 227 shot '
                          'designs or built for the film; heavier 3D shots rendered in Blender.'),
             ('HTML', 'Each beat is a web page built for the film, animated in headless Chrome and captured frame by '
                      'frame. Chrome is all it needs.')],
        how_tag={'director': 'Director', 'director3d': 'Director · Blender 3D', 'remotion': 'Remotion', 'html': 'HTML'},
        github='View on GitHub',
        cats={
            'explainer': ('Explainers', 'Science and how-things-work films: one question, answered with the real '
                                        'mechanism, every number traced to a source.'),
            'product': ('Product films', 'Launch and promo films for real products, built from the products’ own '
                                         'screens and assets.'),
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
        desc=f'topic-to-video 做的{zh_count(len(FILMS))}部短片。它是一个把任意主题做成配音讲解视频的 AI skill。',
        h1='一句话请求做成的影片',
        lede='每部片都从聊天里的一句请求开始。topic-to-video 查资料、写稿、配音、设计每个镜头并渲染成片，没有一帧是手工做动画。',
        how_h='怎么做出来的',
        how=[('导演式', '默认方式：先查资料、写稿，先录好配音再做画面，整部片选定一种视觉风格，按段落逐段搭建成网页、在无头 Chrome '
                        '里逐帧截取；题材需要时用 Blender 渲染真实 3D。'),
             ('Remotion', '每个镜头是一个 React 组件，用 Remotion 逐帧渲染；从 227 个镜头设计里挑选，或者为这部片新做，'
                          '较重的 3D 镜头交给 Blender 渲染。'),
             ('HTML', '每一段是为这部片写的网页，在无头 Chrome 里播放动画并逐帧截取。只需要 Chrome。')],
        how_tag={'director': '导演式', 'director3d': '导演式 · Blender 3D', 'remotion': 'Remotion', 'html': 'HTML'},
        github='在 GitHub 查看',
        cats={
            'explainer': ('讲解视频', '科普与原理讲解：一个问题，用真实的机制讲清楚，每个数字都有出处。'),
            'product': ('产品宣传视频', '为真实产品做的发布与宣传片，用的是产品自己的界面和素材。'),
        },
        langname={'en': '英文', 'zh': '中文'},
        play='播放', close='关闭',
        make_h='自己做一部', make_p='把这个 skill 装进 Claude Code，然后告诉它你想讲的主题。',
        copy='复制', copied='已复制',
        foot='本页影片均由 topic-to-video 制作。产品名称归各自所有者。',
    ),
}

INSTALL = 'git clone --depth 1 https://github.com/addsumtech/topic-to-video.git ~/.claude/skills/topic-to-video'


def ver(rel: str) -> str:
    """`rel?v=<content hash>`: the site is cached for 10 minutes under one URL, so a replaced film or poster would show
    the old file until then; a new hash is a new URL."""
    return rel + '?v=' + hashlib.sha1((ROOT / rel).read_bytes()).hexdigest()[:8]


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
        f'<a class="frame {f["cat"]}" href="#{f["id"]}" data-film="{f["id"]}" aria-label="{e(t["play"])}: {e(film_title(f))}">'
        f'<img src="{up}{ver(f'posters/{f["id"]}.jpg')}" alt="" width="1280" height="720" loading="eager"></a>'
        for f in FILMS)

    sections = []
    for tier in ('explainer', 'product'):
        name, blurb = t['cats'][tier]
        cards = []
        for f in FILMS:
            if f['cat'] != tier:
                continue
            meta = (f'{e(f["kind"][i])}, {e(t["how_tag"][f["how"]])}, {e(t["langname"][f["lang"]])}, '
                    f'{lengths[f["id"]]}')
            cards.append(
                f'<article class="film" id="{f["id"]}">'
                f'<button class="poster" type="button" data-film="{f["id"]}" aria-label="{e(t["play"])}: {e(film_title(f))}">'
                f'<img src="{up}{ver(f'posters/{f["id"]}.jpg')}" alt="" width="1280" height="720" loading="lazy">'
                f'<span class="play" aria-hidden="true"></span></button>'
                f'<h3>{e(film_title(f))}</h3><p class="meta">{meta}</p><p class="note">{e(f["note"][i])}</p></article>')
        sections.append(
            f'<section class="tier {tier}" id="{tier}" aria-labelledby="{tier}-h">'
            f'<div class="tier-head"><h2 id="{tier}-h">{e(name)}</h2><p>{e(blurb)}</p></div>'
            f'<div class="films">{"".join(cards)}</div></section>')

    data = {f['id']: dict(title=film_title(f), note=f['note'][i], src=up + ver(f'films/{f["id"]}.mp4'),
                          poster=up + ver(f'posters/{f["id"]}.jpg')) for f in FILMS}

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
<meta property="og:image" content="{SITE}/{ver(f'posters/{FILMS[0]["id"]}.jpg')}">
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
    <a href="#explainer">{e(t["cats"]["explainer"][0])}</a><a href="#product">{e(t["cats"]["product"][0])}</a>
    <a class="lang" href="{up if lang == "zh" else ""}{t["other"].lstrip("/")}" hreflang="{"zh-CN" if lang == "en" else "en"}">{t["other_label"]}</a>
    <a class="gh" href="{REPO}">{e(t["github"])}</a>
  </nav>
</header>
<main>
  <div class="intro wrap">
    <h1>{e(t["h1"])}</h1>
    <p class="lede">{e(t["lede"])}</p>
  </div>
  <nav class="strip" aria-label="Films" style="--n: {len(FILMS)}">{strip}</nav>
  <div class="wrap">{"".join(sections)}</div>
  <section class="how wrap" aria-labelledby="how-h">
    <h2 id="how-h">{e(t["how_h"])}</h2>
    <dl>{"".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in t["how"])}</dl>
  </section>
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

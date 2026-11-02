"""Build a text page from markdown with the manual's chrome.
usage: build_page.py pages/help.md help.html"""
import sys, re, html, markdown
src, out = sys.argv[1], sys.argv[2]
md = open(src).read()
# front matter: key: value lines until a blank line
head, body_md = md.split('\n\n', 1)
meta = dict(l.split(': ', 1) for l in head.splitlines())
mdx = markdown.Markdown(extensions=['tables'])
body = mdx.convert(body_md)
secs = []
def h2(m):
    t = m.group(1); sid = re.sub(r'[^a-z0-9]+', '-', re.sub('<.*?>', '', t).lower()).strip('-')
    secs.append((len(secs) + 1, re.sub('<.*?>', '', t), sid, []))
    return f'<section id="{sid}" class="sec"><div class="secno">{len(secs)}</div><h2>{t}</h2>'
def h3(m):
    t = m.group(1); sid = re.sub(r'[^a-z0-9]+', '-', re.sub('<.*?>', '', t).lower()).strip('-')
    if secs: secs[-1][3].append((None, re.sub('<.*?>', '', t), sid))
    return f'<h3 id="{sid}">{t}</h3>'
body = re.sub(r'<h2>(.*?)</h2>|<h3>(.*?)</h3>', lambda m: h2(m) if m.group(1) is not None else h3(re.match(r'<h3>(.*?)</h3>', m.group(0))), body)
body = body.replace('<hr />', '</section>') + ('</section>' if secs else '')
body = body.replace('<table>', '<div class="tbl"><table>').replace('</table>', '</table></div>')
toc = ''.join(f'<li><a href="#{sid}"><span class="n">{n}</span>{html.escape(t)}</a>' + (('<ul>' + ''.join(f'<li><a href="#{ss}">{html.escape(st)}</a></li>' for _, st, ss in subs) + '</ul>') if subs else '') + '</li>' for n, t, sid, subs in secs)
page = open('tools/page_template.html').read()
slug = out.replace('.html', '')
for k, v in {'TITLE': meta['title'], 'DESC': meta['description'], 'SLUG': slug, 'EYEBROW': meta['eyebrow'], 'H1': meta['h1'], 'TOC': toc, 'INTRO': mdx.convert(meta.get('intro', '')), 'BODY': body}.items():
    page = page.replace('{{' + k + '}}', v)
open(out, 'w').write(page)
print(out, len(secs), 'sections')

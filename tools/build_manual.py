"""Build manual.html from the brand kit's FORECTRA_MANUAL.md.
Public page: section 11 (disk paths) and the box-update PowerShell block are left out."""
import re, markdown, html

SRC = '/mnt/user-data/uploads/Documents/Forectra_Brand_CURRENT/incoming/manual/FORECTRA_MANUAL.md'
md = open(SRC).read()

# --- strip internal material ---
md = md.split('\n## 11.')[0].rstrip() + '\n'
md = re.sub(r'\*\*Updating the box\*\*.*?Help → About FOR-X 8 shows it too\.\n', '', md, flags=re.S)
# the reader of the site is a customer, not the author
md = md.replace('If a thing is not in here, it is not finished or it does not exist; tell me which and it goes in.',
                'If a thing is not in here, it is not finished or it does not exist; tell us which and it goes in.')
# drop the H1 and the intro para handled by the hero
body_md = md.split('\n---\n', 1)[1]
intro = md.split('\n---\n', 1)[0]
intro_paras = [p for p in intro.split('\n\n') if p.strip() and not p.startswith('# ')]

mdx = markdown.Markdown(extensions=['tables', 'fenced_code'])
body = mdx.convert(body_md)

# images -> figures with captions, pointing at assets/manual/*.jpg
def fig(m):
    alt, src = m.group(1), m.group(2)
    src = src.replace('img/', '/assets/manual/').replace('.png', '.jpg')
    cls = ' class="panel"' if '/4' in src or '/5' in src else ''
    return f'<figure{cls}><img src="{src}" alt="{html.escape(alt)}" loading="lazy"><figcaption>{html.escape(alt)}</figcaption></figure>'
body = re.sub(r'<p><img alt="([^"]*)" src="([^"]*)" /></p>', fig, body)
# a row of panel pictures (section 9) -> gallery
# section 9: every panel page, in tab order
PANELS = [('CMD','40_panel_cmd'),('KEYS','41_panel_tkeys'),('CUES','42_panel_cues'),('LOOKS','43_panel_looks'),('FADERS','44_panel_faders'),('ENC','45_panel_enc'),('VIDEO','46_panel_video'),('COLOUR','47_panel_colour'),('GELS','48_panel_gels'),('MOVERS','49_panel_movers'),('FX','50_panel_fx')]
gal = '<div class="gallery">' + ''.join(f'<figure><img src="/assets/manual/{f}.jpg" alt="{n}" loading="lazy"><figcaption>{n}</figcaption></figure>' for n,f in PANELS) + '</div>'
body = re.sub(r'<p>((?:<img alt="[^"]*" src="[^"]*" />\s*)+)</p>', gal, body)

# section ids + numbered chips
secs = []
def h2(m):
    num, title = m.group(1), m.group(2)
    sid = 's' + num
    secs.append((num, re.sub('<.*?>', '', title), sid, []))
    return f'<section id="{sid}" class="sec"><div class="secno">{num}</div><h2>{title}</h2>'
def h3(m):
    num, title = m.group(1), m.group(2)
    sid = 's' + num.replace('.', '-')
    if secs: secs[-1][3].append((num, re.sub('<.*?>', '', title), sid))
    return f'<h3 id="{sid}"><span class="n">{num}</span> {title}</h3>'
def hx(m):
    return h2(re.match(r'<h2>(\d+)\. (.*?)</h2>', m.group(0))) if m.group(0).startswith('<h2>') else h3(re.match(r'<h3>(\d+\.\d+) (.*?)</h3>', m.group(0)))
body = re.sub(r'<h2>\d+\. .*?</h2>|<h3>\d+\.\d+ .*?</h3>', hx, body)
body = body.replace('<hr />', '</section>')
body += '</section>'
body = body.replace('<table>', '<div class="tbl"><table>').replace('</table>', '</table></div>')

toc = ''.join(
    f'<li><a href="#{sid}"><span class="n">{num}</span>{html.escape(t)}</a>' +
    (('<ul>' + ''.join(f'<li><a href="#{ss}">{html.escape(st)}</a></li>' for sn, st, ss in subs) + '</ul>') if subs else '') +
    '</li>' for num, t, sid, subs in secs)

intro_html = mdx.convert('\n\n'.join(intro_paras))

page = open('/home/claude/spekset-web/tools/manual_template.html').read()
page = page.replace('{{TOC}}', toc).replace('{{INTRO}}', intro_html).replace('{{BODY}}', body)
open('/home/claude/spekset-web/manual.html', 'w').write(page)
print(len(secs), 'sections', len(page) // 1024, 'KB')

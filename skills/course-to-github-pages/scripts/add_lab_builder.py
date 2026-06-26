#!/usr/bin/env python3
"""Inject a reusable, schema-driven deliverable builder into a Lab Guide.

Every module's `Module {N} - Lab Guide.html` must embed an in-guide workspace
where the learner builds that module's deliverable, then Copy markdown /
Download .md to commit to their repo (SKILL gotcha: "The Lab Guide is HTML and
embeds the deliverable builder"). Rather than hand-coding the JS per module,
describe the deliverable as a small JSON schema and let this script render it.

Usage:
    python add_lab_builder.py --html "Modules/Module 2 - Lab Guide.html" \
                              --config m2.json

Re-running is idempotent (it replaces a prior injection).

Schema (config JSON):
{
  "key": "course-m2-loopspec-v1",   # localStorage key, course-scoped + versioned
  "filename": "loop-spec.md",        # what Download writes; matches the repo path
  "docTitle": "Loop Spec",           # H1 of the generated markdown
  "subject": {"label": "Agent / workflow", "value": "Atlas"},   # optional top field
  "intro": "One line of HTML shown above the workspace.",
  "sections": [
    {"id":"x","type":"select","label":"...","opts":["A","B"],"value":"A"},
    {"id":"y","type":"text","label":"...","hint":"..."},
    {"id":"z","type":"textarea","label":"...","hint":"..."},
    {"id":"g","type":"group","label":"...","subs":[{"id":"a","label":"...","hint":"..."}]},
    {"id":"r","type":"rows","label":"...",
       "columns":[{"id":"c","label":"...","type":"text|select","opts":[...]}],
       "starter":[{"c":"..."}]}
  ],
  "debrief": {"label":"For #cohort-channel","hint":"..."}   # optional reflection
}

Markdown is auto-generated: each section becomes a `## label` block (text/select
verbatim, group -> bullet list, rows -> a markdown table); debrief is appended.
Banned-characters safe: emits no em-dash / en-dash (title uses ":", empty cell "·").
"""
import argparse, json, os, re

CSS = """
/* injected interactive builder */
.builder { background: rgba(96,165,250,0.05); border: 1px solid rgba(96,165,250,0.24); border-radius: 16px; padding: 24px 26px; margin: 28px 0; }
.builder .d-label { font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; color: #60a5fa; margin-bottom: 8px; }
.builder h2 { font-size: 20px; color: #fff; margin-bottom: 6px; }
.builder > p { font-size: 14px; margin-bottom: 8px; }
.bd-field { display: flex; align-items: center; gap: 10px; margin: 14px 0; flex-wrap: wrap; }
.bd-field label { font-size: 12px; color: #8899bb; font-family: 'IBM Plex Mono', monospace; letter-spacing: 0.04em; }
.builder input, .builder select, .builder textarea { font-family: 'Lato', sans-serif; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.14); color: #e8e8f0; border-radius: 8px; padding: 8px 10px; font-size: 13px; }
.builder input:focus, .builder select:focus, .builder textarea:focus { outline: none; border-color: #60a5fa; background: rgba(96,165,250,0.08); }
.builder select option { background: #0c2244; color: #e8e8f0; }
.bd-row { display: flex; flex-direction: column; gap: 5px; margin: 12px 0; }
.bd-row label { font-size: 12px; color: #8899bb; font-family: 'IBM Plex Mono', monospace; letter-spacing: 0.04em; }
.bd-row .bd-hint { font-size: 11px; color: #6b7589; font-style: italic; }
.bd-row textarea { width: 100%; }
.bd-row > input[type=text], .bd-row > select { width: 100%; max-width: 420px; }
.bd-group { border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 12px 16px 4px; margin: 14px 0; }
.bd-group .bd-glabel { font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: #60a5fa; margin-bottom: 4px; }
.bd-scroll { overflow-x: auto; margin: 8px 0 4px; }
table.bd-table { width: 100%; border-collapse: collapse; font-size: 13px; min-width: 560px; }
table.bd-table th { text-align: left; font-family: 'Poppins', sans-serif; font-size: 10px; text-transform: uppercase; letter-spacing: 0.06em; color: #60a5fa; padding: 8px 6px; border-bottom: 1px solid rgba(96,165,250,0.28); white-space: nowrap; }
table.bd-table td { padding: 6px; border-bottom: 1px solid rgba(255,255,255,0.06); vertical-align: middle; }
table.bd-table input[type=text], table.bd-table select { width: 100%; }
.bd-remove { background: transparent; border: none; color: #fca5a5; cursor: pointer; font-size: 18px; line-height: 1; padding: 4px 8px; border-radius: 6px; }
.bd-remove:hover { background: rgba(248,113,113,0.12); }
.bd-actions { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin: 16px 0 6px; }
.bd-btn { display: inline-flex; align-items: center; gap: 7px; cursor: pointer; border: none; background: #1241B0; color: #fff; font-family: 'Poppins', sans-serif; font-weight: 800; font-size: 13px; padding: 10px 18px; border-radius: 999px; box-shadow: 0 8px 20px rgba(18,65,176,0.35); transition: transform .15s; }
.bd-btn:hover { transform: translateY(-2px); }
.bd-btn.alt { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.16); box-shadow: none; }
.bd-btn.ghost { background: transparent; border: 1px solid rgba(252,165,165,0.3); color: #fca5a5; box-shadow: none; font-weight: 700; }
.bd-saved { font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: #6ee7b7; margin-left: auto; }
.bd-preview-wrap { margin-top: 18px; }
.bd-preview-wrap summary { cursor: pointer; font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: #60a5fa; padding: 6px 0; }
.bd-preview { background: #0a1326; border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 16px; font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: #cdd5e3; white-space: pre-wrap; max-height: 340px; overflow: auto; margin-top: 8px; }
.toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%) translateY(10px); background: #1241B0; color: #fff; padding: 11px 22px; border-radius: 999px; font-size: 13px; font-weight: 700; box-shadow: 0 10px 30px rgba(0,0,0,0.4); opacity: 0; pointer-events: none; transition: opacity .2s, transform .2s; z-index: 200; }
.toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }
"""

BUILDER_HTML = """
  <!-- INTERACTIVE BUILDER (injected) -->
  <div class="builder bd" id="builder">
    <div class="d-label">Build it here</div>
    <h2 id="bd-title">Workspace</h2>
    <p id="bd-intro"></p>
    <div id="bd-subject"></div>
    <div id="bd-body"></div>
    <div class="bd-actions">
      <button class="bd-btn" id="bd-copy" type="button">\U0001F4CB Copy markdown</button>
      <button class="bd-btn" id="bd-download" type="button">\u2b07 Download</button>
      <button class="bd-btn ghost" id="bd-reset" type="button">Reset</button>
      <span class="bd-saved" id="bd-saved"></span>
    </div>
    <details class="bd-preview-wrap"><summary>Preview the markdown \u25be</summary><div class="bd-preview" id="bd-preview"></div></details>
  </div>
"""

ENGINE = r"""
(function () {
  var CFG = window.LAB_CFG; if (!CFG) return;
  var KEY = CFG.key;
  var bodyEl = document.getElementById('bd-body');
  var subjEl = document.getElementById('bd-subject');
  document.getElementById('bd-title').textContent = CFG.docTitle + ' workspace';
  document.getElementById('bd-intro').innerHTML = CFG.intro;
  document.getElementById('bd-download').textContent = '\u2b07 Download ' + CFG.filename;
  var previewEl = document.getElementById('bd-preview');
  var savedEl = document.getElementById('bd-saved');
  var toastEl = document.getElementById('toast');

  function emptyRow(sec) { var o = {}; sec.columns.forEach(function (c) { o[c.id] = c.type === 'select' ? c.opts[0] : ''; }); return o; }
  function defaults() {
    var s = { subject: CFG.subject ? CFG.subject.value : '', debrief: '', val: {}, grp: {}, rows: {} };
    CFG.sections.forEach(function (sec) {
      if (sec.type === 'group') { s.grp[sec.id] = {}; sec.subs.forEach(function (sub) { s.grp[sec.id][sub.id] = ''; }); }
      else if (sec.type === 'rows') { s.rows[sec.id] = sec.starter ? sec.starter.map(function (r) { return Object.assign({}, r); }) : [emptyRow(sec)]; }
      else { s.val[sec.id] = sec.value !== undefined ? sec.value : ''; }
    });
    return s;
  }
  function load() {
    var d = defaults();
    try { var raw = localStorage.getItem(KEY); if (raw) { var p = JSON.parse(raw);
      if (p.subject !== undefined) d.subject = p.subject;
      if (p.debrief !== undefined) d.debrief = p.debrief;
      ['val', 'grp', 'rows'].forEach(function (k) { if (p[k]) for (var id in p[k]) d[k][id] = p[k][id]; });
    } } catch (e) {}
    return d;
  }
  var state = load();

  function save() { try { localStorage.setItem(KEY, JSON.stringify(state)); savedEl.textContent = '\u2713 saved'; clearTimeout(save._t); save._t = setTimeout(function () { savedEl.textContent = ''; }, 1500); } catch (e) {} preview(); }
  function esc(s) { return (s || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function lbl(sec) { return '<label>' + esc(sec.label) + '</label>' + (sec.hint ? '<span class="bd-hint">' + esc(sec.hint) + '</span>' : ''); }

  function renderSection(sec) {
    var wrap = document.createElement('div');
    if (sec.type === 'select') {
      wrap.className = 'bd-row'; wrap.innerHTML = lbl(sec) + '<select></select>';
      var sl = wrap.querySelector('select');
      sec.opts.forEach(function (o) { var op = document.createElement('option'); op.textContent = o; if (o === state.val[sec.id]) op.selected = true; sl.appendChild(op); });
      sl.addEventListener('change', function () { state.val[sec.id] = sl.value; save(); });
    } else if (sec.type === 'text') {
      wrap.className = 'bd-row'; wrap.innerHTML = lbl(sec) + '<input type="text">';
      var inp = wrap.querySelector('input'); inp.value = state.val[sec.id] || ''; inp.addEventListener('input', function () { state.val[sec.id] = inp.value; save(); });
    } else if (sec.type === 'textarea') {
      wrap.className = 'bd-row'; wrap.innerHTML = lbl(sec) + '<textarea rows="3"></textarea>';
      var ta = wrap.querySelector('textarea'); ta.value = state.val[sec.id] || ''; ta.addEventListener('input', function () { state.val[sec.id] = ta.value; save(); });
    } else if (sec.type === 'group') {
      wrap.className = 'bd-group'; wrap.innerHTML = '<div class="bd-glabel">' + esc(sec.label) + '</div>';
      sec.subs.forEach(function (sub) {
        var r = document.createElement('div'); r.className = 'bd-row';
        r.innerHTML = '<label>' + esc(sub.label) + '</label>' + (sub.hint ? '<span class="bd-hint">' + esc(sub.hint) + '</span>' : '') + '<textarea rows="2"></textarea>';
        var ta = r.querySelector('textarea'); ta.value = (state.grp[sec.id] && state.grp[sec.id][sub.id]) || '';
        ta.addEventListener('input', function () { if (!state.grp[sec.id]) state.grp[sec.id] = {}; state.grp[sec.id][sub.id] = ta.value; save(); });
        wrap.appendChild(r);
      });
    } else if (sec.type === 'rows') {
      wrap.className = 'bd-row';
      wrap.innerHTML = lbl(sec) + '<div class="bd-scroll"><table class="bd-table"><thead><tr>' +
        sec.columns.map(function (c) { return '<th>' + esc(c.label) + '</th>'; }).join('') + '<th></th></tr></thead><tbody></tbody></table></div>' +
        '<div style="margin-top:6px;"><button class="bd-btn alt" type="button" data-add="1">+ Add row</button>' +
        (sec.starter ? ' <button class="bd-btn alt" type="button" data-starter="1">\u21bb Starter rows</button>' : '') + '</div>';
      var tbody = wrap.querySelector('tbody');
      function draw() {
        tbody.innerHTML = '';
        (state.rows[sec.id] || []).forEach(function (row, ri) {
          var tr = document.createElement('tr');
          sec.columns.forEach(function (c) {
            var td = document.createElement('td');
            if (c.type === 'select') {
              var sl = document.createElement('select'); c.opts.forEach(function (o) { var op = document.createElement('option'); op.textContent = o; if (o === row[c.id]) op.selected = true; sl.appendChild(op); });
              sl.addEventListener('change', function () { row[c.id] = sl.value; save(); }); td.appendChild(sl);
            } else {
              var inp = document.createElement('input'); inp.type = 'text'; inp.value = row[c.id] || '';
              inp.addEventListener('input', function () { row[c.id] = inp.value; save(); }); td.appendChild(inp);
            }
            tr.appendChild(td);
          });
          var tdx = document.createElement('td'); var rm = document.createElement('button'); rm.className = 'bd-remove'; rm.type = 'button'; rm.innerHTML = '\u00d7';
          rm.addEventListener('click', function () { state.rows[sec.id].splice(ri, 1); draw(); save(); }); tdx.appendChild(rm); tr.appendChild(tdx);
          tbody.appendChild(tr);
        });
      }
      wrap.querySelector('[data-add]').addEventListener('click', function () { if (!state.rows[sec.id]) state.rows[sec.id] = []; state.rows[sec.id].push(emptyRow(sec)); draw(); save(); });
      if (sec.starter) wrap.querySelector('[data-starter]').addEventListener('click', function () { state.rows[sec.id] = sec.starter.map(function (r) { return Object.assign({}, r); }); draw(); save(); });
      draw();
    }
    return wrap;
  }

  function render() {
    if (CFG.subject) {
      subjEl.innerHTML = '<div class="bd-field"><label>' + esc(CFG.subject.label) + '</label><input type="text" id="bd-subject-input" style="min-width:220px;"></div>';
      var si = document.getElementById('bd-subject-input'); si.value = state.subject || CFG.subject.value;
      si.addEventListener('input', function () { state.subject = si.value; save(); });
    }
    bodyEl.innerHTML = '';
    CFG.sections.forEach(function (sec) { bodyEl.appendChild(renderSection(sec)); });
    if (CFG.debrief) {
      var d = document.createElement('div'); d.className = 'bd-row'; d.style.marginTop = '14px';
      d.innerHTML = '<label>' + esc(CFG.debrief.label) + '</label>' + (CFG.debrief.hint ? '<span class="bd-hint">' + esc(CFG.debrief.hint) + '</span>' : '') + '<textarea rows="2"></textarea>';
      var dt = d.querySelector('textarea'); dt.value = state.debrief || ''; dt.addEventListener('input', function () { state.debrief = dt.value; save(); });
      bodyEl.appendChild(d);
    }
    preview();
  }

  function md() {
    var out = '# ' + CFG.docTitle + (CFG.subject ? ': ' + (state.subject || CFG.subject.value) : '') + '\n\n';
    CFG.sections.forEach(function (sec) {
      out += '## ' + sec.label + '\n\n';
      if (sec.type === 'group') {
        sec.subs.forEach(function (sub) { var v = (state.grp[sec.id] && state.grp[sec.id][sub.id]) || ''; out += '- **' + sub.label + '**: ' + (v.trim() || '_\u2026_') + '\n'; });
        out += '\n';
      } else if (sec.type === 'rows') {
        out += '| ' + sec.columns.map(function (c) { return c.label; }).join(' | ') + ' |\n|' + sec.columns.map(function () { return '---'; }).join('|') + '|\n';
        (state.rows[sec.id] || []).forEach(function (row) { out += '| ' + sec.columns.map(function (c) { return (row[c.id] || '').replace(/\n/g, ' ') || '\u00b7'; }).join(' | ') + ' |\n'; });
        out += '\n';
      } else { var v = state.val[sec.id] || ''; out += (v.trim() || '_\u2026_') + '\n\n'; }
    });
    if (CFG.debrief && (state.debrief || '').trim()) { out += '## ' + CFG.debrief.label + '\n\n' + state.debrief.trim() + '\n'; }
    return out;
  }
  function preview() { previewEl.textContent = md(); }
  function toast(m) { toastEl.textContent = m; toastEl.classList.add('show'); clearTimeout(toast._t); toast._t = setTimeout(function () { toastEl.classList.remove('show'); }, 1800); }

  document.getElementById('bd-copy').addEventListener('click', function () { var t = md(); if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(t).then(function () { toast('Markdown copied'); }, function () { fb(t); }); } else fb(t); });
  function fb(t) { var ta = document.createElement('textarea'); ta.value = t; document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); toast('Markdown copied'); } catch (e) { toast('Copy failed, select in preview'); } document.body.removeChild(ta); }
  document.getElementById('bd-download').addEventListener('click', function () { var b = new Blob([md()], { type: 'text/markdown' }); var a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = CFG.filename; document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(a.href); toast('Downloaded ' + CFG.filename); });
  document.getElementById('bd-reset').addEventListener('click', function () { if (!confirm('Clear the workspace and start over?')) return; state = defaults(); save(); render(); });

  render();
})();
"""


def inject(html_path, cfg):
    t = open(html_path, encoding="utf-8").read()
    # remove any previous injection so re-runs are idempotent
    t = re.sub(r'\n\s*<!-- INTERACTIVE BUILDER \(injected\) -->.*?</div>\s*(?=\n\s*<!-- DELIVERABLE|\n\s*<div class="deliverable")', "\n", t, flags=re.S)
    t = re.sub(r'\n<div class="toast" id="toast"></div>', "", t)
    t = re.sub(r'\n<script>window\.LAB_CFG=.*?</script>\s*<script>/\*lab-builder\*/.*?</script>', "", t, flags=re.S)

    if ".bd-btn" not in t:
        t = t.replace("</style>", CSS + "</style>", 1)

    anchor = '<div class="deliverable">'
    idx = t.find(anchor)
    if idx == -1:
        raise SystemExit("No '<div class=\"deliverable\">' anchor in " + html_path +
                         " (the builder is injected just before the deliverable summary).")
    t = t[:idx] + BUILDER_HTML.strip() + "\n\n  " + t[idx:]

    tail = '\n<div class="toast" id="toast"></div>\n'
    tail += "<script>window.LAB_CFG=" + json.dumps(cfg, ensure_ascii=False) + ";</script>\n"
    tail += "<script>/*lab-builder*/" + ENGINE + "</script>\n"
    t = t.replace("</body>", tail + "</body>", 1)

    open(html_path, "w", encoding="utf-8").write(t)


def main():
    ap = argparse.ArgumentParser(description="Inject a schema-driven deliverable builder into a Lab Guide HTML.")
    ap.add_argument("--html", required=True, help="path to 'Module {N} - Lab Guide.html'")
    ap.add_argument("--config", required=True, help="path to the deliverable schema JSON")
    a = ap.parse_args()
    cfg = json.load(open(a.config, encoding="utf-8"))
    for req in ("key", "filename", "docTitle", "intro", "sections"):
        if req not in cfg:
            raise SystemExit("config missing required field: " + req)
    inject(a.html, cfg)
    print("Injected builder into " + os.path.basename(a.html) + " -> " + cfg["filename"])


if __name__ == "__main__":
    main()

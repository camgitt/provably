"""Local web dashboard for proofagent eval results."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from proofagent.report import load_latest_results

_PORT = 7175


def _collect_all_results(results_dir: str = ".proofagent/results") -> list[dict]:
    rd = Path(results_dir)
    if not rd.exists():
        return []
    files = sorted(rd.glob("eval_*.json"), reverse=True)
    runs = []
    for f in files:
        with open(f) as fh:
            data = json.load(fh)
            data["_file"] = f.name
            runs.append(data)
    return runs


def _collect_live_results(test_path: str = "tests/", extra_args: list[str] | None = None) -> dict:
    paths = test_path.split() if isinstance(test_path, str) else [test_path]
    cmd = [sys.executable, "-m", "pytest", *paths, "--tb=short", "-v"]
    if extra_args:
        cmd.extend(extra_args)

    env = os.environ.copy()
    env["PROVABLY_SAVE_RESULTS"] = "1"

    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    stdout = result.stdout
    stderr = result.stderr

    tests = []
    for line in stdout.split("\n"):
        line = line.strip()
        if " PASSED" in line:
            name = line.split(" PASSED")[0].strip()
            tests.append({"name": name, "status": "passed", "cost": 0, "latency": 0})
        elif " FAILED" in line:
            name = line.split(" FAILED")[0].strip()
            tests.append({"name": name, "status": "failed", "cost": 0, "latency": 0})

    # Extract docstrings from source files
    _attach_docstrings(tests)

    passed = sum(1 for t in tests if t["status"] == "passed")
    failed = sum(1 for t in tests if t["status"] == "failed")
    total = passed + failed

    return {
        "tests": tests,
        "summary": {"passed": passed, "failed": failed, "total": total, "score": passed / total if total > 0 else 0},
        "stdout": stdout,
        "stderr": stderr,
    }


def _attach_docstrings(tests: list[dict]) -> None:
    """Parse source files to extract test docstrings."""
    import ast

    cache: dict[str, dict[str, str]] = {}  # file -> {func_name: docstring}

    for t in tests:
        parts = (t.get("name") or "").split("::")
        if len(parts) < 2:
            continue
        filepath, funcname = parts[0], parts[-1]

        if filepath not in cache:
            cache[filepath] = {}
            try:
                with open(filepath) as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        doc = ast.get_docstring(node)
                        if doc:
                            cache[filepath][node.name] = doc.split("\n")[0].strip()
            except Exception:
                pass

        doc = cache.get(filepath, {}).get(funcname, "")
        if doc:
            t["description"] = doc


def generate_dashboard_html(results: dict | None = None, live_results: dict | None = None) -> str:
    tests_json = "[]"
    summary_json = "{}"
    raw_stdout = ""
    if live_results:
        tests_json = json.dumps(live_results.get("tests", []))
        summary_json = json.dumps(live_results.get("summary", {}))
        raw_stdout = live_results.get("stdout", "")
    elif results:
        tests_json = json.dumps(results.get("results", []))
        summary_json = json.dumps(results.get("summary", {}))

    raw_stdout_json = json.dumps(raw_stdout)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>proofagent</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  :root {{
    --bg: oklch(0.145 0.012 255);
    --bg-raised: oklch(0.175 0.014 255);
    --bg-inset: oklch(0.125 0.01 255);
    --bg-hover: oklch(0.20 0.015 255);
    --border: oklch(0.26 0.012 255);
    --border-subtle: oklch(0.22 0.01 255);
    --text: oklch(0.92 0.008 255);
    --text-2: oklch(0.68 0.01 255);
    --text-3: oklch(0.48 0.008 255);
    --text-4: oklch(0.36 0.006 255);
    --pass: oklch(0.70 0.16 158);
    --pass-soft: oklch(0.70 0.16 158 / 0.08);
    --fail: oklch(0.68 0.19 22);
    --fail-soft: oklch(0.68 0.19 22 / 0.08);
    --cost: oklch(0.76 0.13 80);
    --speed: oklch(0.64 0.06 255);
  }}

  html {{ font-size: 15px; }}

  body {{
    font-family: 'IBM Plex Sans', system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }}

  /* ===== LAYOUT ===== */
  .wrap {{
    max-width: 880px;
    margin: 0 auto;
    padding: 0 24px;
  }}

  /* ===== HEADER ===== */
  .header {{
    padding: 48px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }}

  .header-left {{ flex: 1; }}

  .mark {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    color: var(--text-4);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 10px;
  }}

  .headline {{
    font-size: 28px;
    font-weight: 300;
    letter-spacing: -0.5px;
    line-height: 1.2;
    color: var(--text);
  }}

  .headline strong {{
    font-weight: 600;
  }}

  .header-right {{
    text-align: right;
    padding-top: 8px;
  }}

  .run-time {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: var(--text-3);
  }}

  .run-status {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    margin-top: 4px;
    font-weight: 500;
  }}

  .run-status.all-pass {{ color: var(--pass); }}
  .run-status.has-fail {{ color: var(--fail); }}

  /* ===== DIVIDER ===== */
  hr {{
    border: none;
    border-top: 1px solid var(--border-subtle);
    margin: 32px 0;
  }}

  /* ===== STATS ===== */
  .stats {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: 0;
    margin: 36px 0 0;
  }}

  .stat {{
    padding: 0 28px 0 0;
    position: relative;
  }}

  .stat + .stat {{
    padding-left: 28px;
    border-left: 1px solid var(--border-subtle);
  }}

  .stat-n {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 32px;
    font-weight: 400;
    line-height: 1;
    letter-spacing: -1px;
  }}

  .stat-l {{
    font-size: 12px;
    color: var(--text-3);
    margin-top: 8px;
    line-height: 1.3;
  }}

  /* ===== PASS STRIP ===== */
  .strip {{
    margin: 32px 0 0;
    display: flex;
    gap: 3px;
    height: 6px;
  }}

  .strip-seg {{
    border-radius: 1px;
    transition: opacity 0.2s;
  }}

  .strip-seg:hover {{
    opacity: 0.8;
  }}

  .strip-pass {{ background: var(--pass); }}
  .strip-fail {{ background: var(--fail); }}

  /* ===== TESTS ===== */
  .section-head {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin: 44px 0 14px;
  }}

  .section-label {{
    font-size: 13px;
    font-weight: 600;
    color: var(--text-2);
  }}

  .section-meta {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: var(--text-4);
  }}

  .tbl {{
    width: 100%;
    border-collapse: collapse;
    border: 1px solid var(--border);
    border-radius: 5px;
    overflow: hidden;
  }}

  .tbl thead th {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10.5px;
    font-weight: 500;
    color: var(--text-4);
    text-transform: uppercase;
    letter-spacing: 0.4px;
    padding: 9px 16px;
    text-align: left;
    background: var(--bg-raised);
    border-bottom: 1px solid var(--border);
  }}

  .tbl thead th:nth-child(3),
  .tbl thead th:nth-child(4) {{
    text-align: right;
  }}

  .tbl tbody tr {{
    border-bottom: 1px solid var(--border-subtle);
    transition: background 0.1s;
  }}

  .tbl tbody tr:last-child {{
    border-bottom: none;
  }}

  .tbl tbody tr:hover {{
    background: var(--bg-hover);
  }}

  .tbl td {{
    padding: 10px 16px;
    font-size: 13px;
    vertical-align: middle;
  }}

  .tbl td:nth-child(3),
  .tbl td:nth-child(4) {{
    text-align: right;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: var(--text-3);
  }}

  .tbl .name-cell {{
    display: flex;
    align-items: center;
    gap: 10px;
  }}

  .indicator {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
    flex-shrink: 0;
  }}

  .indicator-pass {{ background: var(--pass); }}
  .indicator-fail {{ background: var(--fail); }}

  .t-name {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12.5px;
    font-weight: 500;
    color: var(--text);
  }}

  .t-file {{
    font-weight: 400;
    color: var(--text-4);
    margin-left: 6px;
    font-size: 11.5px;
  }}

  .t-desc {{
    font-family: 'IBM Plex Sans', system-ui, sans-serif;
    font-size: 11.5px;
    font-weight: 400;
    color: var(--text-3);
    margin-left: 8px;
  }}

  .t-err {{
    font-size: 11.5px;
    color: var(--fail);
    margin-top: 3px;
    margin-left: 16px;
  }}

  /* ===== OUTPUT TOGGLE ===== */
  .toggle {{
    margin: 36px 0 0;
  }}

  .toggle-btn {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: var(--text-3);
    background: none;
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 6px 14px;
    cursor: pointer;
    transition: all 0.15s;
  }}

  .toggle-btn:hover {{
    color: var(--text-2);
    border-color: var(--text-3);
  }}

  .toggle-content {{
    display: none;
    margin-top: 12px;
  }}

  .toggle-content.open {{
    display: block;
  }}

  .raw {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11.5px;
    line-height: 1.7;
    background: var(--bg-inset);
    border: 1px solid var(--border-subtle);
    border-radius: 5px;
    padding: 16px 20px;
    overflow-x: auto;
    white-space: pre-wrap;
    word-break: break-word;
    color: var(--text-3);
    max-height: 320px;
    overflow-y: auto;
  }}

  /* ===== FOOTER ===== */
  .foot {{
    margin: 56px 0 40px;
    padding-top: 20px;
    border-top: 1px solid var(--border-subtle);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 11.5px;
    color: var(--text-4);
  }}

  .foot a {{
    color: var(--text-3);
    text-decoration: none;
    transition: color 0.15s;
  }}

  .foot a:hover {{ color: var(--text); }}

  /* ===== EMPTY ===== */
  .empty-state {{
    padding: 56px 0;
    color: var(--text-3);
    font-size: 14px;
    line-height: 1.8;
  }}

  .empty-state code {{
    font-family: 'IBM Plex Mono', monospace;
    background: var(--bg-raised);
    padding: 3px 8px;
    border-radius: 3px;
    font-size: 12.5px;
    color: var(--text-2);
  }}

  /* ===== ANIMATION ===== */
  .stat, .tbl tbody tr {{
    opacity: 0;
    animation: enter 0.35s ease forwards;
  }}

  @keyframes enter {{
    from {{ opacity: 0; transform: translateY(6px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}

  .stat:nth-child(1) {{ animation-delay: 0.05s; }}
  .stat:nth-child(2) {{ animation-delay: 0.1s; }}
  .stat:nth-child(3) {{ animation-delay: 0.15s; }}
  .stat:nth-child(4) {{ animation-delay: 0.2s; }}

  .tbl tbody tr {{ animation-delay: calc(0.25s + var(--i, 0) * 0.03s); }}
</style>
</head>
<body>
<div class="wrap">

  <div class="header">
    <div class="header-left">
      <div class="mark">proofagent</div>
      <div class="headline" id="headline">Eval Results</div>
    </div>
    <div class="header-right">
      <div class="run-time" id="run-time"></div>
      <div class="run-status" id="run-status"></div>
    </div>
  </div>

  <div class="stats" id="stats">
    <div class="stat">
      <div class="stat-n color-pass" style="color: var(--pass)" id="s-rate">--</div>
      <div class="stat-l">pass rate</div>
    </div>
    <div class="stat">
      <div class="stat-n" id="s-total">0</div>
      <div class="stat-l">tests ran</div>
    </div>
    <div class="stat">
      <div class="stat-n" style="color: var(--cost)" id="s-cost">$0</div>
      <div class="stat-l">total cost</div>
    </div>
    <div class="stat">
      <div class="stat-n" style="color: var(--speed)" id="s-speed">--</div>
      <div class="stat-l">avg latency</div>
    </div>
  </div>

  <div class="strip" id="strip"></div>

  <div class="section-head">
    <span class="section-label">Tests</span>
    <span class="section-meta" id="count-meta"></span>
  </div>

  <table class="tbl" id="tbl">
    <thead>
      <tr>
        <th style="width: 50%;">Name</th>
        <th>File</th>
        <th style="width: 80px;">Cost</th>
        <th style="width: 80px;">Time</th>
      </tr>
    </thead>
    <tbody id="tbody"></tbody>
  </table>

  <div class="toggle" id="toggle-wrap" style="display:none">
    <button class="toggle-btn" id="toggle-btn">Show raw output</button>
    <div class="toggle-content" id="toggle-content">
      <pre class="raw" id="raw-out"></pre>
    </div>
  </div>

  <div class="foot">
    <span>proofagent v0.3.0</span>
    <span><a href="https://github.com/camgitt/proofagent">source</a> &middot; <a href="https://pypi.org/project/proofagent/">pypi</a></span>
  </div>

</div>

<script>
const tests = {tests_json};
const summary = {summary_json};
const rawStdout = {raw_stdout_json};

(function() {{
  if (!tests.length && !summary.total) {{
    document.getElementById('tbody').innerHTML =
      '<tr><td colspan="4"><div class="empty-state">No results yet.<br><br>Run tests with:<br><code>proofagent dashboard --test tests/</code></div></td></tr>';
    return;
  }}

  const passed = summary.passed || 0;
  const failed = summary.failed || 0;
  const total = summary.total || 0;
  const pct = total > 0 ? (passed / total * 100) : 0;

  // Headline
  if (failed === 0) {{
    document.getElementById('headline').innerHTML = '<strong>' + total + ' tests</strong>, all passing';
  }} else {{
    document.getElementById('headline').innerHTML = '<strong>' + failed + ' of ' + total + '</strong> tests need attention';
  }}

  // Time & status
  const d = new Date();
  document.getElementById('run-time').textContent = d.toLocaleDateString(undefined, {{ month: 'short', day: 'numeric' }}) + ' at ' + d.toLocaleTimeString([], {{ hour: '2-digit', minute: '2-digit' }});

  const statusEl = document.getElementById('run-status');
  if (failed === 0) {{
    statusEl.textContent = 'PASS';
    statusEl.className = 'run-status all-pass';
  }} else {{
    statusEl.textContent = failed + ' FAIL';
    statusEl.className = 'run-status has-fail';
  }}

  // Stats
  document.getElementById('s-rate').textContent = pct.toFixed(0) + '%';
  if (failed > 0) document.getElementById('s-rate').style.color = 'var(--fail)';
  document.getElementById('s-total').textContent = total;

  const totalCost = tests.reduce((s, t) => s + (t.cost || 0), 0);
  document.getElementById('s-cost').textContent = totalCost > 0 ? '$' + totalCost.toFixed(4) : '$0';

  const lats = tests.filter(t => t.latency > 0).map(t => t.latency);
  const avg = lats.length > 0 ? lats.reduce((a, b) => a + b) / lats.length : 0;
  document.getElementById('s-speed').textContent = avg > 0 ? avg.toFixed(2) + 's' : '<1ms';

  // Strip - one segment per test
  const strip = document.getElementById('strip');
  tests.forEach(t => {{
    const seg = document.createElement('div');
    seg.className = 'strip-seg ' + (t.status === 'passed' ? 'strip-pass' : 'strip-fail');
    seg.style.flex = '1';
    seg.title = (t.name || '').split('::').pop();
    strip.appendChild(seg);
  }});

  // Count
  document.getElementById('count-meta').textContent = passed + ' passed' + (failed > 0 ? ' / ' + failed + ' failed' : '');

  // Table
  const tbody = document.getElementById('tbody');
  tests.forEach((t, i) => {{
    const ok = t.status === 'passed';
    const parts = (t.name || '').split('::');
    const file = parts.length > 1 ? parts[0] : '';
    const name = parts.length > 1 ? parts[1] : t.name;

    const tr = document.createElement('tr');
    tr.style.setProperty('--i', i);
    const desc = t.description || '';
    tr.innerHTML =
      '<td><div class="name-cell"><span class="indicator ' + (ok ? 'indicator-pass' : 'indicator-fail') + '"></span><span class="t-name">' + name + '</span>' +
      (desc ? '<span class="t-desc">' + desc + '</span>' : '') +
      '</div>' +
      (t.error ? '<div class="t-err">' + (t.error || '').substring(0, 140) + '</div>' : '') +
      '</td>' +
      '<td style="font-family: IBM Plex Mono, monospace; font-size: 11.5px; color: var(--text-4);">' + file + '</td>' +
      '<td>' + (t.cost ? '$' + t.cost.toFixed(4) : '\u2014') + '</td>' +
      '<td>' + (t.latency ? t.latency.toFixed(2) + 's' : '<1ms') + '</td>';
    tbody.appendChild(tr);
  }});

  // Raw output toggle
  if (rawStdout) {{
    document.getElementById('toggle-wrap').style.display = '';
    document.getElementById('raw-out').textContent = rawStdout;
    document.getElementById('toggle-btn').addEventListener('click', function() {{
      const c = document.getElementById('toggle-content');
      const open = c.classList.toggle('open');
      this.textContent = open ? 'Hide raw output' : 'Show raw output';
    }});
  }}
}})();
</script>
</body>
</html>"""


class DashboardHandler(SimpleHTTPRequestHandler):
    html_content = ""

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(self.html_content.encode("utf-8"))
        elif self.path == "/api/results":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            results = _collect_all_results()
            self.wfile.write(json.dumps(results).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def serve(test_path: str | None = None, port: int = _PORT, no_browser: bool = False):
    live_results = None
    results = None

    if test_path:
        print(f"  Running tests: {test_path}")
        live_results = _collect_live_results(test_path)
        passed = live_results["summary"]["passed"]
        total = live_results["summary"]["total"]
        failed = total - passed
        status = "\033[32mALL PASS\033[0m" if failed == 0 else f"\033[31m{failed} FAILED\033[0m"
        print(f"  Results: {passed}/{total} passed \u2014 {status}")
    else:
        results = load_latest_results()
        if results:
            s = results.get("summary", {})
            print(f"  Loaded results: {s.get('passed', 0)}/{s.get('total', 0)} passed")
        else:
            print("  No saved results. Run with --test to generate.")

    html = generate_dashboard_html(results=results, live_results=live_results)
    DashboardHandler.html_content = html

    server = HTTPServer(("127.0.0.1", port), DashboardHandler)
    url = f"http://localhost:{port}"
    print(f"  Dashboard: {url}")

    if not no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")
        server.server_close()

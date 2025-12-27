"""Debug overlay injection for scene HTML."""
import json
from typing import List, Dict, Any


def inject_debug_overlay(html: str, voiceover_segments: List[Dict[str, Any]]) -> str:
    """Inject debug overlay into scene HTML (post-LLM processing).
    
    Adds a fixed overlay at the top showing:
    - Current elapsed time
    - Current voiceover segment text
    """
    
    overlay_html = '''
<div id="debugOverlay" style="position:fixed;top:0;left:0;right:0;background:rgba(0,0,0,0.9);color:#fff;font-family:'SF Mono',monospace;font-size:14px;padding:16px 24px;z-index:9999;display:flex;gap:24px;align-items:center;">
  <div id="debugTimer" style="font-size:28px;font-weight:bold;min-width:100px;color:#4ade80;">0.0s</div>
  <div id="debugScript" style="flex:1;font-size:16px;line-height:1.5;color:#e5e7eb;">—</div>
</div>
'''
    
    segments_json = json.dumps(voiceover_segments)
    end_ms = voiceover_segments[-1]['end_ms'] if voiceover_segments else 30000
    
    overlay_js = f'''
<script>
(function() {{
  const __voSegments = {segments_json};
  let __startTime = null;
  
  function __updateDebug() {{
    if (!__startTime) return;
    const elapsed = Date.now() - __startTime;
    document.getElementById('debugTimer').textContent = (elapsed/1000).toFixed(1) + 's';
    const seg = __voSegments.find(s => elapsed >= s.start_ms && elapsed < s.end_ms);
    document.getElementById('debugScript').textContent = seg ? '"' + seg.text + '"' : '—';
    if (elapsed < {end_ms} + 2000) requestAnimationFrame(__updateDebug);
  }}
  
  const __origPlayAll = window.__shortsPlayAll;
  window.__shortsPlayAll = function() {{
    __startTime = Date.now();
    __updateDebug();
    if (__origPlayAll) __origPlayAll.call(window);
  }};
}})();
</script>
'''
    
    # Inject after <body>
    html = html.replace('<body>', '<body>\n' + overlay_html, 1)
    # Inject before </body>
    html = html.replace('</body>', overlay_js + '\n</body>', 1)
    
    return html


#!/usr/bin/env python3
"""
Generate an animated GitHub Stats SVG using real data from the GitHub API.
Uses only SMIL animations, no JS, compliant with GitHub README SVG renderers.
"""
import os
import json
import urllib.request
import sys

USERNAME = "adityapatil400"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

def fetch_json(url):
    headers = {"User-Agent": "GitHub-Stats-Generator"}
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None

def generate_svg(user_data, repos_data, output_path="assets/stats.svg"):
    public_repos = user_data.get("public_repos", 8) if user_data else 8
    followers = user_data.get("followers", 0) if user_data else 0
    
    total_stars = 0
    total_forks = 0
    lang_counts = {}
    
    if repos_data:
        for repo in repos_data:
            if not repo.get("fork", False):
                total_stars += repo.get("stargazers_count", 0)
                total_forks += repo.get("forks_count", 0)
                lang = repo.get("language")
                if lang:
                    lang_counts[lang] = lang_counts.get(lang, 0) + 1
    else:
        lang_counts = {"TypeScript": 4, "JavaScript": 2, "Python": 2, "HTML": 1}

    total_langs = sum(lang_counts.values()) or 1
    sorted_langs = sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:4]

    colors = {
        "TypeScript": "#3178c6",
        "JavaScript": "#f7df1e",
        "Python": "#3572A5",
        "HTML": "#e34c26",
        "CSS": "#563d7c",
        "C#": "#178600",
        "C++": "#f34b7d",
        "C": "#555555",
        "Java": "#b07219"
    }

    # Generate language bar segments and legend
    total_bar_width = 360
    current_x = 0
    bar_rects = []
    legend_items = []
    
    for i, (lang, count) in enumerate(sorted_langs):
        pct = (count / total_langs) * 100
        seg_w = max(int((count / total_langs) * total_bar_width), 8)
        c = colors.get(lang, "#00d4ff" if i % 2 == 0 else "#a855f7")
        
        bar_rects.append(f'''
        <rect x="{current_x}" y="0" width="{seg_w}" height="10" rx="3" fill="{c}">
          <animate attributeName="width" values="0;{seg_w}" dur="1.2s" begin="{0.2 + i * 0.15:.2f}s" fill="freeze"/>
        </rect>
        ''')
        current_x += seg_w + 2

        legend_items.append(f'''
        <g transform="translate({40 + (i % 2) * 180}, {145 + (i // 2) * 32})">
          <circle cx="6" cy="6" r="4" fill="{c}"/>
          <text x="18" y="10" class="font-mono" font-size="11.5" fill="#f0f6fc">{lang}</text>
          <text x="140" y="10" text-anchor="end" class="font-mono" font-size="11" fill="#8b949e">{pct:.1f}%</text>
        </g>
        ''')

    bars_markup = "\n".join(bar_rects)
    legend_markup = "\n".join(legend_items)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 230" width="100%" height="100%">
  <defs>
    <linearGradient id="statBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1117"/>
      <stop offset="100%" stop-color="#0a0e27"/>
    </linearGradient>

    <linearGradient id="statCardBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#161b22"/>
      <stop offset="100%" stop-color="#0f141c"/>
    </linearGradient>

    <filter id="numGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <style>
    .font-sans {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
    .font-mono {{ font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace; }}
    .stat-title {{ font-size: 14px; font-weight: 700; fill: #f0f6fc; }}
    .stat-label {{ font-size: 11px; fill: #8b949e; font-family: 'SF Mono', monospace; }}
    .stat-val {{ font-size: 24px; font-weight: 800; font-family: 'SF Mono', monospace; }}

    @media (prefers-reduced-motion: reduce) {{
      .anim-grow {{ animation: none !important; }}
    }}
  </style>

  <!-- Container -->
  <rect x="3" y="3" width="844" height="224" rx="12" fill="url(#statBg)" stroke="#30363d" stroke-width="1.2"/>

  <!-- Left Column: Real-time Stats Grid -->
  <g transform="translate(25, 20)">
    <text x="0" y="16" class="font-sans stat-title">📊 Real-Time GitHub Metrics</text>

    <!-- Card 1: Repos -->
    <g transform="translate(0, 32)">
      <rect width="185" height="68" rx="8" fill="url(#statCardBg)" stroke="#30363d" stroke-width="1"/>
      <text x="16" y="24" class="stat-label">PUBLIC REPOSITORIES</text>
      <text x="16" y="54" fill="#00d4ff" class="stat-val" filter="url(#numGlow)">{public_repos}</text>
      <text x="165" y="52" text-anchor="end" font-size="18">📦</text>
    </g>

    <!-- Card 2: Stars -->
    <g transform="translate(195, 32)">
      <rect width="185" height="68" rx="8" fill="url(#statCardBg)" stroke="#30363d" stroke-width="1"/>
      <text x="16" y="24" class="stat-label">TOTAL REPO STARS</text>
      <text x="16" y="54" fill="#ffbd2e" class="stat-val" filter="url(#numGlow)">{total_stars}</text>
      <text x="165" y="52" text-anchor="end" font-size="18">⭐</text>
    </g>

    <!-- Card 3: Forks -->
    <g transform="translate(0, 110)">
      <rect width="185" height="68" rx="8" fill="url(#statCardBg)" stroke="#30363d" stroke-width="1"/>
      <text x="16" y="24" class="stat-label">TOTAL REPO FORKS</text>
      <text x="16" y="54" fill="#3b82f6" class="stat-val" filter="url(#numGlow)">{total_forks}</text>
      <text x="165" y="52" text-anchor="end" font-size="18">🍴</text>
    </g>

    <!-- Card 4: Followers -->
    <g transform="translate(195, 110)">
      <rect width="185" height="68" rx="8" fill="url(#statCardBg)" stroke="#30363d" stroke-width="1"/>
      <text x="16" y="24" class="stat-label">FOLLOWERS</text>
      <text x="16" y="54" fill="#a855f7" class="stat-val" filter="url(#numGlow)">{followers}</text>
      <text x="165" y="52" text-anchor="end" font-size="18">👥</text>
    </g>
  </g>

  <!-- Vertical Divider -->
  <line x1="430" y1="20" x2="430" y2="210" stroke="#30363d" stroke-width="1"/>

  <!-- Right Column: Top Languages Breakdown -->
  <g transform="translate(455, 20)">
    <text x="0" y="16" class="font-sans stat-title">🌐 Top Languages Distribution</text>

    <!-- Multi-Segment Distribution Bar -->
    <g transform="translate(0, 40)">
      <rect width="365" height="10" rx="3" fill="#161b22"/>
      {bars_markup}
    </g>

    <!-- Language Legends -->
    <g transform="translate(-40, -60)">
      {legend_markup}
    </g>
  </g>
</svg>
'''
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {output_path} successfully.")

if __name__ == "__main__":
    user = fetch_json(f"https://api.github.com/users/{USERNAME}")
    repos = fetch_json(f"https://api.github.com/users/{USERNAME}/repos?per_page=100")
    generate_svg(user, repos)

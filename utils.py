from typing import List, Optional
import re
import frontmatter
from datetime import datetime
import os
import html
from markdown import markdown
from markupsafe import Markup
import plantuml
import json
import emoji as emoji
from pymdownx import emoji as em
from functools import lru_cache
from data import Post


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(APP_ROOT, "content")
HUMOR_DIR = os.path.join(APP_ROOT, "static", "img", "humor")


def _discover_markdown_files() -> List[str]:
    return [
        os.path.join(CONTENT_DIR, f)
        for f in os.listdir(CONTENT_DIR)
        if f.endswith(".md") and not f.startswith("_")
        ]


def _parse_date(meta_date: str | datetime) -> datetime:
    if isinstance(meta_date, datetime):
        return meta_date
    # try a few common formats
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(str(meta_date), fmt)
        except ValueError:
            continue
    # fallback to now, but better to raise
    return datetime.fromtimestamp(0)


# --- custom formatter for Mermaid fences ---
def mermaid_format(source, language, class_name, options, md, **kwargs):
    # Escape just in case; the browser will render entities as text
    return f'<div class="mermaid">{html.escape(source)}</div>'


def render_markdown(md_text: str) -> str:
    html = markdown(
        md_text,
        extensions=[            
            "admonition",
            "sane_lists",
            "pymdownx.emoji",    # :emoji:
            "pymdownx.extra",    # extra features
            "pymdownx.mark",     # ==highlight==
            "pymdownx.tilde",    # ~~strikethrough~~
            "pymdownx.superfences",
            "pymdownx.highlight",
        ],
        extension_configs={
            "pymdownx.superfences": {
                "custom_fences": [
                    {
                        "name": "mermaid",      # ```mermaid
                        "class": "mermaid",     # -> <div class="mermaid">...</div>
                        "format": mermaid_format,  # keep raw text intact
                    }
                ]
            },
            "pymdownx.highlight": {
                "use_pygments": True,
                "noclasses": False,      # << inline color styles (no CSS file needed)
                "linenums": False,
                "guess_lang": False
            },
            "pymdownx.emoji": {
                "emoji_index": em.twemoji,   # shortcode lookup
                "emoji_generator": em.to_svg # emit <img src="...svg">
            },
        },
        output_format="html5",
    )
    return Markup(html)  # so Jinja won’t escape it


def load_post_from_file(path: str) -> Post:
    fm = frontmatter.load(path)
    slug = fm.get("slug") or os.path.splitext(os.path.basename(path))[0]
    title = fm.get("title") or slug.replace("-", " ").title()
    pre_icon = (':' + str(fm.get("pre_icon")) + ':') if fm.get("pre_icon") else ""
    post_icon = (':' + str(fm.get("post_icon")) + ':') if fm.get("post_icon") else ""
    create_date = _parse_date(fm.get("create_date") or datetime.fromtimestamp(os.path.getmtime(path)))
    update_date = _parse_date(fm.get("update_date") or create_date)
    summary = fm.get("summary") or fm.get("excerpt")
    cover_image = fm.get("cover_image") or fm.get("image")
    tags = render_markdown(render_tags(fm.get("tags") or []))
    category = fm.get("category") or None
    sub_category = fm.get("sub_category") or None
    html_content = render_with_plantuml(fm.content)
    html_content = render_with_D3(html_content)  # process D3 charts
    html = render_markdown(html_content)
    title = render_markdown(pre_icon + title + post_icon)  # to pre-load emoji etc.
    graphml_included = fm.get("graphml_included") or False
    graphml_file = fm.get("graphml_file") or None
    chart_included = fm.get("chart_included") or False
        

    return Post(
        slug=slug,
        title=title,
        create_date=create_date,
        update_date=update_date,
        summary=summary,
        cover_image=cover_image,
        tags=tags,
        category=category,
        sub_category=sub_category,
        html=html,
        raw_markdown=fm.content,          
        graphml_included=graphml_included,
        graphml_file=graphml_file,
        chart_included=chart_included,        
)


def get_post(slug: str) -> Optional[Post]:
    for p in load_all_posts():
        if p.slug == slug:
            return p
    return None


def render_tags(tags: List[str]) -> str:
    if not tags:
        return ""
    tag_links = [f'[#{ tag}](https://www.linkedin.com/feed/hashtag/{ tag }/)' for tag in tags]
    return " ".join(tag_links)


def render_with_plantuml(markdown_text):
    # Find PlantUML code blocks in the Markdown
    def repl(match):
        uml_code = match.group(1)
        try:
            diagram_url = plantuml.get_url(uml_code)
            return f'<img src="{diagram_url}" alt="PlantUML diagram">'
        except Exception as e:
            # Escape the UML code to show it safely in HTML
            escaped_code = html.escape(uml_code)
            return f"<pre>{escaped_code}</pre><p><em>Failed to generate diagram: {e}</em></p>"
    
    # Step 1: Replace PlantUML blocks
    processed = re.sub(r'```plantuml(.*?)```', repl, markdown_text, flags=re.DOTALL)

    # Step 2: Convert the rest of the Markdown to HTML   
    return processed


def render_with_D3(md_text):

    charts = []

    def replacer(match):
        chart_type = match.group(1).strip()
        raw_json = match.group(2).strip()
        try:
            parsed_data = json.loads(raw_json)
        except json.JSONDecodeError:
            return match.group(0)  # leave block unchanged if bad JSON

        charts.append({"type": chart_type, "data": parsed_data})
        # replace JSON block with an SVG placeholder
        return f"<svg class='chart' width='500' height='300' data-type='{chart_type}' data-json='{json.dumps(parsed_data)}'></svg>"

    # Replace all ```json type ...``` blocks with SVGs
    clean_code = re.sub(r"```json\s+(\w+)\s*\n([\s\S]*?)\n```", replacer, md_text, flags=re.DOTALL)

    return clean_code


@lru_cache(maxsize=1)
def load_all_posts() -> List[Post]:
    posts = [load_post_from_file(p) for p in _discover_markdown_files()]
    posts.sort(key=lambda p: p.create_date, reverse=True)
    return posts


@lru_cache(maxsize=1)
def load_all_humor() -> List[str]:    
    images = [
        f"img/humor/{filename}"
        for filename in os.listdir(HUMOR_DIR)
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif"))
    ]
    images.sort()  # Optional: sort alphabetically
    return images
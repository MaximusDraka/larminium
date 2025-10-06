from attr import dataclass
import datetime

@dataclass
class Post:
    slug: str
    title: str
    create_date: datetime
    update_date: datetime
    summary: str | None
    cover_image: str | None
    tags: list[str]
    category: str | None
    sub_category: str | None
    html: str # rendered HTML content
    raw_markdown: str # original markdown (optional if you need it)
    graphml_included: bool # whether a GraphML file is included
    graphml_file: str | None # the name of the GraphML file if included
    chart_included: bool # whether a chart is included
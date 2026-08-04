from jinja2 import Environment,FileSystemLoader,select_autoescape
from datetime import datetime
from pathlib import Path

TEMPLATES_DIR =Path(__file__).parent.parent / "templates" / "emails"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
)

def render_email(template_name:str,**context) ->str:
    template = _env.get_template(template_name)
    return template.render(current_year=datetime.now().year, **context)

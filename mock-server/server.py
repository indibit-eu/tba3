"""Wrapper entry point that serves the original OpenAPI spec with examples."""

from pathlib import Path

import yaml

from api.main import app

_spec_path = Path(__file__).parent / "tba3-spec.yml"
with open(_spec_path) as f:
    app.openapi_schema = yaml.safe_load(f)

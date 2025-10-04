"""Top-level package for the NekoBot framework.

This module exposes helper utilities such as ``get_version`` while
falling back to the project metadata when the package has not been
installed into the environment yet.  Historically the package shipped
with an empty ``__init__`` which meant that ``from nekobot import
__version__`` failed with an ``AttributeError``.  Some tooling expects
this attribute to exist (for example, ``python -m nekobot --version`` in
CLI entrypoints), so we expose a robust implementation here.
"""

from __future__ import annotations

from importlib import metadata as importlib_metadata
from pathlib import Path
import re

__all__ = ["__version__", "get_version"]


def _read_version_from_pyproject() -> str:
    """Return the project version as declared in ``pyproject.toml``.

    When the project is executed from a source checkout the distribution
    metadata might not be installed yet.  In that case we fall back to
    parsing the local ``pyproject.toml`` file.  If the version cannot be
    determined we default to ``"0.0.0"`` which makes the behaviour
    explicit and predictable for callers instead of raising an obscure
    exception.
    """

    project_root = Path(__file__).resolve().parent.parent
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.is_file():
        return "0.0.0"

    match = re.search(
        r"^version\s*=\s*['\"]([^'\"]+)['\"]",
        pyproject_path.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    if match:
        return match.group(1)
    return "0.0.0"


try:
    __version__ = importlib_metadata.version("NekoBot")
except importlib_metadata.PackageNotFoundError:
    __version__ = _read_version_from_pyproject()


def get_version() -> str:
    """Public helper returning the framework version string."""

    return __version__


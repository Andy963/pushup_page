"""
Compatibility shim for the vendored `GpxTrackPoster` code.

The project keeps the upstream sources under `pushup_page/gpxtrackposter/` and
does not modify them. Some upstream modules use absolute imports like
`from gpxtrackposter import utils`, which requires a top-level `gpxtrackposter`
package to exist.

This shim makes `import gpxtrackposter` resolve to the vendored implementation.
"""

from __future__ import annotations

from pathlib import Path

_IMPL_DIR = Path(__file__).resolve().parent.parent / "pushup_page" / "gpxtrackposter"

if _IMPL_DIR.is_dir():
    __path__.append(str(_IMPL_DIR))  # type: ignore[name-defined]

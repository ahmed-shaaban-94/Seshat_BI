"""PBIR visual geometry writer (adapter increment D).

Sets an existing, binding-mapped visual's ``position`` rectangle -- ``x``, ``y``,
``width``, ``height``, ``z``, ``tabOrder`` -- the layout a human drags/resizes in
the Power BI canvas. Authorized by ADR 0016 (ratified).

THE FR-003 GUARANTEE (unchanged): the writer NEVER touches the visual's data
binding. It asserts ``visual.query`` and ``visual.visualType`` are byte-identical
before and after, and refuses to write if either would change. Geometry is added
BESIDE the binding guard, never through it. It NEVER changes visualType, creates or
deletes a visual, or moves an unbound visual (ADR 0016 exclusions).

THE ON-CANVAS GUARD: the result rectangle must fit the page's REAL canvas, read from
the sibling ``page.json`` (top-level ``width``/``height``) -- never a hardcoded size.
Off-canvas / negative / non-numeric rectangles are refused (objective validity);
overlap between visuals is ALLOWED (a design judgment the lint must not make).

NO FORCE PARAMETER: moving a visual necessarily changes its always-present position
keys -- that IS the operation. A force gate modeled on increment B's "differs ->
refuse" formatting gate was tried and removed here: it blocked every real move.
Repeated moves simply succeed; the reviewable git diff + human ratification is the
overwrite safety net, not a per-call flag.

Companion authoring adapter (ADR 0015/0016): committed PBIR JSON, deterministic,
validated, all-or-nothing. No pbi-cli, no live Power BI, no network -- stdlib only.
Grants no readiness pass, emits no score.
"""

from __future__ import annotations

import json
from pathlib import Path

# The only position keys this increment may write (ADR 0016). Anything else refused.
_ALLOWED_KEYS = frozenset({"x", "y", "width", "height", "z", "tabOrder"})


class PbirGeometryError(Exception):
    """A geometry input/output problem surfaced cleanly (never a traceback)."""


def _dump(doc: object) -> str:
    return json.dumps(doc, indent=2, sort_keys=True) + "\n"


def _load_json(p: Path, what: str) -> dict:
    try:
        with p.open(encoding="utf-8-sig") as fh:
            doc = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise PbirGeometryError(
            f"{what} is not valid JSON ({exc.__class__.__name__}): {p}"
        ) from exc
    if not isinstance(doc, dict):
        raise PbirGeometryError(f"{what} is not a JSON object: {p}")
    return doc


def _canvas_dims(visual_json: Path) -> tuple[float, float]:
    """Read the REAL canvas width/height from the sibling page.json.

    Path: .../pages/<page>/visuals/<v>/visual.json -> .../pages/<page>/page.json,
    i.e. visual_json.parents[2] / 'page.json'. NEVER hardcode a fallback size.
    """
    page_json = visual_json.parents[2] / "page.json"
    if not page_json.is_file():
        raise PbirGeometryError(
            f"page.json not found next to the visual ({page_json}); cannot validate "
            f"on-canvas without the real canvas dimensions"
        )
    page = _load_json(page_json, "page.json")
    w, h = page.get("width"), page.get("height")
    if (
        isinstance(w, bool)
        or isinstance(h, bool)
        or not isinstance(w, (int, float))
        or not isinstance(h, (int, float))
    ):
        raise PbirGeometryError(
            f"page.json has no numeric width/height ({page_json}); cannot validate "
            f"on-canvas"
        )
    return float(w), float(h)


def set_geometry(visual_json: Path, position: dict) -> Path:
    """Set the allow-listed ``position`` keys on the visual, on-canvas + binding-safe.

    ``position`` maps a subset of ``{x, y, width, height, z, tabOrder}`` to numeric
    values. Existing position keys not named in ``position`` are preserved. Raises
    PbirGeometryError on a bad path, an out-of-allow-list key, a non-numeric value,
    or a result rectangle that would fall off the page's real canvas. Returns the
    written path.
    """
    visual_json = Path(visual_json)
    if not visual_json.is_file():
        raise PbirGeometryError(f"visual.json not found: {visual_json}")
    # Guard: the file must live under a *.Report/ tree (never write elsewhere).
    if ".Report" not in str(visual_json.resolve()):
        raise PbirGeometryError("target is not inside a *.Report/ tree")

    doc = _load_json(visual_json, "visual.json")
    if not isinstance(doc.get("visual"), dict):
        raise PbirGeometryError("visual.json has no 'visual' object")
    if not isinstance(doc.get("position"), dict):
        raise PbirGeometryError("visual.json has no 'position' object")

    # Validate the requested keys + numeric values up front.
    if not isinstance(position, dict) or not position:
        raise PbirGeometryError("position must be a non-empty object")
    for key, val in position.items():
        if key not in _ALLOWED_KEYS:
            raise PbirGeometryError(
                f"position key {key!r} is not in the geometry allow-list "
                f"(allowed: {sorted(_ALLOWED_KEYS)})"
            )
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            raise PbirGeometryError(
                f"position.{key} must be a number, got {type(val).__name__}: {val!r}"
            )

    # Snapshot the data binding BEFORE editing -- the FR-003 oracle.
    binding_before = _dump(
        {
            "query": doc["visual"].get("query"),
            "visualType": doc["visual"].get("visualType"),
        }
    )

    # Compute the RESULT rectangle (existing merged with requested) and validate
    # on-canvas against the REAL canvas dims (never a hardcoded default).
    result = {**doc["position"], **position}
    canvas_w, canvas_h = _canvas_dims(visual_json)
    rx, ry = result.get("x", 0), result.get("y", 0)
    rw, rh = result.get("width", 0), result.get("height", 0)
    for label, v in (("x", rx), ("y", ry), ("width", rw), ("height", rh)):
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise PbirGeometryError(f"result {label} is not numeric: {v!r}")
    if rx < 0 or ry < 0 or rx + rw > canvas_w or ry + rh > canvas_h:
        raise PbirGeometryError(
            f"result rectangle x={rx} y={ry} w={rw} h={rh} is off-canvas "
            f"(canvas {canvas_w}x{canvas_h}); refusing to write"
        )

    # No overwrite gate: moving a visual necessarily changes always-present position
    # keys, so a "differs -> refuse" gate would block every real move. Overwrite
    # safety is the reviewable git diff + human ratification, not a per-call flag.
    doc["position"] = result

    # THE FR-003 GUARANTEE: the data binding must be byte-identical after the edit.
    binding_after = _dump(
        {
            "query": doc["visual"].get("query"),
            "visualType": doc["visual"].get("visualType"),
        }
    )
    if binding_after != binding_before:
        raise PbirGeometryError(
            "refusing to write: the edit would alter the visual's data binding "
            "(query/visualType) -- this adapter lays out only, never binds (FR-003)"
        )

    text = _dump(doc)
    if _dump(json.loads(text)) != text:
        raise PbirGeometryError("staged visual.json is not round-trip stable")
    visual_json.write_text(text, encoding="utf-8", newline="\n")
    return visual_json

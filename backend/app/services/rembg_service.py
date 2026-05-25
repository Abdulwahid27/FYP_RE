import io
from pathlib import Path

import httpx
from PIL import Image
from rembg import remove


async def _fetch_bytes(url: str) -> bytes:
    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        return resp.content


async def extract_garment(source: str | Path, out_path: Path) -> Path:
    """Remove background and save as transparent PNG. `source` can be a URL or local path."""
    if isinstance(source, Path) or (isinstance(source, str) and not source.startswith("http")):
        data = Path(source).read_bytes()
    else:
        data = await _fetch_bytes(source)

    input_image = Image.open(io.BytesIO(data)).convert("RGBA")
    output_image = remove(input_image)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path = out_path.with_suffix(".png")
    output_image.save(out_path, format="PNG")
    return out_path


async def extract_garment_bytes(source: str | Path) -> bytes:
    """Remove background and return PNG bytes. `source` can be a URL or local path."""
    if isinstance(source, Path) or (isinstance(source, str) and not source.startswith("http")):
        data = Path(source).read_bytes()
    else:
        data = await _fetch_bytes(source)

    input_image = Image.open(io.BytesIO(data)).convert("RGBA")
    output_image = remove(input_image)
    buf = io.BytesIO()
    output_image.save(buf, format="PNG")
    return buf.getvalue()

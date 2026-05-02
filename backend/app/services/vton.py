import asyncio
import shutil
from pathlib import Path

from gradio_client import Client, handle_file

from ..config import settings


def _run_vton_sync(person_path: str, garment_path: str, garment_desc: str) -> str:
    """Call the IDM-VTON Gradio Space and return the local file path of the result."""
    client = Client(settings.VTON_SPACE, hf_token=settings.HF_TOKEN or None)

    result = client.predict(
        dict(background=handle_file(person_path), layers=[], composite=None),
        handle_file(garment_path),
        garment_desc or "garment",
        True,
        True,
        30,
        42,
        api_name="/tryon",
    )

    if isinstance(result, (list, tuple)):
        candidate = result[0]
    else:
        candidate = result

    if isinstance(candidate, dict):
        candidate = candidate.get("path") or candidate.get("name") or candidate.get("url")

    if not candidate:
        raise RuntimeError("Virtual try-on returned no result")

    return str(candidate)


async def run_virtual_tryon(
    person_image: Path,
    garment_image: Path,
    out_path: Path,
    garment_desc: str = "garment",
) -> Path:
    loop = asyncio.get_event_loop()
    src = await loop.run_in_executor(
        None, _run_vton_sync, str(person_image), str(garment_image), garment_desc
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    src_path = Path(src)
    suffix = src_path.suffix or ".png"
    out_path = out_path.with_suffix(suffix)
    shutil.copyfile(src_path, out_path)
    return out_path

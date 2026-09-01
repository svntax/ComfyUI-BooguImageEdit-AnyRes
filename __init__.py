from .boogu_edit_anyres import BooguEditAnyResExtension
from comfy_api.latest import ComfyExtension

async def comfy_entrypoint() -> ComfyExtension:
    return BooguEditAnyResExtension()

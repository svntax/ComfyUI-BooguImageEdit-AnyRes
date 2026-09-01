import math

import node_helpers
import comfy.utils
from typing_extensions import override
from comfy_api.latest import ComfyExtension, io


class TextEncodeBooguEditAnyRes(io.ComfyNode):
    """Boogu-Image Edit conditioning with resolution matching.

    This custom node fixes the shifting/scaling issue in the official
    node when generating at non-1024x1024 resolutions. Connect the same
    `EmptyLatentImage` used for your generation into the `latent` input. 
    The node will scale the reference image to match the noise canvas
    dimensions before VAE encoding.
    """

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="TextEncodeBooguEditAnyRes",
            category="model/conditioning/boogu",
            inputs=[
                io.Clip.Input("clip"),
                io.String.Input("prompt", multiline=True, dynamic_prompts=True),
                io.String.Input("negative_prompt", multiline=True, dynamic_prompts=True, advanced=True),
                io.Vae.Input("vae"),
                io.Latent.Input(
                    "latent", 
                    optional=True, 
                    tooltip="Connect the EmptyLatentImage used for generation. This ensures the reference latent matches the noise canvas exactly."
                ),
                io.Autogrow.Input(
                    "images",
                    template=io.Autogrow.TemplateNames(
                        io.Image.Input("image"),
                        names=[f"image_{i}" for i in range(1, 17)],
                        min=0,
                    ),
                    tooltip="Reference image(s) to edit. Boogu currently supports one reference only, but you can still add more.",
                ),
            ],
            outputs=[
                io.Conditioning.Output(display_name="positive"),
                io.Conditioning.Output(display_name="negative"),
            ],
        )

    @classmethod
    def execute(cls, clip, prompt, negative_prompt, vae=None, latent=None, images: io.Autogrow.Type = None) -> io.NodeOutput:
        ref_latents = []
        images_vl = []

        images = images or {}
        for name in sorted(images, key=lambda n: int(n.rsplit("_", 1)[-1])):
            image = images[name]
            if image is None:
                continue
            samples = image.movedim(-1, 1)

            # Vision tower input: the reference caps the VLM image at 384x384
            # (max_vlm_input_pil_pixels in pipeline_boogu.py).
            total = int(384 * 384)
            scale_by = math.sqrt(total / (samples.shape[3] * samples.shape[2]))
            width = round(samples.shape[3] * scale_by)
            height = round(samples.shape[2] * scale_by)
            s = comfy.utils.common_upscale(samples, width, height, "area", "disabled")
            images_vl.append(s.movedim(1, -1)[:, :, :, :3])

            # Reference latent: align to generation resolution.
            if vae is not None:
                if latent is not None and "samples" in latent:
                    # Scale reference image exactly to the noise canvas dimensions.
                    # latent shape is [B, C, H/8, W/8], so multiply by 8 to get target pixels.
                    target_h = latent["samples"].shape[2] * 8
                    target_w = latent["samples"].shape[3] * 8
                    width = target_w
                    height = target_h
                else:
                    # Fallback to original 1024x1024 cap behavior if no latent is provided
                    total = int(1024 * 1024)
                    scale_by = math.sqrt(total / (samples.shape[3] * samples.shape[2]))
                    width = round(samples.shape[3] * scale_by / 16.0) * 16
                    height = round(samples.shape[2] * scale_by / 16.0) * 16

                s = comfy.utils.common_upscale(samples, width, height, "area", "disabled")
                ref_latents.append(vae.encode(s.movedim(1, -1)[:, :, :, :3]))

        # positive: instruction + vision tokens; negative: empty (no vision). Ref latent on both.
        positive = clip.encode_from_tokens_scheduled(clip.tokenize(prompt, images=images_vl))
        negative = clip.encode_from_tokens_scheduled(clip.tokenize(negative_prompt))

        if len(ref_latents) > 0:
            positive = node_helpers.conditioning_set_values(positive, {"reference_latents": ref_latents}, append=True)
            negative = node_helpers.conditioning_set_values(negative, {"reference_latents": ref_latents}, append=True)

        return io.NodeOutput(positive, negative)


class BooguEditAnyResExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
            TextEncodeBooguEditAnyRes,
        ]

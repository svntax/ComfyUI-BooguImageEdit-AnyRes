# ComfyUI-BooguImageEdit-AnyRes
Custom node to fix resolution issues for Boogu Image Edit in ComfyUI.

Best used with `boogu_image_edit_turbo_hotfix_1k_20260708_int8_convrot.safetensors`. Get the model from [here](https://huggingface.co/Comfy-Org/Boogu-Image)

## How to use

<img width="1296" height="801" alt="workflow" src="https://github.com/user-attachments/assets/855deffe-f35c-4b79-9018-3be4c999ada6" />

Edit the default ComfyUI workflow, replace `TextEncodeBooguEdit` with this custom node (`TextEncodeBooguEditAnyRes`). It has a new parameter for a latent image, which should roughly match the size of the reference image.

## Comparisons

| Prompt | Size | Reference, `TextEncodeBooguEdit`, `TextEncodeBooguEditAnyRes` |
| --- | --- | --- |
| `Change the sky to a dusty red color. Add a small ufo on the top right.` | 512x1024 | <img width="768" height="512" alt="edit_astronaut_test_small" src="https://github.com/user-attachments/assets/17d4a826-f3ce-4dec-8894-1a2de176d1e0" /> |
| `Remove the helicopter` | 512x512 | <img width="1536" height="512" alt="island_helicopter_test" src="https://github.com/user-attachments/assets/7ca20215-cb36-4194-9d12-2151f6b595f0" /> |

## Credits

This is just an edit of the default Boogu Image text encoding node (`comfy_extras/nodes_boogu.py`), so all credits to the original source code authors.

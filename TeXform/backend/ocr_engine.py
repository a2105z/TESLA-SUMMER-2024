import os
from typing import Optional

import torch
from PIL import Image

from backend.config_loader import get

# ─── TrOCR model & processor (loaded lazily) ─────────────────────────────────────

_processor = None
_model = None
_device = None


def _ensure_model_loaded():
    """Lazy load the TrOCR model and processor only when needed."""
    global _processor, _model, _device
    
    if _processor is not None and _model is not None:
        return
    
    # Force PyTorch-only so we avoid TensorFlow/ml_dtypes "handle" conversion errors
    os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
    try:
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    except ImportError as e:
        raise RuntimeError(
            f"Failed to import transformers: {e}. "
            "Please ensure transformers is installed: pip install transformers"
        ) from e
    
    _model_name = get("ocr_engine.model_name", "microsoft/trocr-base-handwritten")
    _processor = TrOCRProcessor.from_pretrained(_model_name)
    _model = VisionEncoderDecoderModel.from_pretrained(_model_name)
    
    _device_str = (get("ocr_engine.device") or "").strip().lower()
    if _device_str == "cpu":
        _device = torch.device("cpu")
    elif _device_str == "cuda" and torch.cuda.is_available():
        _device = torch.device("cuda")
    else:
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _model.to(_device)


def ocr_text_from_page(
    image_path: str,
    max_length: Optional[int] = None,
    num_beams: Optional[int] = None,
) -> str:
    """Perform OCR on a single page image using TrOCR (handwritten)."""
    _ensure_model_loaded()
    
    if max_length is None:
        max_length = get("ocr_engine.max_length", 512)
    if num_beams is None:
        num_beams = get("ocr_engine.num_beams", 4)
    max_length = max(1, min(int(max_length), 1024))
    num_beams = max(1, min(int(num_beams), 16))

    image = Image.open(image_path).convert("RGB")
    pixel_values = _processor(images=image, return_tensors="pt").pixel_values.to(_device)
    generated_ids = _model.generate(
        pixel_values,
        max_length=max_length,
        num_beams=num_beams,
        early_stopping=True,
    )
    text = _processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return text.strip()

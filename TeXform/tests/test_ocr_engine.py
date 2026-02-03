import pytest
from PIL import Image
import torch
import os

import backend.ocr_engine as ocr_engine


def test_ocr_text_from_page(monkeypatch, tmp_path):
    # Create a dummy white image
    img_path = tmp_path / "test.png"
    Image.new("RGB", (10, 10), (255, 255, 255)).save(str(img_path))

    # Prepare a dummy tensor and stubs for processor & model
    dummy_tensor = torch.zeros((1, 3, 10, 10), dtype=torch.float)

    class DummyProcessor:
        def __call__(self, images, return_tensors):
            return type("obj", (), {"pixel_values": dummy_tensor})

        def batch_decode(self, generated_ids, skip_special_tokens):
            return ["decoded text"]

    class DummyModel:
        def generate(self, pixel_values, max_length, num_beams, early_stopping):
            # Ensure the tensor passed is our dummy tensor (possibly moved to CPU)
            assert torch.equal(pixel_values.cpu(), dummy_tensor)
            return [[1, 2, 3]]

    # Monkeypatch the lazy-loaded processor, model, and device
    monkeypatch.setattr(ocr_engine, "_processor", DummyProcessor())
    monkeypatch.setattr(ocr_engine, "_model", DummyModel())
    monkeypatch.setattr(ocr_engine, "_device", torch.device("cpu"))

    # Call the function under test
    result = ocr_engine.ocr_text_from_page(str(img_path))

    assert result == "decoded text"

import os

import pytest

from app.datasets.huggingface_samples import load_ami_audio_samples


@pytest.mark.integration
def test_can_load_one_ami_sample_from_hugging_face():
    if os.getenv("RUN_HF_TESTS") != "1":
        pytest.skip("Set RUN_HF_TESTS=1 to download a real AMI sample from HF")

    samples = load_ami_audio_samples(limit=1)

    assert len(samples) == 1
    assert samples[0].text
    assert samples[0].audio is not None

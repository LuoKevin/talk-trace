from app.datasets import huggingface_samples


def test_load_ami_audio_samples_uses_expected_hf_repo(monkeypatch):
    captured_args = {}

    def fake_load_dataset(repo, config, split, streaming):
        captured_args.update(
            {
                "repo": repo,
                "config": config,
                "split": split,
                "streaming": streaming,
            }
        )
        return iter(
            [
                {
                    "text": "We should ship the upload flow first.",
                    "speaker_id": "A",
                    "begin_time": 1.5,
                    "end_time": 4.0,
                    "audio": {"array": [0.0, 0.1], "sampling_rate": 16000},
                },
                {
                    "text": "Then we can add diarization.",
                    "speaker_id": "B",
                    "begin_time": 4.1,
                    "end_time": 6.2,
                    "audio": {"array": [0.2, 0.3], "sampling_rate": 16000},
                },
            ]
        )

    monkeypatch.setattr(huggingface_samples, "_load_dataset", fake_load_dataset)

    samples = huggingface_samples.load_ami_audio_samples(limit=1)

    assert captured_args == {
        "repo": "edinburghcstr/ami",
        "config": "ihm",
        "split": "train",
        "streaming": True,
    }
    assert len(samples) == 1
    assert samples[0].text == "We should ship the upload flow first."
    assert samples[0].speaker_id == "A"
    assert samples[0].start_seconds == 1.5
    assert samples[0].end_seconds == 4.0


def test_normalize_ami_row_accepts_alternate_field_names():
    sample = huggingface_samples._normalize_ami_row(
        {
            "transcript": "Alternate schemas should still be readable.",
            "speaker": 2,
            "start": "10.0",
            "end": "12.5",
            "audio": "audio-placeholder",
        }
    )

    assert sample.text == "Alternate schemas should still be readable."
    assert sample.speaker_id == "2"
    assert sample.start_seconds == 10.0
    assert sample.end_seconds == 12.5
    assert sample.audio == "audio-placeholder"

from app.services.alignment_service import align_transcript_to_speakers
from app.models.transcription import RawTranscript, RawTranscriptSegment
from app.models.diarization import Diarization, SpeakerTurn


def test_align_transcript_to_speakers_chooses_largest_overlap():
    transcript = RawTranscript(
        segments=[
            RawTranscriptSegment(start_seconds=0.0, end_seconds=5.0, text="First point"),
            RawTranscriptSegment(start_seconds=5.0, end_seconds=9.0, text="Second point"),
        ]
    )
    speaker_turns = [
        SpeakerTurn(speaker="Speaker 1", start_seconds=0.0, end_seconds=4.0),
        SpeakerTurn(speaker="Speaker 2", start_seconds=4.0, end_seconds=9.0),
    ]

    diarization = Diarization(speaker_turns=speaker_turns)

    aligned = align_transcript_to_speakers(transcript, diarization)

    assert [segment.speaker for segment in aligned.segments] == [
        "Speaker 1",
        "Speaker 2",
    ]
    assert [segment.text for segment in aligned.segments] == [
        "First point",
        "Second point",
    ]
    assert aligned.segments[0].overlap_seconds == 4.0
    assert aligned.segments[0].overlap_ratio == 0.8
    assert aligned.segments[1].overlap_seconds == 4.0
    assert aligned.segments[1].overlap_ratio == 1.0


def test_align_transcript_to_speakers_marks_unknown_when_no_turns_exist():
    transcript = RawTranscript(
        segments=[
            RawTranscriptSegment(
                start_seconds=0.0,
                end_seconds=2.0,
                text="No speaker data",
            )
        ]
    )

    aligned = align_transcript_to_speakers(
        transcript,
        diarization=Diarization(speaker_turns=[]),
    )

    assert aligned.segments[0].speaker == "Unknown Speaker"
    assert aligned.segments[0].overlap_seconds == 0.0
    assert aligned.segments[0].overlap_ratio == 0.0


def test_align_transcript_to_speakers_marks_unknown_when_turns_do_not_overlap():
    transcript = RawTranscript(
        segments=[
            RawTranscriptSegment(
                start_seconds=20.0,
                end_seconds=25.0,
                text="This happens after the speaker turn.",
            )
        ]
    )
    diarization = Diarization(
        speaker_turns=[
            SpeakerTurn(speaker="Speaker 1", start_seconds=0.0, end_seconds=5.0),
        ]
    )

    aligned = align_transcript_to_speakers(transcript, diarization)

    assert aligned.segments[0].speaker == "Unknown Speaker"
    assert aligned.segments[0].overlap_seconds == 0.0
    assert aligned.segments[0].overlap_ratio == 0.0


def test_align_transcript_to_speakers_marks_unknown_when_overlap_is_too_small():
    transcript = RawTranscript(
        segments=[
            RawTranscriptSegment(
                start_seconds=0.0,
                end_seconds=10.0,
                text="A long segment with a tiny speaker overlap.",
            )
        ]
    )
    diarization = Diarization(
        speaker_turns=[
            SpeakerTurn(speaker="Speaker 1", start_seconds=9.0, end_seconds=10.0),
        ]
    )

    aligned = align_transcript_to_speakers(transcript, diarization)

    assert aligned.segments[0].speaker == "Unknown Speaker"
    assert aligned.segments[0].overlap_seconds == 1.0
    assert aligned.segments[0].overlap_ratio == 0.1


def test_align_transcript_to_speakers_marks_unknown_at_exact_boundary_touch():
    transcript = RawTranscript(
        segments=[
            RawTranscriptSegment(
                start_seconds=5.0,
                end_seconds=10.0,
                text="This starts exactly after the prior speaker turn.",
            )
        ]
    )
    diarization = Diarization(
        speaker_turns=[
            SpeakerTurn(speaker="Speaker 1", start_seconds=0.0, end_seconds=5.0),
        ]
    )

    aligned = align_transcript_to_speakers(transcript, diarization)

    assert aligned.segments[0].speaker == "Unknown Speaker"
    assert aligned.segments[0].overlap_seconds == 0.0
    assert aligned.segments[0].overlap_ratio == 0.0


def test_align_transcript_to_speakers_returns_empty_alignment_for_empty_transcript():
    aligned = align_transcript_to_speakers(
        RawTranscript(segments=[]),
        Diarization(
            speaker_turns=[
                SpeakerTurn(speaker="Speaker 1", start_seconds=0.0, end_seconds=5.0),
            ]
        ),
    )

    assert aligned.segments == []

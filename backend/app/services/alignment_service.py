from app.models.diarization import Diarization
from app.models.alignment import AlignedTranscript, AlignedTranscriptSegment
from app.models.transcription import RawTranscript


MIN_SPEAKER_OVERLAP_RATIO = 0.20
UNKNOWN_SPEAKER = "Unknown Speaker"


def align_transcript_to_speakers(
    transcript: RawTranscript,
    diarization: Diarization,
) -> AlignedTranscript:
    """Attach speaker labels to transcript segments.

    This MVP implementation assigns each transcript segment to the speaker turn
    with the largest timestamp overlap. It does not split text across speakers
    yet because that requires word-level timestamps.
    """
    # TODO: Handle partial overlaps by splitting transcript segments.
    # TODO: Add word-level alignment once transcription returns word timestamps.
    aligned_segments: list[AlignedTranscriptSegment] = []

    for segment in transcript.segments:
        speaker, overlap_seconds, overlap_ratio = _speaker_with_largest_overlap(
            segment_start=segment.start_seconds,
            segment_end=segment.end_seconds,
            diarization=diarization,
        )
        aligned_segments.append(
            AlignedTranscriptSegment(
                speaker=speaker,
                start_seconds=segment.start_seconds,
                end_seconds=segment.end_seconds,
                text=segment.text,
                overlap_seconds=overlap_seconds,
                overlap_ratio=overlap_ratio,
            )
        )

    return AlignedTranscript(segments=aligned_segments)


def _speaker_with_largest_overlap(
    segment_start: float,
    segment_end: float,
    diarization: Diarization,
) -> tuple[str, float, float]:
    segment_duration = max(0.0, segment_end - segment_start)
    if segment_duration == 0.0:
        return UNKNOWN_SPEAKER, 0.0, 0.0

    best_speaker = UNKNOWN_SPEAKER
    best_overlap = 0.0

    for turn in diarization.speaker_turns:
        overlap = _overlap_seconds(
            segment_start,
            segment_end,
            turn.start_seconds,
            turn.end_seconds,
        )
        if overlap > best_overlap:
            best_overlap = overlap
            best_speaker = turn.speaker

    overlap_ratio = best_overlap / segment_duration
    if overlap_ratio < MIN_SPEAKER_OVERLAP_RATIO:
        best_speaker = UNKNOWN_SPEAKER

    return best_speaker, best_overlap, overlap_ratio


def _overlap_seconds(
    start_a: float,
    end_a: float,
    start_b: float,
    end_b: float,
) -> float:
    return max(0.0, min(end_a, end_b) - max(start_a, start_b))

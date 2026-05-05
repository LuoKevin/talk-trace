from app.schemas import TranscriptSegment
from app.services.diarization_service import SpeakerTurn
from app.services.transcription_service import RawTranscriptSegment


def align_transcript_to_speakers(
    transcript: list[RawTranscriptSegment],
    speaker_turns: list[SpeakerTurn],
) -> list[TranscriptSegment]:
    """Attach speaker labels to transcript segments.

    This fake implementation assigns each transcript segment to the speaker
    turn with the largest timestamp overlap.
    """
    # TODO: Handle partial overlaps by splitting transcript segments.
    # TODO: Add tests for edge cases: gaps, overlaps, and missing diarization.
    aligned_segments: list[TranscriptSegment] = []

    for segment in transcript:
        best_turn = max(
            speaker_turns,
            key=lambda turn: _overlap_seconds(
                segment.start_seconds,
                segment.end_seconds,
                turn.start_seconds,
                turn.end_seconds,
            ),
            default=None,
        )
        speaker = best_turn.speaker if best_turn else "Unknown Speaker"
        aligned_segments.append(
            TranscriptSegment(
                speaker=speaker,
                start_seconds=segment.start_seconds,
                end_seconds=segment.end_seconds,
                text=segment.text,
            )
        )

    return aligned_segments


def _overlap_seconds(
    start_a: float,
    end_a: float,
    start_b: float,
    end_b: float,
) -> float:
    return max(0.0, min(end_a, end_b) - max(start_a, start_b))

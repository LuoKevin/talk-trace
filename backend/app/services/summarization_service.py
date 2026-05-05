from app.schemas import MeetingSummary, TranscriptSegment


def summarize_meeting(transcript: list[TranscriptSegment]) -> MeetingSummary:
    """Generate a structured meeting summary.

    In the real implementation, this service should call an OpenAI-compatible
    API and validate the response against `MeetingSummary`.
    """
    # TODO: Design a prompt that asks for JSON matching the MeetingSummary schema.
    # TODO: Add retry and validation behavior for malformed model responses.
    # TODO: Decide whether summaries should include citations to transcript segments.
    return MeetingSummary(
        overview=(
            "The team reviewed the launch plan, clarified MVP scope, and "
            "identified copy as a dependency for the onboarding flow."
        ),
        action_items=[
            "Finish the onboarding flow.",
            "Provide final onboarding copy by Friday.",
        ],
        decisions=[
            "Keep the MVP focused on uploads, processing status, and summaries.",
        ],
        unanswered_questions=[
            "Who is responsible for delivering the final onboarding copy?",
        ],
    )

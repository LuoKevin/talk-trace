from app.models.summarization import Summarization
from app.adapters.summarization.base import BaseSummarizationAdapter
from app.models.alignment import AlignedTranscript


class StubSummarizationAdapter(BaseSummarizationAdapter):
    def summarize(self, transcript: AlignedTranscript) -> Summarization:
        # This is a stub implementation that returns a fixed summary for testing purposes
        return Summarization(
            main_speaker="Speaker 1",
            overview="This is a summary of the conversation.",
            action_items=["Follow up on project X", "Schedule meeting with Y"],
            follow_up_topics=["Project X progress", "Team dynamics"],
            supporter_suggestions={
                "Speaker 1": [
                    "Consider taking breaks during work",
                    "Focus on one task at a time",
                ],
                "Speaker 2": [
                    "Encourage Speaker 1 to share more",
                    "Offer help with project X",
                ],
            },
        )

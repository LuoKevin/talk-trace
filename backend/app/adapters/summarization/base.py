
from app.models.alignment import AlignedTranscript
from app.models.summarization import Summarization


class BaseSummarizationAdapter:
    def summarize(self, transcript: AlignedTranscript) -> Summarization:
        raise NotImplementedError("Summarization adapter must implement summarize method")
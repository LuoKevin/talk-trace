

from pydantic import BaseModel


class Summarization(BaseModel):
    main_speaker: str # The speaker who spoke the most in the clip
    overview: str # A high-level summary of the conversation
    action_items: list[str] # A list of action items discussed in the conversation
    follow_up_topics: list[str] # A list of topics that require follow-up or further discussion
    supporter_suggestions: dict[str, list[str]]  # Mapping from speaker to list of suggestions
    
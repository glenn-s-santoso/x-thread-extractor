"""Data models for X Thread Extractor."""

from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class Tweet(BaseModel):
    """Model representing a tweet from X."""

    id: str
    text: str
    author_id: str
    created_at: datetime
    conversation_id: str
    in_reply_to_user_id: Optional[str] = None
    referenced_tweets: Optional[List[Dict[str, str]]] = None
    
    @property
    def is_reply(self) -> bool:
        """Check if the tweet is a reply to another user."""
        if self.in_reply_to_user_id and self.in_reply_to_user_id != self.author_id:
            return True
        
        if self.referenced_tweets:
            for ref in self.referenced_tweets:
                if ref.get("type") == "replied_to":
                    return True
        
        return False


class User(BaseModel):
    """Model representing a user on X."""

    id: str
    username: str
    name: str


class Thread(BaseModel):
    """Model representing a thread of tweets."""

    original_tweet_id: str
    conversation_id: str
    author: User
    tweets: List[Tweet]
    
    @property
    def main_thread_only(self) -> List[Tweet]:
        """Return only the main thread tweets (no replies)."""
        return [tweet for tweet in self.tweets if tweet.author_id == self.author.id and not tweet.is_reply]


class ThreadLearnings(BaseModel):
    """Model representing learnings extracted from a thread."""

    thread_id: str
    author: str
    learnings: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "thread_id": self.thread_id,
            "author": self.author,
            "learnings": self.learnings,
            "generated_at": self.generated_at.isoformat(),
        }

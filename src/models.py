"""Data models for X Thread Extractor."""

from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class PublicMetrics(BaseModel):
    """Model representing tweet public metrics."""
    
    retweet_count: int = 0
    reply_count: int = 0
    like_count: int = 0
    quote_count: int = 0
    bookmark_count: int = 0
    impression_count: int = 0


class Tweet(BaseModel):
    """Model representing a tweet from X."""

    id: str
    text: str
    author_id: str
    created_at: datetime
    conversation_id: str
    in_reply_to_user_id: Optional[str] = None
    referenced_tweets: Optional[List[Dict[str, str]]] = None
    public_metrics: Optional[PublicMetrics] = None
    edit_history_tweet_ids: Optional[List[str]] = None
    
    @property
    def is_reply_to_other_user(self) -> bool:
        """Check if the tweet is a reply to another user (not the author)."""
        # If replying to a different user
        if self.in_reply_to_user_id and self.in_reply_to_user_id != self.author_id:
            return True
        return False
    
    @property
    def replied_to_id(self) -> Optional[str]:
        """Get the ID of the tweet this tweet is replying to, if any."""
        if self.referenced_tweets:
            for ref in self.referenced_tweets:
                if ref.get("type") == "replied_to":
                    return ref.get("id")
        return None
    
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
    def sorted_and_cleaned_threads(self) -> List[Tweet]:
        """Return only the main thread tweets (no replies to other users).
        
        This method extracts the main thread by:
        1. Filtering tweets to only include those from the thread author
        2. Looking for thread position indicators or building a reply chain
        3. Returning tweets in chronological order
        
        Returns:
            List of Tweet objects that form the main thread.
        """
        # Get all tweets by the author
        author_tweets = [tweet for tweet in self.tweets if tweet.author_id == self.author.id]
        
        # Filter out replies to other users
        author_tweets = [tweet for tweet in author_tweets if not tweet.is_reply_to_other_user]
           
        # Find the original tweet (the one that's not replying to any other tweet)
        original_tweet = min(author_tweets, key=lambda t: t.created_at)
        
        # If we have no tweets at all, return empty list
        if not original_tweet:
            return []
        
        # Start building the thread with the original tweet
        thread_tweets: List[Tweet] = [original_tweet]
        current_tweet_id = original_tweet.id
        
        # Build the thread by finding the first reply to each tweet
        while current_tweet_id:
            # Find all replies to the current tweet
            replies: List[Tweet] = []
            for tweet in author_tweets:
                if tweet.replied_to_id == current_tweet_id and tweet not in thread_tweets:
                    replies.append(tweet)
                    author_tweets.remove(tweet)

            if not replies: 
                break
                
            # Sort replies by creation time and take the earliest one
            replies.sort(key=lambda t: t.created_at)
            next_tweet = replies[0]
            thread_tweets.append(next_tweet)
            current_tweet_id = next_tweet.id
        
        return thread_tweets


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

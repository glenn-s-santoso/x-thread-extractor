"""API client for interacting with X (Twitter) API."""

import os
from typing import Dict, List, Optional, Any, Tuple

import requests
from dotenv import load_dotenv

from x_thread_extractor.models import Tweet, User, Thread

# Load environment variables
load_dotenv()


class XApiClient:
    """Client for interacting with X (Twitter) API."""

    BASE_URL = "https://api.twitter.com/2"
    
    def __init__(self, bearer_token: Optional[str] = None):
        """Initialize the API client.
        
        Args:
            bearer_token: X API bearer token. If not provided, will try to load from environment.
        """
        self.bearer_token = bearer_token or os.getenv("X_BEARER_TOKEN")
        if not self.bearer_token:
            raise ValueError(
                "X Bearer Token is required. Set it as X_BEARER_TOKEN in your .env file."
            )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
        }
    
    def get_tweet(self, tweet_id: str) -> Tweet:
        """Get a single tweet by ID.
        
        Args:
            tweet_id: The ID of the tweet to retrieve.
            
        Returns:
            Tweet object with the tweet data.
        """
        url = f"{self.BASE_URL}/tweets/{tweet_id}"
        params = {
            "tweet.fields": "author_id,conversation_id,created_at,in_reply_to_user_id,referenced_tweets",
        }
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        response.raise_for_status()
        
        data = response.json()
        return Tweet(**data["data"])
    
    def get_user(self, user_id: str) -> User:
        """Get a user by ID.
        
        Args:
            user_id: The ID of the user to retrieve.
            
        Returns:
            User object with the user data.
        """
        url = f"{self.BASE_URL}/users/{user_id}"
        
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        
        data = response.json()
        return User(**data["data"])
    
    def get_conversation_tweets(self, conversation_id: str) -> List[Tweet]:
        """Get all tweets in a conversation.
        
        Args:
            conversation_id: The ID of the conversation to retrieve.
            
        Returns:
            List of Tweet objects in the conversation.
        """
        url = f"{self.BASE_URL}/tweets/search/recent"
        params = {
            "query": f"conversation_id:{conversation_id}",
            "max_results": 100,
            "tweet.fields": "author_id,conversation_id,created_at,in_reply_to_user_id,referenced_tweets",
        }
        
        tweets = []
        next_token = None
        
        # Paginate through results
        while True:
            if next_token:
                params["next_token"] = next_token
            
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "data" in data:
                for tweet_data in data["data"]:
                    tweets.append(Tweet(**tweet_data))
            
            # Check if there are more pages
            if "next_token" in data.get("meta", {}):
                next_token = data["meta"]["next_token"]
            else:
                break
        
        return tweets
    
    def get_thread(self, tweet_id: str) -> Thread:
        """Get a complete thread starting from a tweet.
        
        Args:
            tweet_id: The ID of a tweet in the thread.
            
        Returns:
            Thread object containing all tweets in the thread.
        """
        # Get the original tweet
        original_tweet = self.get_tweet(tweet_id)
        
        # Get the author
        author = self.get_user(original_tweet.author_id)
        
        # Get all tweets in the conversation
        all_tweets = self.get_conversation_tweets(original_tweet.conversation_id)
        
        # Create and return the thread
        return Thread(
            original_tweet_id=tweet_id,
            conversation_id=original_tweet.conversation_id,
            author=author,
            tweets=all_tweets,
        )

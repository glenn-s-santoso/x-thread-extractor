"""LLM client for generating key learnings from threads."""

import os
from typing import List, Optional

import openai
from dotenv import load_dotenv

from x_thread_extractor.models import Thread, ThreadLearnings

# Load environment variables
load_dotenv()


class LLMClient:
    """Client for interacting with OpenRouter LLM API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the LLM client.
        
        Args:
            api_key: OpenRouter API key. If not provided, will try to load from environment.
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API Key is required for generating learnings. "
                "Set it as OPENROUTER_API_KEY in your .env file."
            )
        
        # Configure OpenAI client to use OpenRouter
        openai.api_key = self.api_key
        openai.api_base = "https://openrouter.ai/api/v1"
    
    def generate_learnings(self, thread: Thread) -> ThreadLearnings:
        """Generate key learnings from a thread.
        
        Args:
            thread: The thread to analyze.
            
        Returns:
            ThreadLearnings object with extracted learnings.
        """
        # Get only the main thread tweets (no replies)
        main_tweets = thread.main_thread_only
        
        # Prepare the thread text
        thread_text = "\n\n".join([
            f"Tweet {i+1}: {tweet.text}"
            for i, tweet in enumerate(main_tweets)
        ])
        
        # Prepare the prompt
        prompt = f"""
        The following is a thread from X (Twitter) by {thread.author.name} (@{thread.author.username}):
        
        {thread_text}
        
        Extract the key learnings or insights from this thread. Format your response as a list of concise bullet points.
        Each bullet point should capture one distinct learning or insight.
        """
        
        # Call the LLM API
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",  # Can be changed to other models
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts key learnings from X threads."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000,
        )
        
        # Extract the learnings from the response
        learnings_text = response.choices[0].message.content.strip()
        
        # Parse the bullet points
        learnings = []
        for line in learnings_text.split("\n"):
            line = line.strip()
            if line.startswith("- "):
                learnings.append(line[2:])
            elif line.startswith("• "):
                learnings.append(line[2:])
            elif line.startswith("* "):
                learnings.append(line[2:])
        
        # Create and return the learnings object
        return ThreadLearnings(
            thread_id=thread.original_tweet_id,
            author=f"{thread.author.name} (@{thread.author.username})",
            learnings=learnings,
        )

"""Thread extractor functionality."""

import json
from typing import Dict, List, Optional, Any, Union

from x_thread_extractor.api import XApiClient
from x_thread_extractor.llm import LLMClient
from x_thread_extractor.models import Thread, ThreadLearnings


def extract_thread(tweet_id: str, x_bearer_token: Optional[str] = None) -> Thread:
    """Extract a thread from X starting with a tweet ID.
    
    Args:
        tweet_id: The ID of a tweet in the thread.
        x_bearer_token: Optional X API bearer token.
        
    Returns:
        Thread object containing the thread data.
    """
    client = XApiClient(bearer_token=x_bearer_token)
    return client.get_thread(tweet_id)


def generate_learnings(thread: Thread, openrouter_api_key: Optional[str] = None) -> ThreadLearnings:
    """Generate key learnings from a thread.
    
    Args:
        thread: The thread to analyze.
        openrouter_api_key: Optional OpenRouter API key.
        
    Returns:
        ThreadLearnings object with the extracted learnings.
    """
    llm_client = LLMClient(api_key=openrouter_api_key)
    return llm_client.generate_learnings(thread)


def extract_and_analyze(
    tweet_id: str,
    generate_learning: bool = True,
    x_bearer_token: Optional[str] = None,
    openrouter_api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Extract a thread and optionally generate learnings.
    
    Args:
        tweet_id: The ID of a tweet in the thread.
        generate_learning: Whether to generate learnings from the thread.
        x_bearer_token: Optional X API bearer token.
        openrouter_api_key: Optional OpenRouter API key.
        
    Returns:
        Dictionary with thread data and optional learnings.
    """
    # Extract the thread
    thread = extract_thread(tweet_id, x_bearer_token)
    
    # Get only the main thread tweets (no replies)
    main_thread_tweets = thread.main_thread_only
    
    # Prepare the result
    result = {
        "thread_id": thread.original_tweet_id,
        "conversation_id": thread.conversation_id,
        "author": {
            "id": thread.author.id,
            "username": thread.author.username,
            "name": thread.author.name,
        },
        "main_thread": [
            {
                "id": tweet.id,
                "text": tweet.text,
                "created_at": tweet.created_at.isoformat(),
            }
            for tweet in main_thread_tweets
        ],
        "total_tweets_in_thread": len(main_thread_tweets),
    }
    
    # Generate learnings if requested
    if generate_learning:
        learnings = generate_learnings(thread, openrouter_api_key)
        result["learnings"] = learnings.learnings
        result["learnings_generated_at"] = learnings.generated_at.isoformat()
    
    return result


def save_to_json(data: Dict[str, Any], output_file: str) -> None:
    """Save data to a JSON file.
    
    Args:
        data: The data to save.
        output_file: The path to the output file.
    """
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

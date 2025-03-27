"""Command-line interface for X Thread Extractor."""

import os
import sys
from typing import Optional

import click
from dotenv import load_dotenv

from x_thread_extractor.extractor import extract_and_analyze, save_to_json

# Load environment variables
load_dotenv()


@click.command()
@click.option(
    "--tweet-id",
    required=True,
    help="ID of the tweet to extract the thread from",
)
@click.option(
    "--output",
    default="thread_output.json",
    help="Path to the output JSON file",
)
@click.option(
    "--x-token",
    help="X API bearer token (overrides environment variable)",
)
@click.option(
    "--openrouter-key",
    help="OpenRouter API key (overrides environment variable)",
)
@click.option(
    "--no-learnings",
    is_flag=True,
    help="Skip generating learnings from the thread",
)
def main(
    tweet_id: str,
    output: str,
    x_token: Optional[str],
    openrouter_key: Optional[str],
    no_learnings: bool,
) -> None:
    """Extract a thread from X and optionally generate key learnings."""
    try:
        # Use provided tokens or fall back to environment variables
        x_bearer_token = x_token or os.getenv("X_BEARER_TOKEN")
        openrouter_api_key = openrouter_key or os.getenv("OPENROUTER_API_KEY")
        
        if not x_bearer_token:
            click.echo(
                "Error: X Bearer Token is required. Provide it with --x-token or set X_BEARER_TOKEN in your .env file.",
                err=True,
            )
            sys.exit(1)
        
        if not no_learnings and not openrouter_api_key:
            click.echo(
                "Warning: OpenRouter API Key is not provided. Learnings will not be generated. "
                "Provide it with --openrouter-key or set OPENROUTER_API_KEY in your .env file, "
                "or use --no-learnings to skip generating learnings.",
                err=True,
            )
            no_learnings = True
        
        # Extract the thread and generate learnings
        click.echo(f"Extracting thread from tweet ID: {tweet_id}")
        result = extract_and_analyze(
            tweet_id=tweet_id,
            generate_learning=not no_learnings,
            x_bearer_token=x_bearer_token,
            openrouter_api_key=openrouter_api_key,
        )
        
        # Save the result to a JSON file
        save_to_json(result, output)
        click.echo(f"Thread extracted successfully and saved to {output}")
        
        # Print a summary
        click.echo(f"\nThread Summary:")
        click.echo(f"Author: {result['author']['name']} (@{result['author']['username']})")
        click.echo(f"Total tweets in thread: {result['total_tweets_in_thread']}")
        
        if not no_learnings and "learnings" in result:
            click.echo("\nKey Learnings:")
            for i, learning in enumerate(result["learnings"], 1):
                click.echo(f"{i}. {learning}")
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

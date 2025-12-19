"""Twitter/X adapter for public content posting.

Uses X API v2 Free tier for posting Frank's investment wisdom and market commentary.
Free tier allows 500 posts/month (~16/day).

This is ONE-WAY content posting only - no DM conversations (would require Basic tier at $100+/mo).
"""

import logging
from typing import Optional

import tweepy

from src.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class TwitterAdapter:
    """Adapter for posting to Twitter/X using API v2."""

    def __init__(self):
        """Initialize Twitter API v2 client."""
        self.client: Optional[tweepy.Client] = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the tweepy Client for API v2."""
        if not settings.twitter_api_key or not settings.twitter_access_token:
            logger.warning("Twitter API credentials not configured")
            return

        try:
            self.client = tweepy.Client(
                consumer_key=settings.twitter_api_key,
                consumer_secret=settings.twitter_api_secret,
                access_token=settings.twitter_access_token,
                access_token_secret=settings.twitter_access_secret,
                bearer_token=settings.twitter_bearer_token,
                wait_on_rate_limit=True,
            )
            logger.info("Twitter API client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {e}")
            self.client = None

    @property
    def is_configured(self) -> bool:
        """Check if Twitter is properly configured."""
        return self.client is not None

    async def post_tweet(
        self,
        content: str,
        reply_to_id: Optional[str] = None,
    ) -> dict:
        """
        Post a tweet.

        Args:
            content: Tweet text (max 280 characters)
            reply_to_id: Optional tweet ID to reply to (for threads)

        Returns:
            dict with success status and tweet ID or error
        """
        if not self.is_configured:
            return {
                "success": False,
                "error": "Twitter API not configured",
            }

        # Validate tweet length
        if len(content) > 280:
            return {
                "success": False,
                "error": f"Tweet exceeds 280 characters ({len(content)} chars)",
            }

        try:
            response = self.client.create_tweet(
                text=content,
                in_reply_to_tweet_id=reply_to_id,
            )

            tweet_id = response.data["id"]
            logger.info(f"Posted tweet: {tweet_id}")

            return {
                "success": True,
                "tweet_id": tweet_id,
                "url": f"https://twitter.com/i/web/status/{tweet_id}",
            }

        except tweepy.TooManyRequests as e:
            logger.warning(f"Twitter rate limit exceeded: {e}")
            return {
                "success": False,
                "error": "Rate limit exceeded. Try again later.",
                "rate_limited": True,
            }

        except tweepy.Forbidden as e:
            logger.error(f"Twitter API forbidden: {e}")
            return {
                "success": False,
                "error": "Not authorized to post. Check API permissions.",
            }

        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def post_thread(self, tweets: list[str]) -> dict:
        """
        Post a thread of tweets.

        Args:
            tweets: List of tweet texts (each max 280 chars)

        Returns:
            dict with success status and list of tweet IDs
        """
        if not self.is_configured:
            return {
                "success": False,
                "error": "Twitter API not configured",
            }

        if not tweets:
            return {
                "success": False,
                "error": "No tweets provided",
            }

        # Validate all tweets
        for i, tweet in enumerate(tweets):
            if len(tweet) > 280:
                return {
                    "success": False,
                    "error": f"Tweet {i+1} exceeds 280 characters ({len(tweet)} chars)",
                }

        tweet_ids = []
        reply_to_id = None

        try:
            for i, tweet_text in enumerate(tweets):
                result = await self.post_tweet(
                    content=tweet_text,
                    reply_to_id=reply_to_id,
                )

                if not result["success"]:
                    return {
                        "success": False,
                        "error": f"Failed at tweet {i+1}: {result.get('error')}",
                        "partial_tweet_ids": tweet_ids,
                    }

                tweet_ids.append(result["tweet_id"])
                reply_to_id = result["tweet_id"]

            logger.info(f"Posted thread with {len(tweet_ids)} tweets")

            return {
                "success": True,
                "tweet_ids": tweet_ids,
                "thread_url": f"https://twitter.com/i/web/status/{tweet_ids[0]}",
            }

        except Exception as e:
            logger.error(f"Failed to post thread: {e}")
            return {
                "success": False,
                "error": str(e),
                "partial_tweet_ids": tweet_ids,
            }

    async def get_rate_limits(self) -> dict:
        """
        Get current rate limit status.

        Free tier: 500 posts/month, 50 requests/15min per endpoint
        """
        if not self.is_configured:
            return {
                "success": False,
                "error": "Twitter API not configured",
            }

        # Note: X API v2 rate limits are returned in response headers
        # This is a basic implementation - for production, track limits
        return {
            "success": True,
            "tier": "free",
            "monthly_limit": 500,
            "note": "Track usage manually. Free tier allows 500 posts/month.",
        }

    async def delete_tweet(self, tweet_id: str) -> dict:
        """
        Delete a tweet by ID.

        Args:
            tweet_id: The ID of the tweet to delete

        Returns:
            dict with success status
        """
        if not self.is_configured:
            return {
                "success": False,
                "error": "Twitter API not configured",
            }

        try:
            self.client.delete_tweet(tweet_id)
            logger.info(f"Deleted tweet: {tweet_id}")
            return {"success": True}

        except Exception as e:
            logger.error(f"Failed to delete tweet {tweet_id}: {e}")
            return {
                "success": False,
                "error": str(e),
            }

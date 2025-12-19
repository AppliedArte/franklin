"""Content Agent - Generates Frank's public content for Twitter/X.

Creates investment wisdom, market commentary, and educational threads
in Frank's distinctive 1700s British gentleman voice.

This is PUBLIC content only - never personalized financial advice.
"""

import json
from typing import Optional

from src.agents.base import BaseAgent


class ContentAgent(BaseAgent):
    """Agent for generating Frank's Twitter content."""

    def __init__(self):
        # Lower temperature for more consistent tweet quality
        super().__init__(temperature=0.7, max_tokens=1024)

    @property
    def system_prompt(self) -> str:
        from src.persona import PERSONA_BACKGROUND

        return f"""{PERSONA_BACKGROUND}

## Your Current Task: Creating Public Content

You are creating public content for Twitter/X. This content should educate and engage, NOT provide personalized financial advice.

## Content Guidelines

**Voice & Style:**
- Stay in character as Frank - the 1700s British gentleman investor
- Be warm, witty, and insightful
- Use British spellings (colour, favour, honour)
- Use period-appropriate expressions naturally, not excessively
- Be engaging and educational

**Topics You Discuss:**
- Market observations and patterns
- Investment philosophy and timeless principles
- Sophisticated strategies explained simply (basis trades, pre-IPO, DeFi)
- Historical parallels to current markets
- Wisdom about risk, patience, and discipline
- Fixed income strategies and opportunities
- Alternative investments and fund structures

**NEVER Do:**
- Give personalized financial advice
- Recommend specific stocks, tokens, or investments to buy/sell
- Make price predictions or guarantees
- Encourage FOMO or urgency
- Use modern slang or emojis

**Format:**
- Tweets must be under 280 characters
- For threads, each tweet should stand alone but flow together
- End wisdom tweets with a memorable phrase or question

## Examples of Your Style

"The basis has widened to 15% annualised. For those with patience and capital, such dislocations are where fortunes are quietly made. The clever money waits whilst others panic."

"I have observed in my years that the greatest threat to wealth is not the markets themselves, but the temperament of the investor. Master thyself before attempting to master the markets."

"Pre-flotation shares offer extraordinary returns - yet require extraordinary patience. One must be prepared to wait years for the harvest. Not every gentleman has such temperament."

"In matters of fixed income, remember: duration risk cuts both ways. When rates fall, you rejoice. When they rise, you learn humility. Best to understand which before committing capital."
"""

    async def generate_wisdom_tweet(self) -> str:
        """
        Generate a standalone investment wisdom tweet.

        Returns a tweet with timeless investing wisdom in Frank's voice.
        """
        prompt = """Generate a single tweet (under 280 characters) containing timeless investment wisdom.

The tweet should:
- Share a universal investing principle or observation
- Be memorable and quotable
- Sound like wisdom from a gentleman who has seen many market cycles
- NOT recommend any specific investments

Return ONLY the tweet text, nothing else."""

        messages = [{"role": "user", "content": prompt}]
        tweet = await self.generate(messages)
        return tweet.strip()

    async def generate_market_commentary(
        self,
        market_context: Optional[str] = None,
    ) -> str:
        """
        Generate market commentary tweet.

        Args:
            market_context: Optional context about current market conditions

        Returns a tweet with market observations in Frank's voice.
        """
        context_section = ""
        if market_context:
            context_section = f"\n\nCurrent market context to reference:\n{market_context}"

        prompt = f"""Generate a single tweet (under 280 characters) with market commentary.

The tweet should:
- Make an observation about markets, trading, or investment conditions
- Draw on historical parallels if appropriate
- Show sophisticated understanding without being pedantic
- NOT make specific predictions or recommendations{context_section}

Return ONLY the tweet text, nothing else."""

        messages = [{"role": "user", "content": prompt}]
        tweet = await self.generate(messages)
        return tweet.strip()

    async def generate_educational_thread(
        self,
        topic: str,
        num_tweets: int = 5,
    ) -> list[str]:
        """
        Generate an educational thread on a topic.

        Args:
            topic: The topic to explain (e.g., "basis trading", "pre-IPO investing")
            num_tweets: Number of tweets in the thread (default 5)

        Returns list of tweets forming a thread.
        """
        prompt = f"""Generate an educational Twitter thread about: {topic}

Requirements:
- Exactly {num_tweets} tweets
- Each tweet MUST be under 280 characters
- First tweet should hook attention and introduce the topic
- Middle tweets explain the concept clearly
- Last tweet should summarize or offer a memorable insight
- Number each tweet (1/, 2/, etc.)
- Explain the concept as if to a sophisticated but curious friend
- Include relevant caveats about risks where appropriate
- Do NOT recommend specific investments

Return the tweets as a JSON array of strings, like:
["1/ First tweet...", "2/ Second tweet...", "3/ Third tweet..."]

Return ONLY the JSON array, nothing else."""

        messages = [{"role": "user", "content": prompt}]
        response = await self.generate(messages)

        try:
            # Parse JSON response
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("\n", 1)[0]
            cleaned = cleaned.strip()

            tweets = json.loads(cleaned)

            # Validate tweet lengths
            validated_tweets = []
            for tweet in tweets:
                if len(tweet) <= 280:
                    validated_tweets.append(tweet)
                else:
                    # Truncate if needed (shouldn't happen with good prompt)
                    validated_tweets.append(tweet[:277] + "...")

            return validated_tweets

        except json.JSONDecodeError:
            # Fallback: try to parse as newline-separated tweets
            lines = response.strip().split("\n")
            tweets = [line.strip() for line in lines if line.strip()]
            return tweets[:num_tweets]

    async def generate_fixed_income_insight(self) -> str:
        """
        Generate a tweet about fixed income/bonds.

        Returns a tweet with fixed income wisdom in Frank's voice.
        """
        prompt = """Generate a single tweet (under 280 characters) about fixed income investing.

Topics might include:
- Duration and interest rate risk
- Credit spreads and quality
- Yield curve observations
- Bond vs equity considerations
- Treasury strategies
- Private credit opportunities

The tweet should:
- Show deep understanding of fixed income markets
- Use sophisticated but accessible language
- NOT recommend specific bonds or funds

Return ONLY the tweet text, nothing else."""

        messages = [{"role": "user", "content": prompt}]
        tweet = await self.generate(messages)
        return tweet.strip()

    async def generate_alternatives_insight(self) -> str:
        """
        Generate a tweet about alternative investments/funds.

        Returns a tweet about alternatives in Frank's voice.
        """
        prompt = """Generate a single tweet (under 280 characters) about alternative investments.

Topics might include:
- Hedge fund strategies (long/short, market neutral, macro)
- Private equity and venture capital
- Fund structures and access
- Illiquidity premium
- Correlation benefits
- Due diligence considerations

The tweet should:
- Show sophisticated understanding of alternatives
- Acknowledge both opportunities and risks
- NOT recommend specific funds

Return ONLY the tweet text, nothing else."""

        messages = [{"role": "user", "content": prompt}]
        tweet = await self.generate(messages)
        return tweet.strip()

    async def generate_topic_tweet(self, topic: str) -> str:
        """
        Generate a tweet on a specific topic.

        Args:
            topic: The topic to tweet about

        Returns a tweet on the requested topic.
        """
        prompt = f"""Generate a single tweet (under 280 characters) about: {topic}

The tweet should:
- Share insight or wisdom about this topic
- Stay in character as a sophisticated British gentleman investor
- Be educational, not promotional
- NOT recommend specific investments

Return ONLY the tweet text, nothing else."""

        messages = [{"role": "user", "content": prompt}]
        tweet = await self.generate(messages)
        return tweet.strip()

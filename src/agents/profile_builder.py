"""Profile Builder Agent - Extracts financial information through natural conversation.

This is the heart of user understanding, inspired by Boardy AI's approach:
- Builds profile through natural conversation, not forms
- Asks one question at a time
- Adapts questions based on what's already known
- Extracts information from any user message
"""

import json
from typing import Optional

from src.agents.base import BaseAgent
from src.db.models import UserProfile


class ProfileBuilder(BaseAgent):
    """Agent that builds user financial profiles through conversation."""

    def __init__(self):
        super().__init__(temperature=0.7, max_tokens=1024)

    @property
    def system_prompt(self) -> str:
        from src.persona import PERSONA_BACKGROUND

        return f"""{PERSONA_BACKGROUND}

## Your Current Task: Getting to Know Your Client

You are having a natural conversation to understand this person's financial situation and goals. As a proper gentleman, you do this through warm dialogue, not interrogation.

## Your Approach
- Be warm and conversational, as befitting a gentleman of your standing
- Ask ONE question at a time, building on previous answers
- Listen with genuine interest and acknowledge what they share
- Be understanding of any financial circumstance - there is no shame in honest accounts
- Make them feel at ease sharing sensitive matters

## Information to Gather (gradually, through natural discourse)

**Basic Understanding:**
1. Their primary financial aspiration (wealth growth, income generation, capital preservation, liquidity event planning)
2. General sense of their financial scale (are they an accredited investor, qualified purchaser, or institutional?)
3. Their current holdings - both liquid and illiquid (public equities, alternatives, private investments, digital assets)

**Sophistication & Experience:**
4. Their experience with alternative investments (hedge funds, PE, venture, private credit)
5. Their familiarity with crypto/DeFi (have they done basis trades, yield farming, or just hold spot?)
6. Any current deal flow or opportunities they're evaluating

**Risk & Liquidity:**
7. Their temperament regarding risk AND their actual capacity for illiquidity
8. Timeline considerations - any upcoming liquidity needs or events?
9. Concentration risks - any large single positions (founder stock, crypto holdings, etc.)?

**Interests & Access:**
10. Specific sectors or strategies of interest (crypto, pre-IPO, venture, real estate, etc.)
11. What access they currently have (any fund relationships, deal flow sources, networks?)
12. What they feel they're missing or want to learn about

## Important Guidelines
- NEVER ask for specific account details or passwords - a gentleman does not pry
- If they seem uncomfortable, gracefully change course
- Acknowledge progress and wise decisions they've made
- Keep responses measured (2-4 sentences typically)
- Always conclude with a relevant question OR a thoughtful observation

## Compliance
- While you offer wisdom freely, you are not a licensed advisor in the modern sense
- For specific recommendations, you shall eventually suggest they consult qualified professionals
- Include appropriate caveats when discussing financial matters

## Example of Your Manner
"Most excellent! Building wealth for a life of leisure in one's later years - a most prudent aspiration indeed. Now then, if I may inquire - are you presently setting aside funds regularly for investment, or is this a venture you wish to commence?"

Remember: Your purpose is to understand them thoroughly, not to interrogate. Build proper rapport first, as any gentleman would."""

    async def extract_profile_info(
        self,
        user_message: str,
        ai_response: str,
        current_profile: UserProfile,
    ) -> Optional[dict]:
        """
        Extract profile information from a conversation exchange.

        Returns dict of profile fields to update, or None if nothing new.
        """
        extraction_prompt = f"""Analyze this conversation exchange and extract any financial profile information.

Current profile state:
- Annual income: {current_profile.annual_income or 'unknown'}
- Net worth: {current_profile.net_worth or 'unknown'}
- Liquid assets: {current_profile.liquid_assets or 'unknown'}
- Monthly expenses: {current_profile.monthly_expenses or 'unknown'}
- Primary goal: {current_profile.primary_goal or 'unknown'}
- Goal timeline: {current_profile.goal_timeline or 'unknown'}
- Risk tolerance: {current_profile.risk_tolerance or 'unknown'}
- Interests: {current_profile.interests or 'unknown'}

User said: "{user_message}"
AI responded: "{ai_response}"

Extract any NEW information that updates the profile. Return ONLY a JSON object with the fields to update.
Use null for fields with no new information. For numeric fields, use reasonable estimates if exact figures aren't given.

Risk tolerance must be one of: "conservative", "moderate", "aggressive"
Interests should be a list of strings like: ["crypto", "real estate", "stocks"]

Example output:
{{"annual_income": 150000, "primary_goal": "early retirement", "risk_tolerance": "moderate", "interests": ["index funds", "real estate"]}}

Return only the JSON, no explanation."""

        messages = [{"role": "user", "content": extraction_prompt}]

        try:
            response = await self.generate(messages)

            # Parse JSON response
            # Clean up response - remove markdown code blocks if present
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("\n", 1)[0]
            cleaned = cleaned.strip()

            extracted = json.loads(cleaned)

            # Filter out null values
            return {k: v for k, v in extracted.items() if v is not None}

        except (json.JSONDecodeError, Exception):
            # If extraction fails, return None
            return None

    def get_next_question_priority(self, profile: UserProfile) -> list[str]:
        """
        Determine which profile fields to prioritize asking about.

        Returns ordered list of field names to focus on.
        """
        priorities = []

        # Most important first
        if not profile.primary_goal:
            priorities.append("primary_goal")

        if not profile.risk_tolerance:
            priorities.append("risk_tolerance")

        if not profile.annual_income:
            priorities.append("annual_income")

        if not profile.goal_timeline:
            priorities.append("goal_timeline")

        if not profile.net_worth:
            priorities.append("net_worth")

        if not profile.interests:
            priorities.append("interests")

        if not profile.monthly_expenses:
            priorities.append("monthly_expenses")

        if not profile.liquid_assets:
            priorities.append("liquid_assets")

        return priorities

    def build_context_prompt(self, profile: UserProfile) -> str:
        """Build context about what's known and what to ask next."""
        known = []
        unknown = []

        fields = {
            "primary_goal": "their main financial goal",
            "risk_tolerance": "their risk tolerance",
            "annual_income": "their income level",
            "goal_timeline": "their timeline",
            "net_worth": "their net worth",
            "interests": "their investment interests",
            "monthly_expenses": "their expenses",
            "liquid_assets": "their liquid assets",
        }

        for field, description in fields.items():
            value = getattr(profile, field, None)
            if value:
                known.append(f"- {description}: {value}")
            else:
                unknown.append(description)

        context = ""
        if known:
            context += "What you know about this user:\n" + "\n".join(known) + "\n\n"

        if unknown:
            priorities = self.get_next_question_priority(profile)
            context += f"Priority to learn next: {priorities[0] if priorities else 'nothing specific'}\n"
            context += "Still unknown: " + ", ".join(unknown[:3])

        return context

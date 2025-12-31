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

## Your Current Task: Due Diligence on Fund Managers

You are conducting due diligence on fund managers and GPs who seek capital or partnership. As a seasoned allocator and gentleman of considerable experience, you conduct this through sophisticated yet warm dialogue.

## Your Approach
- Be warm but thorough - you are evaluating whether to allocate capital
- Ask ONE question at a time, building naturally on previous answers
- Listen with genuine interest and probe deeper when warranted
- Make them feel respected while gathering critical information
- Show you understand the fund management business deeply

## Due Diligence Framework (gather through natural discourse)

### PHASE 1: Fund Basics & Background
1. **Who they are** - Their name, role, and the fund they represent
2. **Fund type** - VC, PE, hedge fund, crypto fund, real estate, credit, etc.
3. **Fund stage** - Emerging manager, established, or institutional scale?
4. **Vintage** - When did they start? Which fund number is this?

### PHASE 2: Investment Thesis & Strategy
5. **Core thesis** - What is their investment thesis? What problem do they solve?
6. **Target sectors** - Which industries/verticals do they focus on?
7. **Target geography** - Where do they invest? US, Europe, Asia, global?
8. **Target stage** - Pre-seed, seed, Series A, growth, buyout, etc.?

### PHASE 3: Economics & Fund Terms
9. **Cheque size** - What is their typical investment size? Min/max?
10. **Target ownership** - What ownership percentage do they seek?
11. **Fund size** - Target AUM and current AUM?
12. **Terms** - Management fee and carry structure?

### PHASE 4: Track Record & Performance
13. **Portfolio** - How many investments have they made?
14. **Notable deals** - Any recognizable portfolio companies?
15. **Exits** - How many exits? Any notable ones?
16. **Returns** - What returns have they generated? (MOIC, IRR if available)

### PHASE 5: Team & Operations
17. **Team composition** - How large is the team? Key partners?
18. **Team background** - Where did they come from? Relevant experience?
19. **GP commitment** - How much skin in the game?

### PHASE 6: LP Base & Fundraising
20. **Current LPs** - Who are their existing investors? (family offices, endowments, funds of funds)
21. **Fundraising status** - Are they raising? When do they expect to close?

### PHASE 7: Differentiation
22. **Competitive edge** - What makes them different from other funds in their space?
23. **Value-add** - How do they help their portfolio companies beyond capital?
24. **Deal flow** - Where does their deal flow come from?

## Important Guidelines
- Be thorough but not interrogative - this is a dialogue, not a questionnaire
- Acknowledge strong points - "That is indeed an impressive track record"
- Probe gently on weak areas - "And how might you address..."
- Keep responses measured (2-4 sentences typically)
- Always conclude with the next logical question
- Show you understand fund economics deeply (carry, MOIC, J-curve, etc.)

## Example of Your Manner
"A most intriguing thesis indeed - infrastructure for the tokenised economy. Now then, if I may inquire about the particulars - what cheque size do you typically deploy, and at what stage do you prefer to enter?"

"That is a respectable vintage for an emerging manager. Pray tell, what returns have your earlier investments generated thus far? Even unrealised marks would be of interest."

Remember: You are evaluating whether this manager deserves capital allocation. Be thorough, sophisticated, and discerning - but always a gentleman."""

    async def extract_profile_info(
        self,
        user_message: str,
        ai_response: str,
        current_profile: UserProfile,
    ) -> Optional[dict]:
        """
        Extract fund manager DD information from a conversation exchange.

        Returns dict of profile fields to update, or None if nothing new.
        """
        extraction_prompt = f"""Analyze this conversation exchange and extract fund manager due diligence information.

Current profile state:
## Fund Basics
- Fund name: {current_profile.fund_name or 'unknown'}
- Fund type: {current_profile.fund_type or 'unknown'}
- Fund stage: {current_profile.fund_stage or 'unknown'}
- Fund vintage: {current_profile.fund_vintage or 'unknown'}

## Investment Thesis
- Investment thesis: {current_profile.investment_thesis or 'unknown'}
- Target sectors: {current_profile.target_sectors or 'unknown'}
- Target geography: {current_profile.target_geography or 'unknown'}
- Target stage: {current_profile.target_stage or 'unknown'}

## Economics
- Cheque size min: {current_profile.cheque_size_min or 'unknown'}
- Cheque size max: {current_profile.cheque_size_max or 'unknown'}
- Target ownership: {current_profile.target_ownership or 'unknown'}
- Fund size target: {current_profile.fund_size_target or 'unknown'}
- Fund size current: {current_profile.fund_size_current or 'unknown'}
- Management fee: {current_profile.management_fee or 'unknown'}
- Carry: {current_profile.carry or 'unknown'}

## Track Record
- Num investments: {current_profile.num_investments or 'unknown'}
- Num exits: {current_profile.num_exits or 'unknown'}
- Notable investments: {current_profile.notable_investments or 'unknown'}
- Realized returns: {current_profile.realized_returns or 'unknown'}
- IRR: {current_profile.irr or 'unknown'}

## Team
- Team size: {current_profile.team_size or 'unknown'}
- Team background: {current_profile.team_background or 'unknown'}
- GP commitment: {current_profile.gp_commitment or 'unknown'}

## LP Base & Fundraising
- Current LPs: {current_profile.current_lps or 'unknown'}
- Fundraising status: {current_profile.fundraising_status or 'unknown'}
- Target close date: {current_profile.target_close_date or 'unknown'}

## Differentiation
- Competitive edge: {current_profile.competitive_edge or 'unknown'}
- Value add: {current_profile.value_add or 'unknown'}

User said: "{user_message}"
AI responded: "{ai_response}"

Extract any NEW information that updates the profile. Return ONLY a JSON object with the fields to update.
Use null for fields with no new information.

Field types:
- fund_name: string
- fund_type: string (VC, PE, hedge, crypto, real_estate, credit, multi_strategy)
- fund_stage: string (emerging, established, institutional)
- fund_vintage: integer (year)
- investment_thesis: string (their core thesis)
- target_sectors: list of strings ["fintech", "AI", "healthcare"]
- target_geography: list of strings ["US", "Europe", "SEA"]
- target_stage: string (pre_seed, seed, series_a, series_b, growth, buyout)
- cheque_size_min: float (in USD)
- cheque_size_max: float (in USD)
- target_ownership: string (e.g., "10-20%")
- fund_size_target: float (in USD)
- fund_size_current: float (in USD)
- management_fee: string (e.g., "2%")
- carry: string (e.g., "20%")
- num_investments: integer
- num_exits: integer
- notable_investments: list of strings (company names)
- realized_returns: string (e.g., "3.2x MOIC")
- irr: string (e.g., "28% net IRR")
- team_size: integer
- team_background: string
- gp_commitment: string (e.g., "2% of fund" or "$5M")
- current_lps: string (description of LP base)
- fundraising_status: string (raising, first_close, final_close, closed, evergreen)
- target_close_date: string
- competitive_edge: string
- value_add: string

Also set is_fund_manager: true if this is clearly a fund manager.

Example output:
{{"is_fund_manager": true, "fund_name": "Acme Ventures", "fund_type": "VC", "investment_thesis": "B2B SaaS in emerging markets", "cheque_size_min": 500000, "cheque_size_max": 2000000, "target_sectors": ["SaaS", "fintech"]}}

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
        Determine which fund manager DD fields to prioritize asking about.

        Returns ordered list of field names to focus on.
        """
        priorities = []

        # Phase 1: Fund Basics (most important first)
        if not profile.fund_name:
            priorities.append("fund_name")
        if not profile.fund_type:
            priorities.append("fund_type")
        if not profile.fund_stage:
            priorities.append("fund_stage")

        # Phase 2: Investment Thesis
        if not profile.investment_thesis:
            priorities.append("investment_thesis")
        if not profile.target_sectors:
            priorities.append("target_sectors")
        if not profile.target_stage:
            priorities.append("target_stage")

        # Phase 3: Economics
        if not profile.cheque_size_min and not profile.cheque_size_max:
            priorities.append("cheque_size")
        if not profile.fund_size_target:
            priorities.append("fund_size")

        # Phase 4: Track Record
        if not profile.num_investments:
            priorities.append("track_record")
        if not profile.notable_investments:
            priorities.append("notable_investments")
        if not profile.realized_returns and not profile.irr:
            priorities.append("returns")

        # Phase 5: Team
        if not profile.team_size:
            priorities.append("team")
        if not profile.gp_commitment:
            priorities.append("gp_commitment")

        # Phase 6: Fundraising
        if not profile.fundraising_status:
            priorities.append("fundraising_status")
        if not profile.current_lps:
            priorities.append("lp_base")

        # Phase 7: Differentiation
        if not profile.competitive_edge:
            priorities.append("competitive_edge")
        if not profile.value_add:
            priorities.append("value_add")

        return priorities

    def build_context_prompt(self, profile: UserProfile) -> str:
        """Build context about what's known and what to ask next for fund manager DD."""
        known = []
        unknown = []

        fields = {
            # Fund Basics
            "fund_name": "fund name",
            "fund_type": "fund type",
            "fund_stage": "fund stage",
            "fund_vintage": "vintage year",
            # Thesis
            "investment_thesis": "investment thesis",
            "target_sectors": "target sectors",
            "target_geography": "target geography",
            "target_stage": "target stage",
            # Economics
            "cheque_size_min": "minimum cheque size",
            "cheque_size_max": "maximum cheque size",
            "target_ownership": "target ownership",
            "fund_size_target": "target fund size",
            "fund_size_current": "current AUM",
            "management_fee": "management fee",
            "carry": "carry",
            # Track Record
            "num_investments": "number of investments",
            "num_exits": "number of exits",
            "notable_investments": "notable portfolio companies",
            "realized_returns": "realized returns",
            "irr": "IRR",
            # Team
            "team_size": "team size",
            "team_background": "team background",
            "gp_commitment": "GP commitment",
            # Fundraising
            "current_lps": "LP base",
            "fundraising_status": "fundraising status",
            "target_close_date": "target close date",
            # Differentiation
            "competitive_edge": "competitive edge",
            "value_add": "value-add capabilities",
        }

        for field, description in fields.items():
            value = getattr(profile, field, None)
            if value:
                known.append(f"- {description}: {value}")
            else:
                unknown.append(description)

        context = ""
        if known:
            context += "## What you know about this fund manager:\n" + "\n".join(known) + "\n\n"

        if unknown:
            priorities = self.get_next_question_priority(profile)
            context += f"## Priority to learn next: {priorities[0] if priorities else 'DD complete'}\n"
            context += "Still unknown: " + ", ".join(unknown[:5])

        return context

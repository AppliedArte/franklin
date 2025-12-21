"""Advisory Agent - Core wealth guidance agent.

Provides general wealth advice once the user profile is sufficiently built.
Routes to specialist modules when appropriate.
Uses RAG for context from user documents and facts.
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.base import BaseAgent
from src.rag.retrieval import RetrievalService


class AdvisoryAgent(BaseAgent):
    """Main advisory agent for wealth guidance."""

    def __init__(self):
        super().__init__(temperature=0.6, max_tokens=2048)
        self.retrieval_service = RetrievalService()

    @property
    def system_prompt(self) -> str:
        from src.persona import PERSONA_BACKGROUND

        return f"""{PERSONA_BACKGROUND}

## Your Current Task: Providing Wealth Guidance

You now know this person well enough to offer substantive counsel. Draw upon your considerable experience to guide them toward prosperity.

## Your Role
- Provide thoughtful, personalized counsel based on what you know of their circumstances
- Help them grow their fortune, preserve what they have, and achieve their aspirations
- Recommend strategies befitting their temperament and timeline
- Know when matters require specialists (solicitors, accountants, and the like)

## Core Principles

### 1. Counsel Tailored to Their Situation
Always consider what you know of them:
- Their temperament regarding risk shapes your recommendations
- Their timeline affects strategy (bold growth vs careful preservation)
- Their income determines what they might set aside
- Their current holdings inform diversification needs

### 2. Education First
- Explain matters clearly, as you would to a friend
- Help them understand the WHY, not merely the WHAT
- Build their understanding of financial matters over time

### 3. Prudent Recommendations
- "Never place all your eggs in a single basket" - diversification is paramount
- Emphasize measured growth and protection against loss
- Suggest modest beginnings with new ventures
- Recommend professional counsel for complex matters

### 4. Actionable Guidance
- Provide concrete steps, not mere platitudes
- Suggest specific proportions when appropriate
- Break grand ambitions into achievable milestones

## Matters You May Counsel On

**Alternative Investments & Private Markets:**
- Hedge fund strategies (long/short, market neutral, global macro)
- Private equity and venture capital allocation
- Pre-IPO opportunities and secondary market transactions
- SPV structures for direct investments
- Fund of funds vs direct investment considerations

**Crypto & Digital Assets:**
- Basis trading and cash-futures arbitrage strategies
- DeFi yield strategies (lending, liquidity provision, staking)
- On-chain opportunities and protocol analysis
- Custody solutions and security considerations
- Tax implications of digital asset transactions

**Structured Products & Credit:**
- Private credit opportunities
- Preferred equity structures
- Convertible instruments
- Real estate syndications
- Revenue-based financing

**Portfolio Strategy:**
- Alternative allocation frameworks (endowment model, risk parity)
- Correlation analysis and true diversification
- Liquidity management across public and private holdings
- Rebalancing strategies for illiquid positions
- Leverage considerations and margin management

**Tax-Efficient Structures:**
- Opportunity zone investments
- Carried interest and performance allocations
- Estate planning considerations for complex portfolios
- QSBS and founder stock strategies
- International structuring considerations

**Deal Analysis:**
- Cap table analysis and liquidation preferences
- Valuation frameworks for private companies
- Due diligence frameworks
- Term sheet analysis
- Exit scenario modeling

## Matters to Refer to Specialists
- Specific tax filings → "A tax counsel well-versed in such matters would serve you here"
- Legal document review → "Your solicitor should review the particulars"
- Regulatory compliance → "A compliance specialist would be prudent"
- Insurance and estate documents → "An estate planning attorney, I should think"
- Specific trade execution → "Your broker or execution desk would handle the particulars"

## Your Manner of Response
- Warm yet proper
- Measured in length (2-4 paragraphs typically)
- Use enumerated points for multiple recommendations
- Always conclude with a question or suggested next step
- Acknowledge their situation before offering counsel

## Compliance (in your own words)
When offering investment guidance, include something to the effect of:
"*I offer this counsel as a gentleman sharing wisdom, not as a licensed advisor in the modern sense. For matters of particular import, do consider consulting a qualified professional.*"

## Pattern of Response
1. Acknowledge their question or situation with understanding
2. Provide relevant wisdom or context
3. Give specific, actionable counsel
4. Suggest a next step or pose a follow-up question"""

    async def generate_with_profile(
        self,
        messages: list[dict],
        profile_context: str,
    ) -> str:
        """Generate response with profile context injected into system prompt."""
        enhanced_prompt = f"""{self.system_prompt}

## User Profile Context
{profile_context}

Use this profile information to personalize your advice."""

        return await self.generate(messages, system_override=enhanced_prompt)

    async def generate_with_rag(
        self,
        db: AsyncSession,
        user_id: str,
        messages: list[dict],
        profile_context: str = "",
    ) -> str:
        """Generate response with RAG context from documents and user facts."""
        # Get the latest user message for retrieval
        user_query = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_query = msg.get("content", "")
                break

        # Retrieve relevant context
        rag_context = await self.retrieval_service.retrieve_for_query(
            db=db,
            user_id=user_id,
            query=user_query,
            top_k_chunks=5,
            top_k_facts=10,
            include_recent_messages=0,  # We already have messages
        )

        # Build enhanced prompt with RAG context
        rag_prompt_context = rag_context.to_prompt_context()

        enhanced_prompt = f"""{self.system_prompt}

## User Profile Context
{profile_context}

{rag_prompt_context}

Use all available context to provide personalized, informed advice. Reference specific details from their documents or previous conversations when relevant."""

        return await self.generate(messages, system_override=enhanced_prompt)

    def get_specialist_recommendation(self, topic: str) -> Optional[str]:
        """
        Determine if topic needs specialist referral.

        Returns referral message if needed, None otherwise.
        """
        specialist_topics = {
            "tax": "For detailed tax planning, I'd recommend consulting with a CPA or tax professional who can review your complete financial picture.",
            "estate": "Estate planning involves legal documents and strategies that are best handled by an estate planning attorney.",
            "insurance": "An insurance professional can help assess your specific coverage needs and compare options.",
            "legal": "This involves legal considerations that would be best discussed with a qualified attorney.",
            "medical": "For health-related financial decisions, consider consulting both your healthcare provider and a financial advisor who specializes in healthcare planning.",
        }

        topic_lower = topic.lower()
        for keyword, referral in specialist_topics.items():
            if keyword in topic_lower:
                return referral

        return None

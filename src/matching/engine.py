"""Matching Engine - Boardy-style user-to-service matching.

Implements Boardy AI's matching philosophy:
1. Anchor on user's concrete goals
2. Filter by role fit, mandate, timing, mutual value
3. Only match when high confidence
4. Track outcomes for learning
"""

from typing import Optional, List
from datetime import datetime, timedelta

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User, UserProfile, PartnerService, Referral


class MatchingEngine:
    """Boardy-style matching engine for connecting users with services/advisors."""

    def __init__(self, db: AsyncSession):
        self.db = db
        # Minimum profile score needed before making matches
        self.min_profile_score = 40
        # Cooldown between referrals to same user
        self.referral_cooldown_days = 7
        # Max active referrals per user
        self.max_active_referrals = 3

    async def find_matches(
        self,
        user: User,
        limit: int = 5,
    ) -> List[dict]:
        """
        Find potential matches for a user based on their profile.

        Returns list of potential matches with scores and reasons.
        """
        if not user.profile or user.profile.profile_score < self.min_profile_score:
            return []

        # Check referral limits
        if await self._exceeds_referral_limits(user):
            return []

        # Get all active partner services
        result = await self.db.execute(
            select(PartnerService).where(PartnerService.is_active == True)
        )
        services = result.scalars().all()

        # Score each service against user profile
        scored_matches = []
        for service in services:
            score, reasons = self._calculate_match_score(user.profile, service)
            if score > 0.5:  # Minimum threshold
                scored_matches.append({
                    "service": service,
                    "score": score,
                    "reasons": reasons,
                })

        # Sort by score and limit
        scored_matches.sort(key=lambda x: x["score"], reverse=True)
        return scored_matches[:limit]

    async def create_referral(
        self,
        user: User,
        service: PartnerService,
        reason: str,
    ) -> Referral:
        """Create a referral record for tracking."""
        import uuid

        referral = Referral(
            id=str(uuid.uuid4()),
            user_id=user.id,
            partner_service_id=service.id,
            reason=reason,
            status="pending",
        )

        self.db.add(referral)
        await self.db.flush()

        return referral

    async def update_referral_outcome(
        self,
        referral_id: str,
        status: str,
        notes: Optional[str] = None,
    ) -> None:
        """Update the outcome of a referral."""
        result = await self.db.execute(
            select(Referral).where(Referral.id == referral_id)
        )
        referral = result.scalar_one_or_none()

        if referral:
            referral.status = status
            referral.outcome_notes = notes
            if status == "converted":
                referral.converted_at = datetime.utcnow()

    def _calculate_match_score(
        self,
        profile: UserProfile,
        service: PartnerService,
    ) -> tuple[float, List[str]]:
        """
        Calculate match score between user profile and service.

        Returns (score 0-1, list of reasons).
        """
        score = 0.0
        reasons = []
        max_score = 0.0

        # 1. Category/Interest match (weight: 0.3)
        max_score += 0.3
        if profile.interests and service.interests_match:
            overlap = set(profile.interests) & set(service.interests_match)
            if overlap:
                score += 0.3 * (len(overlap) / len(service.interests_match))
                reasons.append(f"Interest match: {', '.join(overlap)}")

        # 2. Risk profile match (weight: 0.2)
        max_score += 0.2
        if profile.risk_tolerance and service.risk_profiles:
            if profile.risk_tolerance in service.risk_profiles:
                score += 0.2
                reasons.append(f"Risk profile compatible")

        # 3. Financial thresholds (weight: 0.25)
        max_score += 0.25
        threshold_match = True

        if service.min_net_worth and profile.net_worth:
            if profile.net_worth >= service.min_net_worth:
                reasons.append("Meets net worth requirement")
            else:
                threshold_match = False

        if service.min_income and profile.annual_income:
            if profile.annual_income >= service.min_income:
                reasons.append("Meets income requirement")
            else:
                threshold_match = False

        if threshold_match:
            score += 0.25

        # 4. Goal alignment (weight: 0.25)
        max_score += 0.25
        if profile.primary_goal and service.category:
            goal_category_map = {
                "retirement": ["retirement", "wealth_management", "tax"],
                "wealth growth": ["investments", "crypto", "real_estate"],
                "passive income": ["real_estate", "dividends", "private_credit"],
                "tax optimization": ["tax", "estate_planning"],
            }

            goal_lower = profile.primary_goal.lower()
            for goal_keyword, categories in goal_category_map.items():
                if goal_keyword in goal_lower and service.category in categories:
                    score += 0.25
                    reasons.append(f"Aligns with {profile.primary_goal} goal")
                    break

        # Normalize score
        final_score = score / max_score if max_score > 0 else 0

        return final_score, reasons

    async def _exceeds_referral_limits(self, user: User) -> bool:
        """Check if user has too many recent/active referrals."""
        cutoff = datetime.utcnow() - timedelta(days=self.referral_cooldown_days)

        result = await self.db.execute(
            select(Referral).where(
                and_(
                    Referral.user_id == user.id,
                    Referral.created_at > cutoff,
                    Referral.status.in_(["pending", "contacted"]),
                )
            )
        )
        recent_referrals = result.scalars().all()

        return len(recent_referrals) >= self.max_active_referrals

    async def get_referral_history(
        self,
        user: User,
        limit: int = 10,
    ) -> List[Referral]:
        """Get referral history for a user."""
        result = await self.db.execute(
            select(Referral)
            .where(Referral.user_id == user.id)
            .order_by(Referral.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    def should_suggest_match(
        self,
        user: User,
        conversation_context: str,
    ) -> bool:
        """
        Determine if we should suggest a match based on conversation context.

        This is the "timing" aspect of Boardy's philosophy - only match
        when the user is ready and the context is right.
        """
        if not user.profile or user.profile.profile_score < self.min_profile_score:
            return False

        # Keywords that suggest user might benefit from specialist help
        trigger_keywords = [
            "need help with",
            "looking for",
            "recommend",
            "who can help",
            "specialist",
            "professional",
            "advisor",
            "beyond my expertise",
        ]

        context_lower = conversation_context.lower()
        return any(keyword in context_lower for keyword in trigger_keywords)

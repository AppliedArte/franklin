"""User and profile factories for test data generation."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import factory
from faker import Faker

fake = Faker()


class UserFactory(factory.Factory):
    """Factory for creating test User instances."""

    class Meta:
        model = dict

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.LazyFunction(fake.name)
    email = factory.LazyFunction(fake.email)
    phone = factory.LazyFunction(lambda: f"+1{fake.msisdn()[3:]}")
    lead_status = "new"
    is_active = True
    created_at = factory.LazyFunction(datetime.utcnow)
    timezone = "America/New_York"

    class Params:
        engaged = factory.Trait(
            lead_status="engaged",
            onboarding_completed=True,
        )
        converted = factory.Trait(
            lead_status="converted",
            onboarding_completed=True,
        )


class UserProfileFactory(factory.Factory):
    """Factory for creating test UserProfile instances."""

    class Meta:
        model = dict

    id = factory.LazyFunction(lambda: str(uuid4()))
    user_id = factory.LazyFunction(lambda: str(uuid4()))
    net_worth = factory.LazyFunction(lambda: fake.random_int(100000, 10000000))
    annual_income = factory.LazyFunction(lambda: fake.random_int(50000, 1000000))
    risk_tolerance = factory.LazyFunction(lambda: fake.random_element(["conservative", "moderate", "aggressive"]))
    primary_goal = factory.LazyFunction(lambda: fake.random_element([
        "wealth preservation",
        "growth",
        "income generation",
        "retirement planning",
    ]))
    profile_score = factory.LazyFunction(lambda: fake.random_int(0, 100))
    created_at = factory.LazyFunction(datetime.utcnow)

    class Params:
        accredited = factory.Trait(
            net_worth=factory.LazyFunction(lambda: fake.random_int(1000000, 50000000)),
            is_accredited=True,
            investor_type="accredited",
        )
        high_net_worth = factory.Trait(
            net_worth=factory.LazyFunction(lambda: fake.random_int(10000000, 100000000)),
            is_accredited=True,
            investor_type="qualified_purchaser",
        )
        fund_manager = factory.Trait(
            is_fund_manager=True,
            fund_name=factory.LazyFunction(lambda: f"{fake.company()} Capital"),
            fund_type=factory.LazyFunction(lambda: fake.random_element(["VC", "PE", "hedge"])),
        )

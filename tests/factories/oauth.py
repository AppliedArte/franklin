"""OAuth credential factories for test data generation."""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

import factory


class OAuthCredentialFactory(factory.Factory):
    """Factory for creating test OAuth credentials."""

    class Meta:
        model = dict

    id = factory.LazyFunction(lambda: str(uuid4()))
    user_id = factory.LazyFunction(lambda: str(uuid4()))
    provider = "google"
    access_token = factory.LazyFunction(lambda: f"ya29.test-{uuid4().hex[:16]}")
    refresh_token = factory.LazyFunction(lambda: f"1//test-{uuid4().hex[:16]}")
    token_expiry = factory.LazyFunction(lambda: datetime.utcnow() + timedelta(hours=1))
    scopes = factory.LazyFunction(lambda: [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events",
    ])
    is_valid = True
    created_at = factory.LazyFunction(datetime.utcnow)

    class Params:
        expired = factory.Trait(
            token_expiry=factory.LazyFunction(lambda: datetime.utcnow() - timedelta(hours=1)),
        )
        invalid = factory.Trait(
            is_valid=False,
            error_message="Token revoked by user",
        )
        no_refresh = factory.Trait(
            refresh_token=None,
        )
        plaid = factory.Trait(
            provider="plaid",
            scopes=["transactions", "accounts"],
        )


class GoogleCalendarEventFactory(factory.Factory):
    """Factory for creating mock Google Calendar events."""

    class Meta:
        model = dict

    id = factory.LazyFunction(lambda: f"evt_{uuid4().hex[:12]}")
    summary = factory.Faker("sentence", nb_words=3)
    location = factory.Faker("address")
    description = factory.Faker("paragraph")

    @factory.lazy_attribute
    def start(self):
        start_time = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
        return {"dateTime": start_time.isoformat() + "Z", "timeZone": "UTC"}

    @factory.lazy_attribute
    def end(self):
        end_time = datetime.utcnow().replace(hour=11, minute=0, second=0, microsecond=0)
        return {"dateTime": end_time.isoformat() + "Z", "timeZone": "UTC"}

    attendees = factory.LazyFunction(lambda: [])
    htmlLink = factory.LazyFunction(lambda: f"https://calendar.google.com/event?eid={uuid4().hex[:16]}")

    class Params:
        all_day = factory.Trait(
            start=factory.LazyAttribute(lambda o: {"date": datetime.utcnow().strftime("%Y-%m-%d")}),
            end=factory.LazyAttribute(lambda o: {"date": (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")}),
        )
        with_attendees = factory.Trait(
            attendees=factory.LazyFunction(lambda: [
                {"email": "attendee1@example.com", "responseStatus": "accepted"},
                {"email": "attendee2@example.com", "responseStatus": "needsAction"},
            ]),
        )

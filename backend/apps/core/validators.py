"""Reusable validators and sanitization functions."""
import re
from typing import Any
from decimal import Decimal, InvalidOperation
from django.utils.html import escape
from rest_framework import serializers


class SanitizationMixin:
    """Mixin for common sanitization methods."""

    @staticmethod
    def sanitize_name(value: str, min_len: int = 2, max_len: int = 100) -> str:
        """Sanitize and validate name fields."""
        if not value or len(value.strip()) < min_len:
            raise serializers.ValidationError(
                f"Name must be at least {min_len} characters long."
            )
        return escape(value.strip()[:max_len])

    @staticmethod
    def sanitize_email(value: str, max_len: int = 254) -> str:
        """Sanitize and validate email fields."""
        if not value:
            raise serializers.ValidationError("Email is required.")
        value = value.strip().lower()
        if len(value) > max_len:
            raise serializers.ValidationError("Email address is too long.")
        return value

    @staticmethod
    def sanitize_phone(value: str, max_len: int = 20) -> str:
        """Sanitize phone number, removing malicious chars."""
        if not value:
            return value
        cleaned = re.sub(r'[^0-9+\-\s()]', '', value)
        return cleaned[:max_len]

    @staticmethod
    def sanitize_text(
        value: str, min_len: int = 5, max_len: int = 2000, allow_links: int = 3
    ) -> str:
        """Sanitize general text (messages, replies)."""
        if not value or len(value.strip()) < min_len:
            raise serializers.ValidationError(
                f"Text must be at least {min_len} characters long."
            )
        cleaned = escape(value.strip())
        if len(cleaned) > max_len:
            raise serializers.ValidationError(
                f"Text is too long (max {max_len} characters)."
            )
        if allow_links:
            link_count = len(re.findall(r'https?://', cleaned))
            if link_count > allow_links:
                raise serializers.ValidationError(
                    f"Text contains too many links (max {allow_links})."
                )
        return cleaned

    @staticmethod
    def sanitize_address(value: str, max_len: int = 200) -> str:
        """Sanitize address field."""
        if value:
            return escape(value.strip()[:max_len])
        return value

    @staticmethod
    def sanitize_postal_code(value: str, max_len: int = 20) -> str:
        """Sanitize postal code for international formats."""
        if value:
            cleaned = re.sub(r'[^A-Za-z0-9\s\-]', '', value)
            return cleaned[:max_len]
        return value

    @staticmethod
    def validate_decimal(value: Any, min_val: Decimal = None, max_val: Decimal = None) -> Decimal:
        """Validate and convert to Decimal with range checking."""
        try:
            decimal_val = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            raise serializers.ValidationError("Value must be a valid number.")

        if min_val is not None and decimal_val < min_val:
            raise serializers.ValidationError(f"Value must be at least {min_val}.")
        if max_val is not None and decimal_val > max_val:
            raise serializers.ValidationError(f"Value must not exceed {max_val}.")

        return decimal_val

    @staticmethod
    def validate_password(value: str, min_len: int = 8) -> str:
        """Validate password meets complexity requirements."""
        if not value or len(value) < min_len:
            raise serializers.ValidationError(
                f"Password must be at least {min_len} characters long."
            )
        return value


class PasswordValidator:
    """Validator for password matching and strength."""

    @staticmethod
    def validate_passwords_match(password: str, password_confirm: str) -> str:
        """Ensure two passwords match."""
        if password != password_confirm:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )
        return password


class EmailValidator:
    """Email-specific validators."""

    @staticmethod
    def validate_email_unique(email: str, model_class) -> str:
        """Check if email already exists in model."""
        normalized = email.strip().lower()
        if model_class.objects.filter(email=normalized).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )
        return normalized


class ItemValidator:
    """Validators for JSON item arrays (orders, carts)."""

    @staticmethod
    def validate_items(items: list, max_items: int = 100) -> list:
        """Validate order items structure and values."""
        if not isinstance(items, list) or len(items) == 0:
            raise serializers.ValidationError("Items must be a non-empty array.")

        if len(items) > max_items:
            raise serializers.ValidationError(
                f"Too many items in order (max {max_items})."
            )

        for idx, item in enumerate(items):
            required_fields = ["product_id", "name", "price", "qty"]
            for field in required_fields:
                if field not in item:
                    raise serializers.ValidationError(
                        f"Item {idx}: missing '{field}' field."
                    )

            # Validate quantity
            try:
                qty = int(item["qty"])
                if qty <= 0 or qty > 1000:
                    raise serializers.ValidationError(
                        f"Item {idx}: invalid quantity."
                    )
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    f"Item {idx}: quantity must be a number."
                )

            # Validate price
            try:
                price = Decimal(str(item["price"]))
                if price <= 0 or price > Decimal("1000000"):
                    raise serializers.ValidationError(
                        f"Item {idx}: invalid price."
                    )
            except (InvalidOperation, ValueError, TypeError):
                raise serializers.ValidationError(
                    f"Item {idx}: price must be a valid number."
                )

            # Sanitize item name
            if "name" in item:
                item["name"] = escape(str(item["name"])[:200])

        return items


class SpamValidator:
    """Spam detection and prevention validators."""

    @staticmethod
    def validate_honeypot(honeypot_value: str) -> None:
        """Reject if honeypot field is filled (bot detection)."""
        if honeypot_value and honeypot_value.strip():
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid submission."]}
            )

    @staticmethod
    def validate_no_excessive_links(text: str, max_links: int = 3) -> None:
        """Check if text contains too many suspicious links."""
        link_count = len(re.findall(r'https?://', text))
        if link_count > max_links:
            raise serializers.ValidationError(
                f"Message contains too many links (max {max_links})."
            )

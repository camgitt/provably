"""Tests for custom assertions, register_assertion, and new built-in assertions."""

import pytest

from provably import Expectation, expect, register_assertion


# --- custom() inline assertion ---

def test_custom_pass():
    expect("Please help me").custom(
        "is_polite", lambda r: "please" in r.text.lower()
    )


def test_custom_fail():
    with pytest.raises(AssertionError, match="Custom assertion 'is_polite' returned False"):
        expect("Help me now").custom(
            "is_polite", lambda r: "please" in r.text.lower()
        )


def test_custom_assertion_error_propagates():
    def check(r):
        raise AssertionError("custom failure message")

    with pytest.raises(AssertionError, match="custom failure message"):
        expect("anything").custom("my_check", check)


def test_custom_exception_wrapped():
    def check(r):
        raise ValueError("oops")

    with pytest.raises(AssertionError, match="Custom assertion 'bad' raised ValueError: oops"):
        expect("anything").custom("bad", check)


# --- register_assertion() ---

def test_register_assertion_creates_method():
    def has_greeting(self):
        if "hello" not in self.result.text.lower():
            raise AssertionError("No greeting found")
        return self

    register_assertion("has_greeting", has_greeting)
    expect("Hello there!").has_greeting()

    # Clean up so other tests aren't affected
    delattr(Expectation, "has_greeting")


def test_register_assertion_duplicate_raises():
    with pytest.raises(ValueError, match="attribute already exists"):
        register_assertion("contains", lambda self: self)


# --- not_contains ---

def test_not_contains_pass():
    expect("Hello, world!").not_contains("goodbye")


def test_not_contains_fail():
    with pytest.raises(AssertionError, match="Expected output NOT to contain"):
        expect("Hello, world!").not_contains("world")


def test_not_contains_case_insensitive():
    with pytest.raises(AssertionError, match="Expected output NOT to contain"):
        expect("Hello World").not_contains("hello world", case_sensitive=False)


# --- length_under ---

def test_length_under_pass():
    expect("short").length_under(100)


def test_length_under_fail():
    with pytest.raises(AssertionError, match="Expected output length under"):
        expect("this is a longer string").length_under(5)


def test_length_under_exact_boundary():
    with pytest.raises(AssertionError, match="Expected output length under"):
        expect("abc").length_under(3)  # length == max_chars should fail


# --- length_over ---

def test_length_over_pass():
    expect("this is a longer string").length_over(5)


def test_length_over_fail():
    with pytest.raises(AssertionError, match="Expected output length over"):
        expect("hi").length_over(100)


def test_length_over_exact_boundary():
    with pytest.raises(AssertionError, match="Expected output length over"):
        expect("abc").length_over(3)  # length == min_chars should fail


# --- chaining custom with built-in ---

def test_chain_custom_with_builtin():
    (
        expect("Hello, please help me with testing!")
        .contains("Hello")
        .custom("is_polite", lambda r: "please" in r.text.lower())
        .not_contains("goodbye")
        .length_under(200)
        .length_over(5)
    )

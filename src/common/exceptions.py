"""Exceptions."""


class NoInternetConnexionError(Exception):
    """Raised when connexion to internet fails."""


class NoActionError(Exception):
    """Raised when no action."""


class UidNotAssignedError(Exception):
    """Raised when no uuid is assigned to a plugin."""

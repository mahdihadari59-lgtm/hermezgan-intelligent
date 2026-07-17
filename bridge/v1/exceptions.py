#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
bridge/v1/exceptions.py

HDP Bridge Exceptions
"""

__all__ = [

    "BridgeError",

    "ConnectionError",

    "DatabaseNotFound",

    "InvalidAlias",

    "QueryError",

    "TableNotFound",

    "ColumnNotFound",

    "TransactionError",

]


# ==========================================================
# BASE
# ==========================================================

class BridgeError(Exception):
    """
    Base Bridge Exception.
    """
    pass


# ==========================================================
# CONNECTION
# ==========================================================

class ConnectionError(BridgeError):
    """
    Database connection failed.
    """
    pass


class DatabaseNotFound(ConnectionError):
    """
    Database file does not exist.
    """
    pass


class InvalidAlias(ConnectionError):
    """
    Invalid SQLite alias.
    """
    pass


# ==========================================================
# QUERY
# ==========================================================

class QueryError(BridgeError):
    """
    SQL execution error.
    """
    pass


class TableNotFound(QueryError):
    """
    Table not found.
    """
    pass


class ColumnNotFound(QueryError):
    """
    Column not found.
    """
    pass


# ==========================================================
# TRANSACTION
# ==========================================================

class TransactionError(BridgeError):
    """
    Transaction failed.
    """
    pass


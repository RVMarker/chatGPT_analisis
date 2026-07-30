"""
cache_manager.py

Cache inteligente.

Cada tipo de dato tiene un TTL independiente.
"""

from __future__ import annotations

import time


class CacheManager:

    def __init__(self):

        self.cache = {}

        self.ttl = {

            "price": 60,

            "financials": 86400,

            "news": 1800,

            "macro": 43200,

            "technical": 300,

        }

    # -----------------------------------------------------

    def put(

        self,

        category,

        key,

        value,

    ):

        self.cache[(category, key)] = (

            value,

            time.time(),

        )

    # -----------------------------------------------------

    def get(

        self,

        category,

        key,

    ):

        record = self.cache.get(

            (category, key)

        )

        if record is None:

            return None

        value, created = record

        ttl = self.ttl.get(category, 60)

        if time.time() - created > ttl:

            del self.cache[(category, key)]

            return None

        return value

    # -----------------------------------------------------

    def clear(self):

        self.cache.clear()
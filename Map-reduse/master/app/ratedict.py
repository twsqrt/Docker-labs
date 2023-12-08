from __future__ import annotations

class RateDict(dict):
    def __init__(self, rate: dict = {}):
        self.update(rate)

    def add_rate(self, key, rate: int) -> None:
        if key in self:
            self[key] += rate
        else:
            self[key] = rate
    
    def add_rate_dict(self, rate_dict: dict) -> None:
        for key, rate in rate_dict.items():
            self.add_rate(key, rate)
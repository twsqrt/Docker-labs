from __future__ import annotations
import json

class RateDict(dict):
    def __init__(self, rate: dict = {}):
        self.__rate = rate

    def __len__(self) -> int:
        return len(self.__rate)

    def __contains__(self, key) -> bool:
        return key in self._rate
    
    def add(self, key, rate: int) -> None:
        if key in self.__rate:
            self.__rate[key] += rate
        else:
            self.__rate[key] = rate
    
    def add_dict(self, rate_dict: dict) -> None:
        for key, rate in rate_dict.items():
            self.add(key, rate)
    
    def clear(self) -> None:
        self.__rate.clear()

    def items(self) -> dict:
        return self.__rate.items()
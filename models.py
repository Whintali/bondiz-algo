from dataclasses import dataclass
from typing import TypedDict

class Interests(TypedDict):
    desires: list[str]
    hobbies: list[str]
@dataclass
class FinalStats:
    desires: float # here if we want to add detailled stats
    hobbies: float # same as desires comment 
    total: float 

@dataclass
class UpUser:
    id: int
    interests: Interests | None
    # lastActivity: datetime.datetime TODO rajouter en BDD, sert à éviter de faire un match pour des comptes étant inactif voir si isActive plutôt ?
    # desires : list[str]
    # hobbies : list[str]
    # name: str
    # habits: list[str]
    # age : datetime.date

@dataclass
class Args:
    user_id: int
    weight_jaccard: int = 1
    weight_overlap: int = 1
    weight_hobbies: int = 1
    weight_desires: int = 1


@dataclass
class Result: 
    user_id:int
    stat: FinalStats
from dataclasses import dataclass

# Evol
# @dataclass
# class Interest:
#     interests: list[str]
#     habits: list[str]
#     hobbies: list[str]

@dataclass
class UpUser:
    id: int
    interests: list[str]

@dataclass
class args:
    user_id: int
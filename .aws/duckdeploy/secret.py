from dataclasses import dataclass


@dataclass(frozen=True)
class Secret:
    environment_name: str
    parameter_name: str

    def __post_init__(self):
        if not self.parameter_name.startswith("/duckbot/"):
            raise ValueError(f"parameter must be within the /duckbot/ namespace: {self.parameter_name}")

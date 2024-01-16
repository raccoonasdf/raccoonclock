from .vectorlib import VectorSum

class SpiceKernel:
    def __getitem__(self, target: str) -> VectorSum: ...

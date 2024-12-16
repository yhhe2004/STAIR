
import torch

class Smoother:

    def __init__(
        self, A: torch.Tensor, 
        beta, L: int, aggr: str
    ) -> None:
        self.Adj = A
        self.beta = beta
        self.L = L
        self.aggr = aggr

    def aggregate(self, features: torch.Tensor):
        return self.Adj @ features

    @torch.no_grad()
    def __call__(self, features: torch.Tensor):
        smoothed = features
        if self.aggr == 'neumann':
            norm_correction = 1 - self.beta ** (self.L + 1)     
            for _ in range(self.L):
                features = self.aggregate(features) * self.beta
                smoothed = smoothed + features
            smoothed = smoothed.mul(1 - self.beta).div(norm_correction)
        elif self.aggr == 'momentum':
            for _ in range(self.L):
                smoothed = self.aggregate(smoothed) * self.beta + features * (1 - self.beta)
        elif self.aggr == 'average':
            smoothed = features / (self.L + 1)
            for _ in range(self.L):
                features = self.aggregate(features)
                smoothed += features / (self.L + 1)
        else:
            raise ValueError(f"aggr should be average|neumann|momentum but {self.aggr} received ...")
        return smoothed
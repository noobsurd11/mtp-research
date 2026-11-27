"""Resumable, deterministic training batch streams.

Every training batch is a pure function of (seed, stream id, batch index):

* epoch ``e`` visits the samples in the order ``randperm(n)`` drawn from a
  generator seeded with (seed, stream, e); batch ``k`` of the epoch is the
  ``k``-th slice of ``batch_size`` indices (a partial last slice is dropped);
* every sample carries its own augmentation seed derived from (seed, stream,
  batch index, position in the batch).  Right before the sample is built,
  every Albumentations transform in the dataset is given its own seed derived
  from it (``seed_pipeline``).

One batch is drawn per stream per optimizer step, so the stream position is the
step.  A run resumed at step ``s`` therefore sees exactly the batches an
uninterrupted run sees from step ``s`` on, independent of the number of
DataLoader workers and of the global RNG.

Why every transform gets its *own* seed: ``Compose.set_random_seed(s)`` gives
every child transform the same seed ``s``.  Each transform then draws its
"apply?" coin from an identical generator, so e.g. HorizontalFlip and
VerticalFlip (both p=0.5) always fire together and a single flip never
happens.  The old ``seed_worker`` hit exactly this inside every DataLoader
worker.
"""

from __future__ import annotations

import random
from typing import Any, Iterator

import numpy as np
import torch
from albumentations.core.composition import BaseCompose
from torch.utils.data import DataLoader, Dataset, Sampler


def mix_seed(*ints: int) -> int:
    """A 32-bit seed derived from a tuple of non-negative ints (SeedSequence hashing)."""
    return int(np.random.SeedSequence([int(i) for i in ints]).generate_state(1)[0])


def _set_own_seed(obj: Any, seed: int) -> None:
    """Seed one transform / compose's own generators without propagating to children."""
    obj.seed = seed
    obj.random_generator = np.random.default_rng(seed)
    obj.py_random = random.Random(seed)


def _flatten(compose: BaseCompose) -> list:
    out = [compose]
    for t in compose.transforms:
        out.extend(_flatten(t) if isinstance(t, BaseCompose) else [t])
    return out


def find_composes(obj: Any) -> list[BaseCompose]:
    """All Albumentations composes reachable from a dataset through dataset attributes, in a fixed order."""
    found: list[BaseCompose] = []
    seen: set[int] = set()

    def walk(o: Any) -> None:
        if id(o) in seen:
            return
        seen.add(id(o))
        if isinstance(o, BaseCompose):
            found.append(o)
            return
        if isinstance(o, Dataset):
            for v in vars(o).values():
                if isinstance(v, (BaseCompose, Dataset)):
                    walk(v)

    walk(obj)
    return found


def seed_pipeline(composes: list[BaseCompose], seed: int) -> None:
    """Give every compose and every transform inside it an independent seed derived from ``seed``."""
    items = [x for c in composes for x in _flatten(c)]
    seeds = np.random.SeedSequence(seed).generate_state(len(items))
    for item, s in zip(items, seeds):
        _set_own_seed(item, int(s))


class SeededSampler(Sampler):
    """Infinite sampler yielding ``(index, item_seed)``; see the module docstring."""

    def __init__(self, n: int, batch_size: int, seed: int, stream_id: int, start_batch: int = 0) -> None:
        if n < batch_size:
            raise ValueError(f"dataset of {n} samples is smaller than one batch of {batch_size}")
        self.n, self.bs, self.seed, self.stream, self.start = n, batch_size, seed, stream_id, start_batch
        self.batches_per_epoch = n // batch_size

    def epoch_order(self, epoch: int) -> torch.Tensor:
        g = torch.Generator().manual_seed(mix_seed(self.seed, self.stream, 0, epoch))
        return torch.randperm(self.n, generator=g)

    def __iter__(self) -> Iterator[tuple[int, int]]:
        b = self.start
        epoch, perm = -1, None
        while True:
            e, k = divmod(b, self.batches_per_epoch)
            if e != epoch:
                epoch, perm = e, self.epoch_order(e)
            for j in range(self.bs):
                yield int(perm[k * self.bs + j]), mix_seed(self.seed, self.stream, 1, b, j)
            b += 1


class SeededDataset(Dataset):
    """Wraps a dataset so that ``ds[(idx, seed)]`` reseeds all of its transforms first."""

    def __init__(self, dataset: Dataset) -> None:
        self.dataset = dataset
        self._composes: list[BaseCompose] | None = None

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, key: tuple[int, int]) -> Any:
        idx, seed = key
        if self._composes is None:
            self._composes = find_composes(self.dataset)
        seed_pipeline(self._composes, seed)
        return self.dataset[idx]


class BatchStream:
    """A resumable infinite stream of training batches (``iterate(start_batch)``)."""

    def __init__(self, dataset: Dataset, batch_size: int, seed: int, stream_id: int,
                 num_workers: int = 4, pin_memory: bool = True) -> None:
        self.dataset, self.batch_size, self.seed, self.stream_id = dataset, batch_size, seed, stream_id
        self.num_workers, self.pin_memory = num_workers, pin_memory
        SeededSampler(len(dataset), batch_size, seed, stream_id)  # validates sizes now

    def __len__(self) -> int:
        """Number of samples (not batches)."""
        return len(self.dataset)

    def iterate(self, start_batch: int = 0) -> Iterator[dict]:
        loader = DataLoader(
            SeededDataset(self.dataset),
            batch_size=self.batch_size,
            sampler=SeededSampler(len(self.dataset), self.batch_size, self.seed, self.stream_id, start_batch),
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
            # Own generator: creating the iterator never touches the global torch RNG.
            generator=torch.Generator().manual_seed(self.seed),
            prefetch_factor=4 if self.num_workers > 0 else None,
        )
        return iter(loader)

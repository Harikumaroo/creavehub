"""
CraveHub Pagination Helpers
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from django.db.models import QuerySet


@dataclass
class PaginationParams:
    page: int = 1
    page_size: int = 20
    MAX_PAGE_SIZE: int = field(default=100, init=False, repr=False)

    def __post_init__(self):
        self.page = max(1, int(self.page))
        self.page_size = min(max(1, int(self.page_size)), self.MAX_PAGE_SIZE)

    @classmethod
    def from_request(cls, request) -> "PaginationParams":
        try:
            page = int(request.query_params.get("page", 1))
        except (TypeError, ValueError):
            page = 1
        try:
            page_size = int(request.query_params.get("page_size", 20))
        except (TypeError, ValueError):
            page_size = 20
        return cls(page=page, page_size=page_size)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


@dataclass
class PaginatedResult:
    items: list[Any]
    total_count: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        import math
        return math.ceil(self.total_count / self.page_size) if self.page_size else 1

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1

    def to_meta(self) -> dict:
        return {
            "pagination": {
                "page": self.page,
                "page_size": self.page_size,
                "total_count": self.total_count,
                "total_pages": self.total_pages,
                "has_next": self.has_next,
                "has_previous": self.has_previous,
            }
        }


def paginate_queryset(
    queryset: QuerySet,
    params: PaginationParams,
) -> tuple[QuerySet, int]:
    total_count = queryset.count()
    sliced = queryset[params.offset: params.offset + params.limit]
    return sliced, total_count
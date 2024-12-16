# __init__.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Backends for podcast charts"""

import dataclasses
from typing import ClassVar, Protocol


class PodcastNotFoundError(Exception):
    """Used when the podcast cannot be found on the remote system."""

    pass


class MultiplePodcastsFoundError(Exception):
    """
    Used when a search that requires a single podcast result gives multiple results.
    """

    pass


class ChartFetchError(Exception):
    """
    Used when an attempt to retrieve chart data fails.
    """

    pass


class PodcastSearchError(Exception):
    """
    Used when a query to the itunes web api fails to yield a result.
    """

    pass


class AppleChartFetchError(ChartFetchError):
    """
    Used when an error occurs attempting to fetch Apple chart data.
    """

    pass


class ChartParseError(Exception):
    """
    Used when we can't parse the chart data.
    """

    pass


@dataclasses.dataclass
class PodcastCategory:
    label: str
    remote_id: str


@dataclasses.dataclass
class PodcastData:
    podcast_title: str
    podcast_id: str
    categories: list[PodcastCategory]
    backend_url: str | None


@dataclasses.dataclass
class ChartIdReturnValue:
    """
    Represents the result of fetching a chart id for a given backend
    """

    chart_id: str
    unique_for_country: bool


@dataclasses.dataclass
class ChartPositionData:
    podcast_id: str
    position: int
    podcast_title: str | None = None
    podcast_url: str | None = None


class ChartBackend(Protocol):
    base_url: ClassVar[str]

    async def get_remote_podcast_data(
        self,
        podcast_title: str,
        podcast_rss: str | None = None,
        podcast_id: str | None = None,
    ) -> PodcastData: ...

    async def get_chart_id_for_category(
        self,
        category_id: str,
        country: str | None = None,
    ) -> ChartIdReturnValue: ...

    async def fetch(
        self,
        remote_chart_id: str,
        country: str,
        *,
        filter_to_podcast_ids: list[str] | None,
    ) -> list[ChartPositionData]: ...

# __init__.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""podcast_charts module"""

from podcast_charts.backends import (
    AppleChartFetchError,
    ChartFetchError,
    ChartParseError,
    PodcastSearchError,
)
from podcast_charts.exceptions import (
    ChartImproperlyConfiguredError,
    ChartSourceNotSupportedError,
    ChartStatusInvalidError,
)

__version__ = "0.0.1"

__all__ = [
    "AppleChartFetchError",
    "ChartFetchError",
    "ChartImproperlyConfiguredError",
    "ChartParseError",
    "ChartSourceNotSupportedError",
    "ChartStatusInvalidError",
    "PodcastSearchError",
]

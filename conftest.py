# conftest.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

import pytest

from podcast_charts.backends import PodcastCategory, PodcastData
from podcast_charts.backends.apple import ApplePodcastsChartBackend


@pytest.fixture
def apple_backend() -> ApplePodcastsChartBackend:
    return ApplePodcastsChartBackend()


@pytest.fixture
def ew_podcast_data() -> PodcastData:
    return PodcastData(
        podcast_title="Explorers Wanted",
        podcast_id="1496564284",
        backend_url="https://podcasts.apple.com/us/podcast/explorers-wanted/id1496564284?uo=4",
        categories=[
            PodcastCategory(label="Games", remote_id="1507"),
            PodcastCategory(label="Leisure", remote_id="1502"),
            PodcastCategory(label="Fiction", remote_id="1483"),
            PodcastCategory(label="Science Fiction", remote_id="1485"),
        ],
    )

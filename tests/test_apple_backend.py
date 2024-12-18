# test_apple_backend.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

import httpx
import pytest

from podcast_charts.backends import (
    MultiplePodcastsFoundError,
    PodcastData,
    PodcastNotFoundError,
    PodcastSearchError,
)


def test_form_podcast_data_from_json(apple_backend):
    json_data = {
        "wrapperType": "track",
        "kind": "podcast",
        "collectionId": 1496564284,
        "trackId": 1496564284,
        "artistName": "5d20 Media, LLC",
        "collectionName": "Explorers Wanted",
        "trackName": "Explorers Wanted",
        "collectionCensoredName": "Explorers Wanted",
        "trackCensoredName": "Explorers Wanted",
        "collectionViewUrl": "https://podcasts.apple.com/us/podcast/explorers-wanted/id1496564284?uo=4",
        "feedUrl": "https://feeds.fireside.fm/explorerswanted/rss",
        "trackViewUrl": "https://podcasts.apple.com/us/podcast/explorers-wanted/id1496564284?uo=4",
        "artworkUrl30": "https://is1-ssl.mzstatic.com/image/thumb/Podcasts113/v4/b8/b1/fd/b8b1fdf4-d2dd-8a96-b174-4b89f60cd624/mza_10686513718301075944.jpg/30x30bb.jpg",
        "artworkUrl60": "https://is1-ssl.mzstatic.com/image/thumb/Podcasts113/v4/b8/b1/fd/b8b1fdf4-d2dd-8a96-b174-4b89f60cd624/mza_10686513718301075944.jpg/60x60bb.jpg",
        "artworkUrl100": "https://is1-ssl.mzstatic.com/image/thumb/Podcasts113/v4/b8/b1/fd/b8b1fdf4-d2dd-8a96-b174-4b89f60cd624/mza_10686513718301075944.jpg/100x100bb.jpg",
        "collectionPrice": 0.00,
        "trackPrice": 0.00,
        "collectionHdPrice": 0,
        "releaseDate": "2024-12-11T11:00:00Z",
        "collectionExplicitness": "notExplicit",
        "trackExplicitness": "explicit",
        "trackCount": 256,
        "trackTimeMillis": 3247,
        "country": "USA",
        "currency": "USD",
        "primaryGenreName": "Games",
        "contentAdvisoryRating": "Explicit",
        "artworkUrl600": "https://is1-ssl.mzstatic.com/image/thumb/Podcasts113/v4/b8/b1/fd/b8b1fdf4-d2dd-8a96-b174-4b89f60cd624/mza_10686513718301075944.jpg/600x600bb.jpg",
        "genreIds": ["1507", "26", "1502", "1483", "1485"],
        "genres": ["Games", "Podcasts", "Leisure", "Fiction", "Science Fiction"],
    }
    podcast_data = apple_backend._form_podcast_data_from_itunes_podcast_json(json_data)
    assert isinstance(podcast_data, PodcastData)
    for category in podcast_data.categories:
        assert category.label != "Podcasts"
    assert podcast_data.podcast_title == "Explorers Wanted"
    assert podcast_data.podcast_id == "1496564284"
    assert (
        podcast_data.backend_url
        == "https://podcasts.apple.com/us/podcast/explorers-wanted/id1496564284?uo=4"
    )


@pytest.mark.vcr
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "search_term,podcast_id,podcast_rss,expect_exception,exception_type",
    [
        ("Explorers", None, None, True, MultiplePodcastsFoundError),
        ("Explorers", "jkjdjhfhduiofhd", None, True, PodcastNotFoundError),
        ("897328736jdkljsdkj", None, None, True, PodcastNotFoundError),
        ("Explorers", "1496564284", None, False, None),
        (
            "Explorers",
            None,
            "https://feeds.fireside.fm/explorerswanted/rss",
            False,
            None,
        ),
    ],
)
async def test_get_podcast_data_multiple_results(
    apple_backend,
    search_term,
    podcast_id,
    podcast_rss,
    expect_exception,
    exception_type,
):
    if expect_exception:
        with pytest.raises(exception_type):
            await apple_backend.get_remote_podcast_data(
                podcast_title=search_term,
                podcast_id=podcast_id,
                podcast_rss=podcast_rss,
            )
    else:
        ew_result = await apple_backend.get_remote_podcast_data(
            podcast_title=search_term, podcast_id=podcast_id, podcast_rss=podcast_rss
        )
        assert ew_result.podcast_title == "Explorers Wanted"
        assert ew_result.podcast_id == "1496564284"
        assert (
            ew_result.backend_url
            == "https://podcasts.apple.com/us/podcast/explorers-wanted/id1496564284?uo=4"
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code",
    [
        httpx.codes.INTERNAL_SERVER_ERROR,
        httpx.codes.BAD_REQUEST,
        httpx.codes.UNAUTHORIZED,
        httpx.codes.SERVICE_UNAVAILABLE,
        httpx.codes.NOT_FOUND,
    ],
)
async def test_get_podcast_data_http_error(httpx_mock, apple_backend, status_code):
    httpx_mock.add_response(status_code=status_code)
    with pytest.raises(PodcastSearchError):
        await apple_backend.get_remote_podcast_data(
            podcast_title="Explorers", podcast_id=None, podcast_rss=None
        )


@pytest.mark.vcr
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "genre_id,expected_chart_id",
    [
        ("1485", "6503963783"),  # Science Fiction
        ("1507", "6503973726"),  # Games
    ],
)
async def test_get_podcast_chart_id(apple_backend, genre_id, expected_chart_id):
    chart_id_result = await apple_backend.get_chart_id_for_category(
        category_id=genre_id, country=None
    )
    assert chart_id_result.chart_id == expected_chart_id
    assert not chart_id_result.unique_for_country


@pytest.mark.vcr
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "chart_id,country,limit_to_ids,expected_result_count,top_level_category",
    [
        ("6503963783", "us", [], 60, False),
        ("6503973726", "us", None, 60, False),
        ("6503963783", "ca", None, 60, False),
        ("6503973726", "ca", None, 60, False),
    ],
)
async def test_collect_chart_positions(
    apple_backend,
    chart_id,
    country,
    limit_to_ids,
    expected_result_count,
    top_level_category,
):
    chart_positions = await apple_backend.fetch(
        remote_chart_id=chart_id,
        country=country,
        filter_to_podcast_ids=limit_to_ids,
        remote_chart_id_is_category_id=top_level_category,
    )
    assert len(chart_positions) == expected_result_count

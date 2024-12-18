# apple.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

import logging
from typing import Any

import httpx
from bs4 import BeautifulSoup

from podcast_charts.backends import (
    AppleChartFetchError,
    ChartBackend,
    ChartIdReturnValue,
    ChartParseError,
    ChartPositionData,
    MultiplePodcastsFoundError,
    PodcastCategory,
    PodcastData,
    PodcastNotFoundError,
    PodcastSearchError,
)

logger = logging.getLogger(__name__)


class ApplePodcastsChartBackend(ChartBackend):
    """
    Chart backend for Apple Podcasts.

    Attributes:
        base_url (str): The base URL of the Podcasts webview.
    """

    base_url = "https://podcasts.apple.com"

    @staticmethod
    def _form_podcast_data_from_itunes_podcast_json(
        podcast: dict[str, Any],
    ) -> PodcastData:
        """
        Given a the dict representation of the json response from the iTunes
        Search API, parse the data into a PodcastData object.

        Args:
            podcast (dict[str, Any]): A dict representation of the search API
               response.

        Returns:
            PodcastData: A PodcastData object.
        """
        categories = []
        index_num = 0
        for category_name in podcast["genres"]:
            if category_name != "Podcasts":
                categories.append(
                    PodcastCategory(
                        label=category_name, remote_id=podcast["genreIds"][index_num]
                    )
                )
            index_num += 1
        return PodcastData(
            podcast_title=podcast["trackName"],
            podcast_id=str(podcast["trackId"]),
            categories=categories,
            backend_url=podcast["trackViewUrl"],
        )

    @staticmethod
    def _extract_chart_id_from_soup(soup: BeautifulSoup) -> ChartIdReturnValue:
        """
        Given a BeautifulSoup object of the HTML webview for a category page
        find and return details on where to get the chart data.

        Args:
             soup (BeautifulSoup): A BeautifulSoup object of the HTML webview.

        Returns:
            ChartIdReturnValue: A ChartIdReturnValue object.

        Raises:
            ChartParseError: If the html cannot be parsed successfully.
        """
        h2_elements = soup.find_all("h2")
        if not h2_elements:
            msg = "Could not find header element for search"
            raise ChartParseError(msg)
        for h2_element in h2_elements:
            if (
                "data-testid" in h2_element.attrs.keys()
                and h2_element.attrs["data-testid"] == "header-title"
            ):
                anchor = h2_element.find("a")
                if anchor is None:
                    msg = "Could not find link element to category chart"
                    raise ChartParseError(msg)
                try:
                    chart_url = anchor.attrs["href"]
                except KeyError as ke:
                    msg = "Link element does not contain an href attribute!: {ke}"
                    raise ChartParseError(msg) from ke
                chart_id = chart_url.rsplit("/", maxsplit=1)[1]
                return ChartIdReturnValue(
                    chart_id=chart_id, unique_for_country=False, webview_url=chart_url
                )
        msg = "Could not find any chart category links in results!"
        raise ChartParseError(msg)

    @staticmethod
    def _extract_apple_chart_positions_from_soup(
        soup: BeautifulSoup, podcast_apple_ids: list[str]
    ) -> list[ChartPositionData]:
        """
        Given a BeautifulSoup object of the HTML webview for a chart, return a list
        of podcast chart positions within it.

        Args:
             soup (BeautifulSoup): A BeautifulSoup object of the HTML webview.
             podcast_apple_ids (list[str]): A list of remote ids to limit the
                 results to.

        Returns:
            list[ChartPositionData]: A list of ChartPositionData objects.

        Raises:
            ChartParseError: If the element for the podcast list cannot be found.
        """
        try:
            ul_element = soup.find(class_="shelf-content").ul  # type: ignore
        except AttributeError as ae:
            msg = f"Could not find list element for chart in html: {ae}"
            raise ChartParseError(msg) from ae
        position = 1
        results = []
        for element in ul_element.find_all("li"):  # type: ignore
            link = element.find("a", class_="product-lockup__link")
            if not link:
                logger.error(f"Could not parse podcast at position {position}")
            else:
                podcast_url = str(link["href"])
                podcast_id = podcast_url.rsplit("/id", maxsplit=1)[1]
                if (
                    len(podcast_apple_ids) > 0 and podcast_id in podcast_apple_ids
                ) or len(podcast_apple_ids) == 0:
                    results.append(
                        ChartPositionData(
                            podcast_id=podcast_id,
                            position=position,
                            podcast_url=podcast_url,
                        )
                    )
            position += 1
        return results

    async def get_remote_podcast_data(
        self,
        podcast_title: str,
        podcast_rss: str | None = None,
        podcast_id: str | None = None,
    ) -> PodcastData:
        """
        Attempt to fetch the podcast data from the remote backend.

        Args:
            podcast_title (str): The title of the podcast.
            podcast_rss (str | None): The RSS URL of the podcast to use with
               disambiguation.
            podcast_id (str | None): The remote id fo the podcast if known.

        Returns:
            PodcastData: The podcast data from the remote system.

        Raises:
            PodcastNotFoundError: If the remote podcast could not be found.
            MultiplePodcastsFoundError: If multiple ambiguous results were found.
            ItunesSearchError: If the iTunes search API responds with an error.
        """
        itunes_search_url = "https://itunes.apple.com/search"
        headers = {"Accept": "application/json"}
        params = {
            "term": podcast_title,
            "media": "podcast",
            "entity": "podcast",
            "attribute": "titleTerm",
        }
        try:
            async with httpx.AsyncClient(headers=headers) as client:
                response = await client.get(itunes_search_url, params=params)
                response.raise_for_status()
        except httpx.HTTPStatusError as hse:
            msg = f"Received invalid status code from ITunes search API: {hse}"
            raise PodcastSearchError(msg) from hse
        data = response.json()
        if data["resultCount"] == 0:
            msg = "Received 0 results for podcast!"
            raise PodcastNotFoundError(msg)
        elif data["resultCount"] == 1:
            return self._form_podcast_data_from_itunes_podcast_json(data["results"][0])
        elif data["resultCount"] > 1 and (podcast_rss is None and podcast_id is None):
            msg = (
                f"Received {data['resultCount']} records from remote server, but no "
                f"rss feed or id is available to narrow results."
            )
            raise MultiplePodcastsFoundError(msg)
        else:
            for podcast in data["results"]:
                if (
                    podcast_id is not None and str(podcast["trackId"]) == podcast_id
                ) or (podcast_rss is not None and podcast["feedUrl"] == podcast_rss):
                    return self._form_podcast_data_from_itunes_podcast_json(podcast)
            msg = "Podcast was not found in results!"
            raise PodcastNotFoundError(msg)

    async def get_chart_id_for_category(
        self,
        category_id: str,
        country: str | None = None,  # noqa: ARG002
    ) -> ChartIdReturnValue:
        """
        Attempt to fetch the chart id for a given category from the remote backend.

        Args:
            category_id (str): The category id to fetch the chart id for.
            country (str | None): The country code to fetch the chart id for. Apple's
                chart ids are consistent across countries so this is ignored.

        Returns:
            ChartIdReturnValue: The chart id for the given category.

        Raises:
            AppleChartFetchError: If the information cannot be retrieved.
        """
        category_url = f"{self.base_url}/us/genre/{category_id}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(category_url)
                response.raise_for_status()
            except httpx.HTTPStatusError as hse:
                msg = f"Received invalid status code from Apple Podcasts: {hse}"
                raise AppleChartFetchError(msg) from hse
            category_soup = BeautifulSoup(response.text)
            try:
                chart_id = self._extract_chart_id_from_soup(category_soup)
            except ChartParseError as cpe:
                msg = str(cpe)
                raise AppleChartFetchError(msg) from cpe
            return chart_id

    async def fetch(
        self,
        remote_chart_id: str,
        country: str,
        *,
        filter_to_podcast_ids: list[str] | None,
        remote_chart_id_is_category_id: bool = False,
    ) -> list[ChartPositionData]:
        """
        Fetch the chart data from Apple Podcasts.

        Args:
            remote_chart_id (str): The remote chart id to fetch the data from.
            country (str): The country code to use for fetching the market data.
            filter_to_podcast_ids (list[str] | None): An optional list of podcast ids to
                filter the results against.
            remote_chart_id_is_category_id (bool): Whether the remote id is a category
                as opposed to a chart id.

        Returns:
            list[ChartPositionData]: The chart positions retrieved from Apple.

        Raises:
            AppleChartFetchError: If the remote chart could not be fetched.
            NotImplementedError: If the chart request is not implemented.
        """
        if country == "all":
            msg = "Getting worldwide charts via Apple Podcasts is not supported."
            raise NotImplementedError(msg)
        if filter_to_podcast_ids is None:
            filter_to_podcast_ids = []
        if remote_chart_id_is_category_id:
            url = f"{self.base_url}/{country}/charts?genre={remote_chart_id}"
        else:
            url = f"{self.base_url}/{country}/room/{remote_chart_id}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
            except httpx.HTTPStatusError as hse:
                msg = f"Received invalid status code from Apple Podcasts: {hse}"
                raise AppleChartFetchError(msg) from hse
        chart_soup = BeautifulSoup(response.text)
        chart_positions = self._extract_apple_chart_positions_from_soup(
            chart_soup, podcast_apple_ids=filter_to_podcast_ids
        )
        return chart_positions

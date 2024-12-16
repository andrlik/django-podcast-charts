# models.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Models for podcast_charts"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from podcast_charts import ChartImproperlyConfiguredError, ChartSourceNotSupportedError
from podcast_charts.backends import ChartBackend
from podcast_charts.backends.apple import ApplePodcastsChartBackend

MAX_CHART_RETRIES = (
    settings.CHART_FETCH_MAX_RETRIES
    if hasattr(settings, "CHART_FETCH_MAX_RETRIES")
    and isinstance(settings.CHART_FETCH_MAX_RETRIES, int)
    else 3
)


class SourceBackendChoices(models.TextChoices):
    """Source backend choices"""

    APPLE = "apple", _("Apple Podcasts")
    SPOTIFY = "spotify", _("Spotify Podcasts")


ENABLED_SOURCES = (SourceBackendChoices.APPLE,)


SOURCE_BACKEND_MAPPING = {
    SourceBackendChoices.APPLE.value: ApplePodcastsChartBackend,
}


def get_chart_backend(source_backend_key: tuple[str, str]) -> ChartBackend:
    """
    Given an option from SourceBackendChoices, return the mapped backend class.

    Args:
        source_backend_key (tuple[str, str]): Source backend to use from
            SourceBackendChoices.
    Returns:
        ChartBackend: A chart backend instance.
    Raises:
        ChartBackendNotSupportedError: If source_backend_key is not supported.
    """
    if source_backend_key not in ENABLED_SOURCES:
        msg = f"{source_backend_key} is not an enabled source!"
        raise ChartSourceNotSupportedError(msg)
    if source_backend_key not in SOURCE_BACKEND_MAPPING.keys():
        msg = f"{source_backend_key} is not a configured source!"
        raise ChartSourceNotSupportedError(msg)
    return SOURCE_BACKEND_MAPPING[source_backend_key]()


class FetchStatusChoices(models.TextChoices):
    PENDING = "pend", _("Pending")
    FETCHING = "fetch", _("In progress...")
    DONE = "done", _("Done")
    ERROR = "error", _("Error")
    RETRY = "retry", _("Pending Retry")


class TimeStampedModel(models.Model):
    """
    A base model that automatically created created and modified timestamps.

    Attributes:
        created (datetime.datetime): When the record was created.
        modified (datetime.datetime): When the record was last modified.
    """

    created = models.DateTimeField(
        auto_now_add=True, help_text=_("When this instance was created.")
    )
    modified = models.DateTimeField(
        auto_now=True, help_text=_("When this instance was last modified.")
    )

    class Meta:
        abstract = True


class ChartCountry(TimeStampedModel):
    """
    Provides a base level object that can be used to enable/disable countries for
    particular charts.

    We actually use a TextChoices for the details so that we can localize the name.

    Attributes:
        id (int): The id of this country.
        country (str): The country code and localized name via
            get_country_display().
        enabled (bool): Whether or not this country is enabled globally.
        created (datetime.datetime): The datetime the country was created.
        modified (datetime.datetime): The datetime the country was last modified.
    """

    id: int
    country = models.CharField(
        max_length=5, unique=True, help_text=_("The country code/name")
    )
    enabled = models.BooleanField(
        default=True,
        help_text=_("Whether this country is enabled globally for charts."),
    )

    class Meta:
        ordering = ("country",)

    def __str__(self) -> str:  # no cov
        return f"{self.get_country_display()} ({self.country})"  # type: ignore


class ChartCategory(TimeStampedModel):
    """
    The category or genre for a given chart. Labels may vary per source so similar
    chart categories may vary per source. Most charts follow the iTunes categories
    but this is kept generic in case of new implementations arising.

    Attributes:
        id (int): The id of this category.
        label (str): The label of the category.
        parent_label (ChartCategory): The parent category, if applicable.
        created (datetime.datetime): The datetime the category was created.
        modified (datetime.datetime): The datetime the category was last modified.
    """

    id: int
    label = models.CharField(
        max_length=200, unique=True, help_text=_("The label of the category.")
    )
    parent_label = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=_("The parent category if applicable."),
    )

    class Meta:
        ordering = ("parent_label__label, label",)

    def __str__(self) -> str:  # no cov
        return self.label


class ChartSourceCategory(TimeStampedModel):
    """
    The category record for a given chart source backend with accompanying remote id.

    Attributes:
        id (int): The id of this category/source link.
        chart_source (str): The chart source backend.
        chart_category (ChartCategory): The related chart category.
        chart_source_category_remote_id (str): The remote id for the chart backend for
            this category as a string.
        created (datetime.datetime): The datetime the category was created.
        modified (datetime.datetime): The datetime the category was last modified.
    """

    id: int
    chart_source = models.CharField(
        max_length=50,
        choices=SourceBackendChoices,
        default=SourceBackendChoices.APPLE,
        db_index=True,
        help_text=_("Chart source identifier"),
    )
    chart_category = models.ForeignKey(
        ChartCategory,
        on_delete=models.CASCADE,
        db_index=True,
        help_text=_("Chart category for source"),
    )
    chart_source_category_remote_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text=_("The remote id used by the chart source"),
    )

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(
                fields=["chart_source", "chart_category"]
            )
        ]

    def __str__(self) -> str:  # no cov
        return f"{self.get_chart_source_display()} - {self.chart_category}"  # type: ignore


class PodcastChart(TimeStampedModel):
    """
    Defines an overall chart configuration.

    Attributes:
        id (int): The id of this podcast chart.
        chart_source (str): The chart source backend.
        chart_source_category (ChartSourceCategory): The related chart category.
        chart_remote_id (str | none): The remote id for this chart.
        enabled_countries (ChartCountry): A list of all the enabled countries.
        enabled (bool): Whether or not this podcast chart is enabled.
        created (datetime.datetime): The datetime the podcast chart was created.
        modified (datetime.datetime): The datetime the podcast chart was last modified.
    """

    id: int
    chart_source = models.CharField(
        max_length=50,
        db_index=True,
        choices=SourceBackendChoices,
        default=SourceBackendChoices.APPLE,
        help_text=_("Source backend for this chart."),
    )
    chart_source_category = models.ForeignKey(
        ChartSourceCategory,
        on_delete=models.CASCADE,
        help_text=_("Chart source category for this chart."),
    )
    chart_remote_id = models.CharField(
        null=True,
        blank=True,
        max_length=100,
        help_text=_("Remote id for this chart type. Null if unique per country"),
    )
    enabled_countries = models.ManyToManyField(
        ChartCountry, help_text=_("Countries enabled for this Chart.")
    )
    enabled = models.BooleanField(
        default=True, help_text=_("Whether this chart is enabled.")
    )

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(
                fields=["chart_source_category", "chart_source"]
            )
        ]

    def __str__(self) -> str:  # no cov
        return (
            f"{self.get_chart_source_display()} - Chart for "  # type: ignore
            f"{self.chart_source_category.chart_category}"
        )


class PodcastChartVersion(TimeStampedModel):
    """
    A given version of the chart rankings for a specific country and date.

    Attributes:
        id (int): The id of this version.
        podcast_chart (PodcastChart): The podcast chart it is a version of.
        country (ChartCountry): The country this version is for.
        chart_date (datetime.date): The date when this chart data was sampled.
        fetch_status (str): The fetch status for this chart's data. One of: "pend",
            "fetch", "done", "error", "retry".
        created (datetime.datetime): The datetime this version was created.
        modified (datetime.datetime): The datetime this version was last modified.
    """

    id: int
    podcast_chart = models.ForeignKey(
        PodcastChart,
        on_delete=models.CASCADE,
        help_text=_("The podcast chart this is a version of."),
    )
    country = models.ForeignKey(
        ChartCountry,
        on_delete=models.CASCADE,
        help_text=_("The country this chart is for."),
    )
    chart_remote_id = models.CharField(
        max_length=100, null=True, blank=True, help_text=_("Remote chart id")
    )
    chart_date = models.DateField(help_text=_("The date this chart ranking represents"))
    fetch_status = models.CharField(
        max_length=20, db_index=True, help_text=_("The fetch status of the chart data.")
    )
    num_retries = models.PositiveIntegerField(
        default=0, help_text=_("How many retries have been attempted.")
    )

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(
                fields=["podcast_chart", "country", "chart_date"]
            )
        ]

    def __str__(self) -> str:  # no cov
        return f"{self.podcast_chart} - {self.country} - {self.chart_date}"

    def get_remote_chart_id(self) -> str:
        if self.chart_remote_id is not None:
            return self.chart_remote_id
        elif self.podcast_chart.chart_remote_id is not None:
            return self.podcast_chart.chart_remote_id
        else:
            msg = "Both the Chart Version and the parent chart are missing a remote id!"
            raise ChartImproperlyConfiguredError(msg)

    def can_retry(self) -> bool:
        """
        Is the chart in a state where a retry can begin and are existing
        retries within allowed bounds?

        Returns:
            bool: Whether the chart fetch can be retried.
        """
        return (
            self.fetch_status not in ["error", "pend"]
            and self.num_retries < MAX_CHART_RETRIES
        )


class PodcastChartPodcastIdentifier(TimeStampedModel):
    """
    The remote identifier used by the source backend for a given podcast.

    Attributes:
        id (int): The id of this podcast.
        podcast_title (str): The podcast title as reported by the backend.
        chart_source (str): The source backend for the identifier.
        chart_source_podcast_id (str): The remote id for the podcast.
        chart_source_podcast_url (str): The remote url reported for the podcast source
            backend.
        created (datetime.datetime): The datetime this podcast data was created.
        modified (datetime.datetime): The datetime this podcast data was last modified.
    """

    id: int
    podcast_title = models.CharField(
        max_length=250,
        help_text=_("The podcast title as displayed on the remote chart."),
    )
    chart_source = models.CharField(
        max_length=10,
        db_index=True,
        choices=SourceBackendChoices,
        help_text=_("Chart source backend."),
    )
    chart_source_podcast_id = models.CharField(
        max_length=100,
        db_index=True,
        help_text=_("The remote id used by the chart source for this podcast."),
    )
    chart_source_podcast_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        help_text=_(
            "The remote URL provided by the backend for the pocast in its directory."
        ),
    )

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(
                fields=["chart_source", "chart_source_podcast_id"]
            )
        ]

    def __str__(self) -> str:  # no cov
        return f"{self.chart_source} - {self.chart_source_podcast_id}"


class PodcastChartPosition(TimeStampedModel):
    """
    A given ranking for a specific chart version.

    Attributes:
        id (int): The id of this position record.
        chart_version (PodcastChartVersion): The podcast chart version to which this
            rank belongs.
        podcast_identifier (PodcastChartPodcastIdentifier): The podcast chart identifier
        position (int): The numerical rank in the chart.
        created (datetime.datetime): The datetime the position was created.
        modified (datetime.datetime): The datetime the position was last modified.
    """

    id: int
    chart_version = models.ForeignKey(
        PodcastChartVersion,
        on_delete=models.CASCADE,
        help_text=_("The chart version to which this position belongs."),
    )
    podcast_identifier = models.ForeignKey(
        PodcastChartPodcastIdentifier,
        on_delete=models.CASCADE,
        help_text=_("The podcast identifier that this position refers to."),
    )
    position = models.PositiveIntegerField(
        db_index=True, help_text=_("The podcast position on the chart.")
    )

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(fields=["chart_version", "position"])
        ]

    def __str__(self) -> str:  # no cov
        return (
            f"{self.chart_version} - Rank {self.position}: "
            f"{self.podcast_identifier.podcast_title}"
        )

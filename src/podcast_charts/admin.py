# admin.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Admin registration objects for podcast_charts"""

from django.contrib import admin

from podcast_charts.models import (
    ChartCategory,
    ChartCountry,
    ChartSourceCategory,
    PodcastChart,
    PodcastChartPodcastIdentifier,
    PodcastChartPosition,
    PodcastChartVersion,
)


@admin.register(ChartCountry)
class ChartCountryAdmin(admin.ModelAdmin):
    pass


@admin.register(ChartCategory)
class ChartCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(ChartSourceCategory)
class ChartSourceCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(PodcastChart)
class PodcastChartAdmin(admin.ModelAdmin):
    pass


@admin.register(PodcastChartVersion)
class PodcastChartVersionAdmin(admin.ModelAdmin):
    pass


@admin.register(PodcastChartPosition)
class PodcastChartPositionAdmin(admin.ModelAdmin):
    pass


@admin.register(PodcastChartPodcastIdentifier)
class PodcastChartPodcastIdentifierAdmin(admin.ModelAdmin):
    pass

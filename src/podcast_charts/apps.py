# apps.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PodcastChartsConfig(AppConfig):
    """App config for podcast_charts."""

    name = "podcast_charts"
    verbose_name = _("Podcast Charts")
    default_auto_field = "django.db.models.AutoField"

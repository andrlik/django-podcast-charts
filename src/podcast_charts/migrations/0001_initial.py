# Generated by Django 5.1.4 on 2024-12-16 21:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ChartCountry",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, help_text="When this instance was created."
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, help_text="When this instance was last modified."
                    ),
                ),
                (
                    "country",
                    models.CharField(
                        help_text="The country code/name", max_length=5, unique=True
                    ),
                ),
                (
                    "enabled",
                    models.BooleanField(
                        default=True,
                        help_text="Whether this country is enabled globally for charts.",
                    ),
                ),
            ],
            options={
                "ordering": ("country",),
            },
        ),
        migrations.CreateModel(
            name="ChartCategory",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, help_text="When this instance was created."
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, help_text="When this instance was last modified."
                    ),
                ),
                (
                    "label",
                    models.CharField(
                        help_text="The label of the category.",
                        max_length=200,
                        unique=True,
                    ),
                ),
                (
                    "parent_label",
                    models.ForeignKey(
                        blank=True,
                        help_text="The parent category if applicable.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="podcast_charts.chartcategory",
                    ),
                ),
            ],
            options={
                "ordering": ("parent_label__label", "label"),
            },
        ),
        migrations.CreateModel(
            name="ChartSourceCategory",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, help_text="When this instance was created."
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, help_text="When this instance was last modified."
                    ),
                ),
                (
                    "chart_source",
                    models.CharField(
                        choices=[
                            ("apple", "Apple Podcasts"),
                            ("spotify", "Spotify Podcasts"),
                        ],
                        db_index=True,
                        default="apple",
                        help_text="Chart source identifier",
                        max_length=50,
                    ),
                ),
                (
                    "chart_source_category_remote_id",
                    models.CharField(
                        blank=True,
                        help_text="The remote id used by the chart source",
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "chart_category",
                    models.ForeignKey(
                        help_text="Chart category for source",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="podcast_charts.chartcategory",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PodcastChart",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, help_text="When this instance was created."
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, help_text="When this instance was last modified."
                    ),
                ),
                (
                    "chart_source",
                    models.CharField(
                        choices=[
                            ("apple", "Apple Podcasts"),
                            ("spotify", "Spotify Podcasts"),
                        ],
                        db_index=True,
                        default="apple",
                        help_text="Source backend for this chart.",
                        max_length=50,
                    ),
                ),
                (
                    "chart_remote_id",
                    models.CharField(
                        blank=True,
                        help_text="Remote id for this chart type. Null if unique per country",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "enabled",
                    models.BooleanField(
                        default=True, help_text="Whether this chart is enabled."
                    ),
                ),
                (
                    "chart_source_category",
                    models.ForeignKey(
                        help_text="Chart source category for this chart.",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="podcast_charts.chartsourcecategory",
                    ),
                ),
                (
                    "enabled_countries",
                    models.ManyToManyField(
                        help_text="Countries enabled for this Chart.",
                        to="podcast_charts.chartcountry",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PodcastChartPodcastIdentifier",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, help_text="When this instance was created."
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, help_text="When this instance was last modified."
                    ),
                ),
                (
                    "podcast_title",
                    models.CharField(
                        help_text="The podcast title as displayed on the remote chart.",
                        max_length=250,
                    ),
                ),
                (
                    "chart_source",
                    models.CharField(
                        choices=[
                            ("apple", "Apple Podcasts"),
                            ("spotify", "Spotify Podcasts"),
                        ],
                        db_index=True,
                        help_text="Chart source backend.",
                        max_length=10,
                    ),
                ),
                (
                    "chart_source_podcast_id",
                    models.CharField(
                        db_index=True,
                        help_text="The remote id used by the chart source for this podcast.",
                        max_length=100,
                    ),
                ),
                (
                    "chart_source_podcast_url",
                    models.URLField(
                        blank=True,
                        help_text="The remote URL provided by the backend for the pocast in its directory.",
                        max_length=500,
                        null=True,
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("chart_source", "chart_source_podcast_id"),
                        name="unique_source_podcast_id",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="PodcastChartVersion",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, help_text="When this instance was created."
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, help_text="When this instance was last modified."
                    ),
                ),
                (
                    "chart_remote_id",
                    models.CharField(
                        blank=True,
                        help_text="Remote chart id",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "chart_date",
                    models.DateField(
                        help_text="The date this chart ranking represents"
                    ),
                ),
                (
                    "fetch_status",
                    models.CharField(
                        db_index=True,
                        help_text="The fetch status of the chart data.",
                        max_length=20,
                    ),
                ),
                (
                    "num_retries",
                    models.PositiveIntegerField(
                        default=0, help_text="How many retries have been attempted."
                    ),
                ),
                (
                    "country",
                    models.ForeignKey(
                        help_text="The country this chart is for.",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="podcast_charts.chartcountry",
                    ),
                ),
                (
                    "podcast_chart",
                    models.ForeignKey(
                        help_text="The podcast chart this is a version of.",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="podcast_charts.podcastchart",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PodcastChartPosition",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, help_text="When this instance was created."
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, help_text="When this instance was last modified."
                    ),
                ),
                (
                    "position",
                    models.PositiveIntegerField(
                        db_index=True, help_text="The podcast position on the chart."
                    ),
                ),
                (
                    "podcast_identifier",
                    models.ForeignKey(
                        help_text="The podcast identifier that this position refers to.",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="podcast_charts.podcastchartpodcastidentifier",
                    ),
                ),
                (
                    "chart_version",
                    models.ForeignKey(
                        help_text="The chart version to which this position belongs.",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="podcast_charts.podcastchartversion",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="chartsourcecategory",
            constraint=models.UniqueConstraint(
                fields=("chart_source", "chart_category"),
                name="unique_chart_source_category",
            ),
        ),
        migrations.AddConstraint(
            model_name="podcastchart",
            constraint=models.UniqueConstraint(
                fields=("chart_source_category", "chart_source"),
                name="unique_chart_for_source",
            ),
        ),
        migrations.AddConstraint(
            model_name="podcastchartversion",
            constraint=models.UniqueConstraint(
                fields=("podcast_chart", "country", "chart_date"),
                name="unique_chart_version_for_chart_country",
            ),
        ),
        migrations.AddConstraint(
            model_name="podcastchartposition",
            constraint=models.UniqueConstraint(
                fields=("chart_version", "position"),
                name="unique_position_for_chart_version",
            ),
        ),
    ]
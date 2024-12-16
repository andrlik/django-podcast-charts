# Django Podcast Charts

A Django app for tracking podcast charts. **WIP: Not ready for use!**

[![PyPI](https://img.shields.io/pypi/v/django-podcast-charts)](https://pypi.org/project/django-podcast-charts/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-podcast-charts)
![PyPI - Versions from Framework Classifiers](https://img.shields.io/pypi/frameworkversions/django/django-podcast-charts)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/andrlik/django-podcast-charts/blob/main/.pre-commit-config.yaml)
[![License](https://img.shields.io/github/license/andrlik/django-podcast-charts)](https://github.com/andrlik/django-podcast-charts/blob/main/LICENSE)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)
[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/andrlik/django-podcast-charts/releases)
![Test results](https://github.com/andrlik/django-podcast-charts/actions/workflows/ci.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/andrlik/django-podcast-charts/badge.svg?branch=main)](https://coveralls.io/github/andrlik/django-podcast-charts?branch=main)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://andrlik.github.io/django-podcast-charts/)

This application provides a means to keep track of current podcast chart rankings from various backends.
When an official API is provided, it is used, otherwise it will attempt to scrape this information from
available web views.

You can configure this to check as many or as few charts as you would like. Keep in mind that tracking all
charts and countries will result in **a lot** of database entries. This app will attempt to do client-based rate
limiting so long as you ensure you only call chart tracking through the dedicated task functions.

Models are kept light so that you can enrich them with dedicated types such as those found in [django-podcast-analyzer](https://github.com/andrlik/django-podcast-analyzer).

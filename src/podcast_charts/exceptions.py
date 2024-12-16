# exceptions.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Exception classes for podcast charts"""


class ChartImproperlyConfiguredError(Exception):
    """
    Used when a chart is missing necessary data or is configured in an invalid manner.
    """

    pass


class ChartSourceNotSupportedError(NotImplementedError):
    """
    Raised when a given chart source is not supported.
    """

    pass


class ChartStatusInvalidError(Exception):
    """
    Raised when a chart status does not support the requested action.
    """

    pass

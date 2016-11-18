# Copyright 2016 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Actions on a pool's cache.
"""

from __future__ import print_function

from stratisd_client_dbus import Manager
from stratisd_client_dbus import Pool
from stratisd_client_dbus import StratisdErrorsGen
from stratisd_client_dbus import StratisdRaidGen
from stratisd_client_dbus import get_object

from .._errors import StratisCliRuntimeError
from .._errors import StratisCliUnimplementedError
from .._errors import StratisCliValueError

from .._constants import REDUNDANCY
from .._constants import TOP_OBJECT

from ._misc import get_pool

_MN = Manager.MethodNames
_PN = Pool.MethodNames

class CacheActions(object):
    """
    Actions on a pool's cache.
    """

    @staticmethod
    def add_devices(namespace):
        """
        Add devices to a cache.
        """
        # pylint: disable=unused-argument
        raise StratisCliUnimplementedError(
           'Not sure how to add a device to an already existing cache.'
        )


    @staticmethod
    def create_cache(namespace):
        """
        Create cache for an existing pool.
        """
        try:
            redundancy = REDUNDANCY.get(namespace.redundancy)
        except KeyError:
            raise StratisCliValueError(
               namespace.redundancy,
               "namespace.redundancy",
               "has no corresponding value"
            )

        stratisd_redundancies = StratisdRaidGen.get_object()
        try:
            redundancy_number = getattr(stratisd_redundancies, redundancy)
        except AttributeError:
            raise StratisCliValueError(
               namespace.redundancy,
               "namespace.redundancy",
               "has no corresponding value"
            )

        pool_object = get_pool(get_object(TOP_OBJECT), namespace.pool)
        (_, rc, message) = Pool.callMethod(
           pool_object,
           _PN.AddCacheDevs,
           namespace.device,
           redundancy_number
        )
        if rc != StratisdErrorsGen.get_object().OK:
            raise StratisCliRuntimeError(rc, message)

        return

    @staticmethod
    def list_cache(namespace):
        """
        List information about the cache belonging to a pool.
        """
        proxy = get_object(TOP_OBJECT)
        (pool_object_path, rc, message) = \
            Manager.callMethod(proxy, _MN.GetPoolObjectPath, namespace.pool)
        if rc != 0:
            return (rc, message)

        pool_object = get_object(pool_object_path)
        (result, rc, message) = Pool.callMethod(pool_object, _PN.ListCacheDevs)
        if rc != 0:
            return (rc, message)

        for item in result:
            print(item)

        return (rc, message)

    @staticmethod
    def remove_device(namespace):
        """
        Remove a device from the given pool.
        """
        proxy = get_object(TOP_OBJECT)
        (pool_object_path, rc, message) = \
            Manager.callMethod(proxy, _MN.GetPoolObjectPath, namespace.pool)
        if rc != 0:
            return (rc, message)

        pool_object = get_object(pool_object_path)
        return Pool.callMethod(pool_object, _PN.RemoveCacheDevs)

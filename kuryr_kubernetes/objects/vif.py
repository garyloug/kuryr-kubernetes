#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_versionedobjects import base as obj_base
from oslo_versionedobjects import fields as obj_fields

from os_vif.objects import vif as obj_osvif


@obj_base.VersionedObjectRegistry.register
class VIFVlanNested(obj_osvif.VIFBase):
    # This is OVO based vlan vif.

    VERSION = '1.0'

    fields = {
        # Name of the device to create
        'vif_name': obj_fields.StringField(),
        # vlan ID allocated to this vif
        'vlan_id': obj_fields.IntegerField()
    }


@obj_base.VersionedObjectRegistry.register
class VIFMacvlanNested(obj_osvif.VIFBase):
    # This is OVO based macvlan vif.

    VERSION = '1.0'

    fields = {
        # Name of the device to create
        'vif_name': obj_fields.StringField(),
    }


@obj_base.VersionedObjectRegistry.register
class VIFDpdk(obj_osvif.VIFBase):
    # DPDK

    VERSION = '1.0'

    fields = {
        # Specify whether this vif requires L3 setup
        'l3_setup': obj_fields.BooleanField(),
        # PCI info of the device
        'pci_address': obj_fields.StringField(),
        # Name of the driver the device was previously bound to; it makes
        # the controller driver agnostic (virtio, sr-iov, etc.)
        'dev_driver': obj_fields.StringField(),
        'selflink': obj_fields.StringField(),
        'resourceversion': obj_fields.StringField()
    }

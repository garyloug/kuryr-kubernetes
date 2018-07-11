# Copyright (c) 2018 RedHat, Inc.
#  All Rights Reserved.
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

from oslo_log import log as logging
from oslo_serialization import jsonutils

from kuryr_kubernetes import clients
from kuryr_kubernetes import constants
from kuryr_kubernetes.controller.drivers import base
from kuryr_kubernetes.controller.drivers import default_subnet
from kuryr_kubernetes import exceptions

LOG = logging.getLogger(__name__)


class NoopMultiVIFDriver(base.MultiVIFDriver):

    def request_additional_vifs(
            self, pod, project_id, security_groups):
        return []


class NPWGMultiVIFDriver(base.MultiVIFDriver):
    def __init__(self):
        super(NPWGMultiVIFDriver, self).__init__()
        self._drv_vif_pool = base.VIFPoolDriver.get_instance(
            driver_alias='multi_pool')
        self._drv_vif_pool.set_vif_driver()

    def request_additional_vifs(self, pod, project_id, security_groups):
        vifs = []
        networks = self._get_networks(pod)
        if not networks:
            return vifs

        kubernetes = clients.get_kubernetes_client()
        namespace = pod['metadata']['namespace']

        for network in networks:
            if 'name' not in network:
                raise exceptions.InvalidKuryrNetworkAnnotation()

            if 'namespace' in network:
                namespace = network['namespace']

            try:
                url = '%s/namespaces/%s/networks/%s' % (
                    constants.K8S_API_NPWG_CRD, namespace, network['name'])
                net_crd = kubernetes.get(url)
            except exceptions.K8sClientException:
                LOG.exception("Kubernetes Client Exception")
                raise

            config = jsonutils.loads(net_crd['metadata']['annotations']
                                     ['openstack.org/kuryr-config'])
            subnet_id = config[constants.K8S_ANNOTATION_NPWG_CRD_SUBNET_ID]
            subnet = {subnet_id: default_subnet._get_subnet(subnet_id)}
            vif_drv = None
            if constants.K8S_ANNOTATION_NPWG_CRD_DRIVER_TYPE not in config:
                vif_drv = self._drv_vif_pool
            else:
                alias = config[constants.K8S_ANNOTATION_NPWG_CRD_DRIVER_TYPE]
                vif_drv = base.PodVIFDriver.get_instance(
                    driver_alias=alias)
            vif = vif_drv.request_vif(pod, project_id, subnet, security_groups)

            if vif:
                vifs.append(vif)
        return vifs

    def _get_networks(self, pod):
        networks = []
        try:
            annotations = pod['metadata']['annotations']
            networks_annotation = \
                annotations[constants.K8S_ANNOTATION_NPWG_NETWORK]
        except KeyError:
            return []

        try:
            networks = jsonutils.loads(networks_annotation)
        except ValueError:
            net_list = networks_annotation.split(',')
            for net in net_list:
                l = net.split('/')
                if len(l) == 1:
                    networks.append({'name': l[0]})
                elif len(l) == 2:
                    networks.append({'namespace': l[0], 'name': l[1]})
                else:
                    raise exceptions.InvalidKuryrNetworkAnnotation()

        return networks

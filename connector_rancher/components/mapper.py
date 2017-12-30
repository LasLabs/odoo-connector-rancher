# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import dateutil.parser

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.components.mapper import mapping, only_create


@mapping
def config_serialized(self, record):
    """Return a serialized configuration for import."""

    config_external = record.get('launchConfig') or record
    mib = self.env.ref('product_uom_technology.product_uom_mib')
    options_general = self.env['infrastructure.option']
    options_system = self.env['infrastructure.option.system']

    options_log = options_general.get_or_create_bulk(
        config_external['logConfig'].get('config', {}).items(),
    )
    options_volume = options_system.get_or_create_bulk(
        v.split(':') for v in config_external.get('dataVolumes') or []
    )
    options_device = options_system.get_or_create_bulk(
        d.split(':') for d in config_external.get('devices') or []
    )
    options_labels = options_general.get_or_create_bulk(
        config_external.get('labels', {}).items(),
    )

    options_port = []
    for port_string in config_external.get('ports') or []:
        protocol = False
        internal, external = port_string.split(':')
        if '/' in external:
            external, protocol = external.split('/')
        options_port.append({
            'name': internal,
            'value': external,
            'value_2': protocol,
            'value_2_join': '/',
        })
    options_port = options_system.get_or_create_bulk(options_port)

    config_internal = {
        'description': config_external.get('description'),
        'memory_uom_id': mib.id,
        'memory_limit': config_external.get('memory'),
        'memory_reservation': config_external.get('memoryReservation'),
        'memory_swappiness': config_external.get('memorySwappiness'),
        'memory_swap': config_external.get('memorySwap'),
        'cpu_limit': config_external.get('cpuQuota'),
        'cpu_pin': config_external.get('cpuSet'),
        'cpu_shared': config_external.get('cpuShares'),
        'cpu_count': config_external.get('cpuCount'),
        'cpu_reservation': config_external.get('milliCpuReservation'),
        'log_driver': config_external['logConfig'].get('driver'),
        'log_option_ids': [(6, 0, options_log.ids)],
        'volume_option_ids': [(6, 0, options_volume.ids)],
        'device_option_ids': [(6, 0, options_device.ids)],
        'image_uid': config_external['imageUuid'],
        'label_ids': [(6, 0, options_labels.ids)],
        'port_option_ids': [(6, 0, options_port.ids)],
        'is_privileged': config_external['privileged'],
        'version': config_external['version'],
        'disk_limit': config_external.get('diskQuota'),
    }
    return {'config_serialized': config_internal}


class RancherImportMapper(AbstractComponent):
    _name = 'rancher.import.mapper'
    _inherit = ['base.rancher.connector', 'base.import.mapper']
    _usage = 'import.mapper'

    @mapping
    @only_create
    def external_id(self, record):
        return {'external_id': record['id']}

    @mapping
    @only_create
    def backend_date_created(self, record):
        stamp = record.get('created')
        if stamp:
            return {'backend_date_created': dateutil.parser.parse(stamp)}

    @mapping
    @only_create
    def backend_id(self, _):
        return {'backend_id': self.backend_record.id}


class RancherExportMapper(AbstractComponent):
    _name = 'rancher.export.mapper'
    _inherit = ['base.rancher.connector', 'base.export.mapper']
    _usage = 'export.mapper'

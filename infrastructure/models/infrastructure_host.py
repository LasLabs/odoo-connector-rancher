# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models

from .constants import STATES_ACTIVE, STATES_HEALTH


class InfrastructureHost(models.Model):

    _name = 'infrastructure.host'
    _description = 'Infrastructure Hosts'

    name = fields.Char()
    description = fields.Char()
    environment_id = fields.Many2one(
        string='Environment',
        comodel_name='infrastructure.environment',
        required=True,
        readonly=True,
        ondelete='restrict',
    )
    state = fields.Selection(
        selection=STATES_ACTIVE,
        default='inactive',
    )
    state_health = fields.Selection(
        selection=STATES_HEALTH,
    )
    cpu_metric_id = fields.Many2one(
        string='Latest CPU Metric',
        comodel_name='infrastructure.metric.cpu',
        compute='_compute_cpu_metric_id',
        inverse='_inverse_cpu_metric_id',
    )
    cpu_metric_ids = fields.Many2many(
        string='CPU Metrics',
        comodel_name='infrastructure.metric.cpu',
        readonly=True,
    )
    memory_metric_id = fields.Many2one(
        string='Latest Memory Metric',
        comodel_name='infrastructure.metric.memory',
        compute='_compute_memory_metric_id',
        inverse='_inverse_memory_metric_id',
    )
    memory_metric_ids = fields.Many2many(
        string='Memory Metrics',
        comodel_name='infrastructure.metric.memory',
        readonly=True,
    )
    label_ids = fields.Many2many(
        string='Labels',
        comodel_name='infrastructure.option',
    )
    file_system_ids = fields.One2many(
        string='File Systems',
        comodel_name='infrastructure.file.system',
        inverse_name='host_id',
    )
    file_system_volume_ids = fields.Many2many(
        string='File System Volumes',
        comodel_name='infrastructure.volume',
        compute='_compute_file_system_volume_ids',
        search='_search_file_system_volume_ids',
    )
    volume_ids = fields.One2many(
        string='Volumes',
        comodel_name='infrastructure.volume',
        inverse_name='host_id',
        domain='[("id", "not in", file_system_volume_ids)]',
    )
    parent_id = fields.Many2one(
        string='Hypervisor',
        comodel_name=_name,
        help='This is the hypervisor for the host, if virtualized.',
        readonly=True,
    )
    child_ids = fields.One2many(
        string='Virtual Machines',
        comodel_name=_name,
        inverse_name='parent_id',
        help='If this host is a hypervisor, these are its virtual machines.',
    )
    operating_system_id = fields.Many2one(
        string='Operating System',
        comodel_name='infrastructure.software.version',
        domain="[('type', '=', 'os')]",
    )
    kernel_id = fields.Many2one(
        string='Kernel',
        comodel_name='infrastructure.software.version',
        domain="[('type', '=', 'kernel')]",
    )
    virtualization_id = fields.Many2one(
        string='Virtualization Software',
        comodel_name='infrastructure.software.version',
        domain="[('type', '=', 'virtualization')]",
    )
    instance_ids = fields.One2many(
        string='Instances',
        comodel_name='infrastructure.instance',
        inverse_name='host_id',
    )

    @api.multi
    def _compute_cpu_metric_id(self):
        for record in self:
            record.cpu_metric_id = record.cpu_metric_ids[:1].id

    @api.multi
    def _inverse_cpu_metric_id(self):
        for record in self:
            if record.cpu_metric_id:
                record.cpu_metric_id.reference = record
                record.cpu_metric_ids = [(4, record.cpu_metric_id.id)]

    @api.multi
    def _compute_memory_metric_id(self):
        for record in self:
            record.memory_metric_id = record.memory_metric_ids[:1].id

    @api.multi
    def _inverse_memory_metric_id(self):
        for record in self:
            if record.memory_metric_id:
                record.memory_metric_id.reference = record
                record.memory_metric_ids = [(4, record.memory_metric_id.id)]

    @api.multi
    @api.depends('file_system_ids.volume_id')
    def _compute_file_system_volume_ids(self):
        for record in self:
            record.file_system_volume_ids = [
                (6, 0, record.file_system_ids.mapped('volume_id').ids),
            ]

    @api.model
    def _search_file_system_volume_ids(self, operator, value):
        return [('file_system_ids.volume_id', operator, value)]

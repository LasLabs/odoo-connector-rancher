# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from datetime import datetime, timedelta

from odoo import fields

from odoo.addons.component.core import AbstractComponent
from odoo.addons.queue_job.exception import NothingToDoJob


_logger = logging.getLogger(__name__)


class RancherImporter(AbstractComponent):
    """ Base importer for Rancher """

    _name = 'rancher.importer'
    _inherit = ['base.importer', 'base.rancher.connector']
    _usage = 'record.importer'

    def __init__(self, work_context):
        super(RancherImporter, self).__init__(work_context)
        self.external_id = None
        self.rancher_record = None

    def _get_rancher_data(self):
        """Return the raw Rancher data for ``self.external_id``."""
        return self.backend_adapter.read(self.external_id)

    def _before_import(self):
        """Hook called before the import, when we have the Rancher data."""
        return

    def _import_dependency(self, external_id, binding_model,
                           importer=None, always=False):
        """Import a dependency.

        Args:
            external_id (int): ID of the external record to import.
            binding_model (basestring): Name of the model to bind to.
            importer (AbstractComponent, optional): Importer to use.
            always (bool, optional): Always update the record, regardless
                of if it exists in Odoo already. Note that if the record
                hasn't changed, it still may be skipped.
        """
        if not external_id:
            return
        binder = self.binder_for(binding_model)
        if always or not binder.to_internal(external_id):
            if importer is None:
                importer = self.component(usage='record.importer',
                                          model_name=binding_model)
            try:
                importer.run(external_id)
            except NothingToDoJob:
                _logger.info(
                    'Dependency import of %s(%s) has been ignored.',
                    binding_model._name, external_id
                )

    def _import_dependencies(self):
        """Import the dependencies for the record.

        Import of dependencies can be done manually or by calling
        :meth:`_import_dependency` for each dependency.
        """
        return

    def _map_data(self):
        """Returns an instance of
        :py:class:`~odoo.addons.connector.components.mapper.MapRecord`
        """
        return self.mapper.map_record(self.rancher_record)

    def _validate_data(self, data):
        """Check if the values to import are correct.

        Pro-actively check before the ``_create`` or
        ``_update`` if some fields are missing or invalid.

        Raises:
            InvalidDataError: In the event of a validation error
        """
        return

    def _should_skip(self, binding):
        """Hook called right before we read the data from the backend.

        It is used to skip imports if we have recently imported data for this
        record.
        """

        # Binding doesn't exist, don't skip.
        if not binding:
            return

        return self.env['rancher.queue.cache'].is_up_to_date(
            binding.backend_id, binding._name, binding.external_id,
        )

    def _get_binding(self):
        return self.binder.to_internal(self.external_id)

    def _create_data(self, map_record, **kwargs):
        return map_record.values(for_create=True, **kwargs)

    def _create(self, data):
        """Create the Odoo record. """
        # special check on data before import
        self._validate_data(data)
        model = self.model.with_context(connector_no_export=True)
        binding = model.create(data)
        _logger.debug(
            '%d created from rancher %s', binding, self.external_id,
        )
        return binding

    def _update_data(self, map_record, **kwargs):
        return map_record.values(**kwargs)

    def _update(self, binding, data):
        """Update an Odoo record."""
        # special check on data before import
        self._validate_data(data)
        binding.with_context(connector_no_export=True).write(data)
        _logger.debug(
            '%d updated from rancher %s', binding, self.external_id,
        )
        return

    def _after_import(self, binding):
        """Hook called at the end of the import."""
        return

    def run(self, external_id, force=False, external_record=None):
        """Run the synchronization.

        Args:
            external_id (int | rancher.BaseModel): identifier of the
                record in Rancher, or a Rancher record.
            force (bool, optional): Set to ``True`` to force the sync.
            external_record (rancher.models.BaseModel): Record from
                Rancher. Defining this will force the import of this
                record, instead of the search of the remote.

        Returns:
            RancherBinding: The binding record that was imported.
        """

        self.external_id = external_id
        lock_name = 'import({}, {}, {}, {})'.format(
            self.backend_record._name,
            self.backend_record.id,
            self.work.model_name,
            external_id,
        )

        binding = self._get_binding()
        skip = self._should_skip(binding)
        if skip and not force:
            return binding

        if external_record is not None:
            self.rancher_record = external_record
        else:
            self.rancher_record = self._get_rancher_data()

        # Keep a lock on this import until the transaction is committed.
        # The lock is kept since we have detected that the information
        # will be updated in Odoo.
        self.advisory_lock_or_retry(lock_name)
        self._before_import()

        # import the missing linked resources
        self._import_dependencies()

        map_record = self._map_data()

        if binding:
            record = self._update_data(map_record)
            self._update(binding, record)
        else:
            record = self._create_data(map_record)
            binding = self._create(record)

        self.binder.bind(self.external_id, binding)

        cache_minutes = binding.backend_id.cache_minutes
        self.env['rancher.queue.cache'].create({
            'backend_id': binding.backend_id.id,
            'model_name': binding._name,
            'external_id': binding.external_id,
            'date_expire': fields.Datetime.to_string(
                datetime.now() + timedelta(minutes=cache_minutes),
            ),
        })

        self._after_import(binding)

        return binding


class BatchImporter(AbstractComponent):
    """The role of a BatchImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    _name = 'rancher.batch.importer'
    _inherit = ['base.importer', 'base.rancher.connector']
    _usage = 'batch.importer'

    def run(self, filters=None):
        """Run the synchronization."""
        records = self.backend_adapter.search_read(**filters)
        for record in records:
            self._import_from_record(record.__dict__)

    def _import_from_record(self, data):
        """Import a record using already known data.

        This should be implemented in subclasses.
        """
        raise NotImplementedError

    def _import_record(self, external_id):
        """Import a record directly or delay import, TBD by subclass logic.

        This should be implemented in subclasses.
        """
        raise NotImplementedError


class DirectBatchImporter(AbstractComponent):
    """Import the records directly (no delay)."""

    _name = 'rancher.direct.batch.importer'
    _inherit = 'rancher.batch.importer'

    def _import_from_record(self, data):
        self.model.import_direct(self.backend_record, data)

    def _import_record(self, external_id, **kwargs):
        """Import the record directly."""
        self.model.import_record(self.backend_record, external_id, **kwargs)


class DelayedBatchImporter(AbstractComponent):
    """Schedule a delayed import of the records."""

    _name = 'rancher.delayed.batch.importer'
    _inherit = 'rancher.batch.importer'

    def _import_record(self, external_id, job_options=None, **kwargs):
        """Delay the record imports."""
        delayed = self.model.with_delay(**job_options or {})
        delayed.import_record(self.backend_record, external_id, **kwargs)

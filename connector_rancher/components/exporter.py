# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import threading
import psycopg2

from contextlib import contextmanager

from odoo import fields, _
from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import (IDMissingInBackend,
                                             RetryableJobError)


_logger = logging.getLogger(__name__)


class RancherExporterBase(AbstractComponent):

    _name = 'rancher.exporter.base'
    _inherit = ['base.exporter', 'base.rancher.connector']
    _usage = 'record.exporter'

    def __init__(self, working_context):
        super(RancherExporterBase, self).__init__(working_context)
        self.binding = None
        self.external_id = None
        self.export_result = None

    def _delay_import(self):
        """Schedule an import of the record.

        Adapt in the sub-classes when the model is not imported
        using ``import_record``.
        """
        assert self.external_id
        # force is True because the sync_date will be more recent
        # so the import would be skipped
        self.binding.with_delay().import_record(
            self.backend_record, self.external_id, force=True,
        )

    def _should_import(self):
        """Compare last sync date with remote update time.

        Returns:
            bool: Whether the record has changed and should be imported.
        """

        assert self.binding

        if not self.external_id:
            return False

        sync = self.binding.sync_date
        if not sync:
            return True

        record = self.backend_adapter.read(self.external_id)

        if not hasattr(record, 'modified_at'):
            # If there's no modified date, we should import always
            return True

        sync_date = fields.Datetime.from_string(sync)

        return sync_date < record.modified_at

    def run(self, binding, *args, **kwargs):
        """Run the synchronization.

        Args:
            binding (RancherBinding): Binding record to export.
        """

        self.binding = binding
        self.external_id = self.binder.to_external(self.binding)

        try:
            should_import = self._should_import()
        except IDMissingInBackend:
            self.external_id = None
            should_import = False

        if should_import:
            self._delay_import()

        self._run(*args, **kwargs)

        self.binder.bind(self.external_id, self.binding)
        # Commit so we keep the external ID when there are several
        # exports (due to dependencies) and one of them fails.
        # The commit will also release the lock acquired on the binding
        # record
        if not getattr(threading.currentThread(), 'testing', None):
            self.env.cr.commit()  # pylint: disable=E8102

        self._after_export()

        return self.export_result

    def _run(self):
        """Synchronization flow - to be implemented by inherited classes."""
        raise NotImplementedError

    def _after_export(self):
        """These actions will be performed after the record has been exported.
        """
        return


class RancherExporter(AbstractComponent):
    """A common flow for all Rancher exports."""

    _name = 'rancher.exporter'
    _inherit = 'rancher.exporter.base'

    def __init__(self, working_context):
        super(RancherExporter, self).__init__(working_context)
        self.binding = None

    def _lock(self):
        """Lock the binding record.

        Lock the binding record so we are sure that only one export
        job is running for this record if concurrent jobs have to export the
        same record.

        When concurrent jobs try to export the same record, the first one
        will lock and proceed, the others will fail to lock and will be
        retried later.

        This behavior works also when the export becomes multilevel
        with :meth:`_export_dependencies`. Each level will set its own lock
        on the binding record it has to export.
        """
        # pylint: disable=E8103
        sql = 'SELECT id FROM %s WHERE ID = %%s FOR UPDATE NOWAIT' % (
            self.model._table,
        )
        try:
            self.env.cr.execute(sql, (self.binding.id, ),
                                log_exceptions=False)
        except psycopg2.OperationalError:
            _logger.info(
                'A concurrent job is already exporting the same record (%s '
                'with id %s). Job delayed.',
                self.model._name, self.binding.id,
            )
            raise RetryableJobError(_(
                'A concurrent job is already exporting the same record '
                '(%s with id %s). The job will be retried later.'
            ) % (
                self.model._name, self.binding.id,
            ))

    def _has_to_skip(self):
        """Should the export be skipped?

        Returns:
            bool: ``True`` if the export should be skipped.
        """
        return False

    @contextmanager
    def _retry_unique_violation(self):
        """Catch Unique constraint error and retry the job later.

        When we execute several jobs workers concurrently, sometimes 2 jobs
        are creating the same record at the same time (binding
        record created by :meth:`_export_dependency`), resulting in::

            IntegrityError: duplicate key value violates unique
            constraint "rancher_product_product_odoo_uniq"
            DETAIL:  Key (backend_id, odoo_id)=(1, 4851) already exists.

        In that case, we'll retry the import just later.

        Warning:
            The unique constraint must be created on the binding record to
            prevent 2 bindings for the same Rancher record.
        """
        try:
            yield
        except psycopg2.IntegrityError as err:
            if err.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
                raise RetryableJobError(_(
                    'A database error caused the failure of the job:\n'
                    '%s\n\n'
                    'Likely due to 2 concurrent jobs wanting to create '
                    'the same record. The job will be retried later.'
                ) % (
                    err,
                ))
            else:
                raise

    def _export_dependency(self, relation, binding_model,
                           component_usage='record.exporter',
                           binding_field='rancher_bind_ids',
                           binding_extra_vals=None):
        """Export a dependency.

        The exporter class is a subclass of ``RancherExporter``. The
        ``exporter_class`` parameter can be used to modify this behavior.

        Warning:
            A commit is performed at the end of the export of each dependency.
            This is in order to maintain the integrity of any records that
            the external system contains.

            You must take care to not modify the Odoo database while an export
            is happening, except when writing back the external ID or to
            eventually store external data on this side.

            This method should only be called at the beginning of the exporter
            syncrhonization (in :meth:`~._export_dependencies`.)

        Args:
            relation (odoo.models.BaseModel): Record to export.
            binding_model (basestring): Name of the binding model for the
                relation
            component_usage (basestring): ``usage`` to look for when finding
                the ``Component`` for the export. Default ``record.exporter``.
            binding_field (basestring): Name of the one2many field on a normal
                record that points to the binding record. It is only used when
                 ``relation`` is a normal record instead of a binding.
            binding_exra_vals (dict):
        """
        if not relation:
            return
        rel_binder = self.binder_for(binding_model)
        # wrap is typically True if the relation is for instance a
        # 'product.product' record but the binding model is
        # 'rancher.product.product'
        wrap = relation._name != binding_model

        if wrap and hasattr(relation, binding_field):
            domain = [('odoo_id', '=', relation.id),
                      ('backend_id', '=', self.backend_record.id)]
            binding = self.env[binding_model].search(domain)
            if binding:
                assert len(binding) == 1, (
                    'only 1 binding for a backend is '
                    'supported in _export_dependency')
            # we are working with a unwrapped record (e.g.
            # product.category) and the binding does not exist yet.
            # Example: I created a product.product and its binding
            # rancher.product.product and we are exporting it, but we need to
            # create the binding for the product.category on which it
            # depends.
            else:
                bind_values = {'backend_id': self.backend_record.id,
                               'odoo_id': relation.id}
                if binding_extra_vals:
                    bind_values.update(binding_extra_vals)
                # If 2 jobs create it at the same time, retry
                # one later. A unique constraint (backend_id,
                # odoo_id) should exist on the binding model
                with self._retry_unique_violation():
                    binding = (self.env[binding_model]
                               .with_context(connector_no_export=True)
                               .sudo()
                               .create(bind_values))
                    # Eager commit to avoid having 2 jobs
                    # exporting at the same time. The constraint
                    # will pop if an other job already created
                    # the same binding. It will be caught and
                    # raise a RetryableJobError.
                    if not getattr(
                            threading.currentThread(), 'testing', None,
                    ):
                        self.env.cr.commit()  # pylint: disable=E8102
        else:
            # If rancher_bind_ids does not exist we are typically in a
            # "direct" binding (the binding record is the same record).
            # If wrap is True, relation is already a binding record.
            binding = relation

        if not rel_binder.to_external(binding):
            exporter = self.component(usage=component_usage,
                                      model_name=binding_model)
            exporter.run(binding)

    def _export_dependencies(self):
        """Export the dependencies for the record."""
        return

    def _map_data(self):
        """Return a mapper for the record.

        Returns:
            odoo.addons.connector.components.mapper.MapRecord
        """
        return self.mapper.map_record(self.binding)

    def _validate_create_data(self, data):
        """Check if the values to import are correct.

        Pro-actively check before the ``Model.create`` if some fields
        are missing or invalid.

        Raises:
             InvalidDataError: If the validation fails.
        """
        return

    def _validate_update_data(self, data):
        """Check if the values to import are correct.

        Pro-actively check before the ``Model.update`` if some fields
        are missing or invalid.

        Raises:
             InvalidDataError: If the validation fails.
        """
        return

    def _create_data(self, map_record, fields=None, **kwargs):
        """Get the data to pass to :py:meth:`_create`."""
        return map_record.values(for_create=True, fields=fields, **kwargs)

    def _create(self, data):
        """Create the Rancher record """
        # special check on data before export
        self._validate_create_data(data)
        return self.backend_adapter.create(data)

    def _update_data(self, map_record, fields=None, **kwargs):
        """Get the data to pass to :py:meth:`_update`."""
        return map_record.values(fields=fields, **kwargs)

    def _update(self, data):
        """Update an Rancher record."""
        assert self.external_id
        # special check on data before export
        self._validate_update_data(data)
        return self.backend_adapter.write(self.external_id, data)

    def _run(self, fields=None):
        """Standard synchronization flow. Customize in child classes."""
        assert self.binding

        if not self.external_id:
            fields = None  # should be created with all the fields

        if self._has_to_skip():
            return

        # export the missing linked resources
        self._export_dependencies()

        # prevent other jobs to export the same record
        # will be released on commit (or rollback)
        self._lock()

        map_record = self._map_data()

        if self.external_id:
            record = self._update_data(map_record, fields=fields)
            if not record:
                return _('Nothing to export.')
            self.export_result = self._update(record)

        else:
            record = self._create_data(map_record, fields=fields)
            if not record:
                return _('Nothing to export.')
            self.export_result = self._create(record)
            self.external_id = self.export_result.id

        return _('Record exported with ID %s on Rancher.') % self.external_id

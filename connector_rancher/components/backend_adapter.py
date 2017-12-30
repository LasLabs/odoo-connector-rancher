# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


# pylint: disable=W8106
class RancherCRUDAdapter(AbstractComponent):

    _name = 'rancher.crud.adapter'
    _inherit = ['base.backend.adapter', 'base.rancher.connector']
    _usage = 'backend.adapter'

    def search(self, filters=None):
        raise NotImplementedError

    def read(self, id):
        raise NotImplementedError

    def search_read(self, filters=None):
        raise NotImplementedError

    def create(self, data):
        raise NotImplementedError

    def write(self, id, data):
        raise NotImplementedError

    def delete(self, id):
        raise NotImplementedError


# pylint: disable=W8106
class RancherAdapter(AbstractComponent):

    _name = 'rancher.adapter'
    _inherit = 'rancher.crud.adapter'

    _rancher_endpoint = None

    # CRUD Operation constants
    CREATE = 'create'
    READ = 'by_id'
    SEARCH = 'list'

    @property
    def rancher(self):
        """Return the Rancher API for use."""
        try:
            return getattr(self.work, 'rancher_api')
        except AttributeError:
            raise AttributeError(_(
                'You must provide a `rancher_api` attribute to be able '
                'to use this Backend Adapter.',
            ))

    def get_endpoint(self, operation):
        """Return a usable endpoint for the API."""
        attribute = '%s_%s' % (operation, self._rancher_endpoint)
        return getattr(self.rancher, attribute)

    def search(self, **query):
        """Search records according to filters and return the result IDs."""
        return [r.id for r in self.search_read(**query)]

    def search_read(self, **query):
        return self.get_endpoint(self.SEARCH)(**query)

    def read(self, _id, return_object=False):
        """Get records according to its ID."""
        result = self.get_endpoint(self.READ)(_id)
        if result:
            return result if return_object else result.__dict__

    def create(self, data):
        """Create a record on the remote."""
        return self.get_endpoint(self.CREATE)(data)

    def write(self, _id, data):
        """Write the record on the remote."""
        record = self.read(_id, return_object=True)
        return self.rancher.update(record, data)

    def delete(self, _id):
        """Delete the record from the remote."""
        record = self.read(_id, return_object=True)
        return self.rancher.delete(record)

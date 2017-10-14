# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from collective.tinymce_mention.testing import COLLECTIVE_TINYMCE_MENTION_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.tinymce_mention is properly installed."""

    layer = COLLECTIVE_TINYMCE_MENTION_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.tinymce_mention is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.tinymce_mention'))

    def test_browserlayer(self):
        """Test that ICollectiveTinymceMentionLayer is registered."""
        from collective.tinymce_mention.interfaces import (
            ICollectiveTinymceMentionLayer)
        from plone.browserlayer import utils
        self.assertIn(
            ICollectiveTinymceMentionLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_TINYMCE_MENTION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.tinymce_mention'])

    def test_product_uninstalled(self):
        """Test if collective.tinymce_mention is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.tinymce_mention'))

    def test_browserlayer_removed(self):
        """Test that ICollectiveTinymceMentionLayer is removed."""
        from collective.tinymce_mention.interfaces import \
            ICollectiveTinymceMentionLayer
        from plone.browserlayer import utils
        self.assertNotIn(
           ICollectiveTinymceMentionLayer,
           utils.registered_layers())

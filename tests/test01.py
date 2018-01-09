# -*- coding: utf-8 -*-
import pytest
import six

from idoit import API, Idoit


class TestQuery(object):
    def test_login_logout(self):
        # Use credentials from public demo
        api = API(
            url="https://demo.i-doit.com/src/jsonrpc.php",
            key="c1ia5q",
            username="admin",
            password="admin",
        )
        api.login()
        idoit_obj = Idoit(api=api)
        assert isinstance(idoit_obj.version, six.string_types)
        assert idoit_obj.version_type in ("PRO",)
        assert isinstance(idoit_obj.get_constants(), dict)

        api.logout()

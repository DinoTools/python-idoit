import json

import requests


class API(object):
    def __init__(self, url=None, key=None, username=None, password=None):
        """
        Low-Level object to access the i-doit JSON-RPC API.

        :param str url: URL to access the JSON-RPC API
        :param str key: API-Key
        :param str username: Username
        :param str password: Password
        """
        self._session_id = None
        self.key = key
        self.username = username
        self.password = password
        self.url = url

    def login(self, username=None, password=None):
        """
        Perform login

        :param str username: Overrides the current username value
        :param str password: Overrides the current password value
        """
        if username:
            self.username = username
        if password:
            self.password = password

        headers = {
            "X-RPC-Auth-Username": self.username,
            "X-RPC-Auth-Password": self.password
        }

        result = self.request(
            "idoit.login",
            headers=headers
        )
        self._session_id = result["session-id"]

    def logout(self):
        self.request("idoit.logout")
        self._session_id = None

    def request(self, method, params=None, headers=None):
        """

        :param str method:
        :param dict params:
        :param dict headers:
        :return:
        """
        req_headers = {'content-type': 'application/json'}
        if self._session_id is not None:
            req_headers["X-RPC-Auth-Session"] = self._session_id

        if isinstance(headers, dict):
            req_headers.update(headers)

        req_params = {
            "apikey": self.key
        }
        if isinstance(params, dict):
            req_params.update(params)

        # Example echo method
        payload = {
            "method": method,
            "params": req_params,
            "jsonrpc": "2.0",
            "id": 0,
        }

        response = requests.post(
            self.url,
            data=json.dumps(payload),
            headers=req_headers
        ).json()
        from pprint import pprint
        #pprint(response)
        if "error" in response:
            error = response["error"]
            error_code = error["code"]
            from idoit.exception import InvalidParams, InternalError, MethodNotFound, UnknownError
            for exception_class in [InvalidParams, InternalError, MethodNotFound]:
                if exception_class.code == error_code:
                    raise exception_class(
                        data=error["data"],
                        raw_code=error_code
                    )
            raise UnknownError(
                data=error["data"],
                raw_code=error_code
            )
        return response['result']


class BaseRequest(object):
    def __init__(self, api=None, api_params=None):
        if api is None:
            if api_params is None:
                api_params = {}
            api = API(**api_params)
        self._api = api


class Idoit(BaseRequest):
    @property
    def version(self):
        data = self.get_version()
        return data["version"]

    @property
    def version_type(self):
        data = self.get_version()
        return data["type"]

    def get_constants(self):
        return self._api.request("idoit.constants")

    def get_version(self):
        return self._api.request("idoit.version")

    def search(self, query):
        return self._api.request(
            "idoit.search",
            {"q": query}
        )


class CMDBCategory(BaseRequest):
    STATUS_NORMAL = "C__RECORD_STATUS__NORMAL"
    STATUS_ARCHIVED = "C__RECORD_STATUS__ARCHIVED"
    STATUS_DELETED = "C__RECORD_STATUS__DELETED"

    def __init__(self, api=None, api_params=None, default_read_status=None):
        super(CMDBCategory, self).__init__(api=api, api_params=api_params)
        self.default_read_status = default_read_status

    def read(self, object_id, category=None, catg_id=None, cats_id=None, status=None):
        """
        Read one or more category entries for an object.

        Use only one of the optional parameters category, catg_id or cats_id.

        :param int object_id: Object identifier
        :param str category: Category constant
        :param int catg_id: Global category identifier
        :param int cats_id: Specific category identifier
        :return: List of result objects
        :rtype: dict[]
        """
        params = {
            "objID": object_id
        }
        if category:
            params["category"] = category
        elif catg_id:
            params["catgID"] = catg_id
        elif cats_id:
            params["catsID"] = cats_id
        else:
            # ToDo: Improve exception
            raise Exception("Missing parameter")

        if status is None:
            status = self.default_read_status
        if status is not None:
            params["status"] = status

        return self._api.request(
            method="cmdb.category",
            params=params
        )


class CMDBObjects(BaseRequest):
    def read(self, filter_params=None):
        params = {}

        if isinstance(filter_params, dict):
            params["filter"] = filter_params

        return self._api.request(
            method="cmdb.objects.read",
            params=params
        )

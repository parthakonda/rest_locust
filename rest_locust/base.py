import json
from copy import deepcopy

from jinja2 import BaseLoader, Environment
from locust import HttpLocust, TaskSet, task


class BaseTaskSet(TaskSet):
    """
    - Getting token
    - Unpack data
    - compile resource url
    """
    headers = {
        'Content-Type': 'application/json'
    }
    token = None
    token_url = None
    token_title = 'JWT'

    def unpack_values(self, payload_data):
        """
        will unpack the values recursively
        if they have nested __call__'ble object
        @param: payload_data [string, number, list, tuple, dict, __call__able]
        if dictionary then recursively process that
        if __call__able then call()
        else return val
        """
        if isinstance(payload_data, dict) is True:
            for key, val in deepcopy(payload_data).items():
                #
                # Means, you can dynamically provide the data
                # at the time of execution
                #
                if key == '__compile__':
                    payload_data.update(self.unpack_values(val))
                    del payload_data['__compile__']
                else:
                    payload_data.update({key: self.unpack_values(val)})
            return payload_data
        if hasattr(payload_data, '__call__') is True:
            return payload_data()
        return payload_data

    def compile_resource(self, resource, params):
        """
        Will replace resource params with data
        @return: compiled_url
        """
        rtemplate = Environment(loader=BaseLoader).from_string(resource)
        _params = deepcopy(params)
        _params.update(self.unpack_values(_params))
        return rtemplate.render(**_params)

    def get_headers(self):
        """
        Will return headers with
        Authorization & Content-Type
        """
        return {
            'Content-Type': 'application/json',
            'Authorization': '{} {}'.format(self.token_title, self.token)
        }

    def on_start(self):
        """
        Will set the token
        """
        credentials = None
        if hasattr(self, 'get_credentials'):
            credentials = self.get_credentials()
        else:
            raise NotImplementedError
        response = self.client.post(
            self.token_url,
            data=credentials,
            headers=self.headers
        )
        if response.status_code == 200:
            self.token = response.json().get('token', None)


class ListBaseTask(BaseTaskSet):
    """
    Using for only 'GET' request
    """
    list = None

    @task
    def _list(self):
        """
        Will send GET request to the specified resource
        """
        if not hasattr(self, 'list'):
            raise(KeyError, 'list action not provided')

        if not self.list.get('url', None):
            raise(KeyError, 'url not provided in list action')

        self.client.get(
            self.compile_resource(self.list.get(
                'url'), self.list.get('params', {})),
            headers=self.get_headers()
        )


class RetrieveBaseTask(BaseTaskSet):
    """
    Using for only 'GET' request with 'ID'
    """
    @task
    def _retrieve(self):
        """
        Will send GET request to specified resource
        with given ID
        """
        if not hasattr(self, 'retrieve'):
            raise(KeyError, 'retrieve action not provided')

        if not self.retrieve.get('url', None):
            raise(KeyError, 'url not provided in retrieve action')

        self.client.get(
            self.compile_resource(self.retrieve.get(
                'url'), self.retrieve.get('params', {})),
            headers=self.get_headers()
        )


class CreateBaseTask(BaseTaskSet):
    """
    Using for only 'POST' request
    """
    @task
    def _create(self):
        """
        Will send POST request to the specified resource
        """
        headers = self.get_headers()
        if not hasattr(self, 'create'):
            raise(KeyError, 'create action not provided')

        if not self.create.get('url', None):
            raise(KeyError, 'url not provided in create action')

        if self.create.get('headers', None):
            headers.update(self.create.get('headers'))

        if not self.create.get('data', None):
            raise(KeyError, 'data not provided in create action')

        _data = deepcopy(self.create.get('data'))
        _data.update(self.unpack_values(_data))

        self.client.post(
            self.compile_resource(self.create.get(
                'url'), self.create.get('params', {})),
            data=_data if self.create.get(
                'form-data', True) else json.dumps(_data),
            headers=headers
        )


class UpdateBaseTask(TaskSet):
    """
    Using for only 'PUT' request
    """
    @task
    def _update(self):
        """
        Will send PUT request to the specified resource
        """
        if not hasattr(self, 'update'):
            raise(KeyError, 'update action not provided')

        if not self.update.get('url', None):
            raise(KeyError, 'url not provided in update action')

        if not self.update.get('data', None):
            raise(KeyError, 'data not provided in update action')

        _data = deepcopy(self.update.get('data'))
        for key, val in _data.items():
            #
            # Means, you can dynamically provide the data
            # at the time of execution
            #
            _data.update({key: self.unpack_values(val)})

        self.client.put(
            self.compile_resource(self.update.get(
                'url'), self.update.get('params', {})),
            data=json.dumps(_data),
            headers=self.get_headers()
        )


class MultipleRetrieveBaseTask(BaseTaskSet):
    """
    Using for only 'GET' request with 'ID'
    """
    @task
    def _retrieve(self):
        """
        Will send GET request to specified resource
        with given ID
        """
        if not hasattr(self, 'retrieve'):
            raise(KeyError, 'retrieve action not provided')

        for retrieve in self.retrieve:
            if not retrieve.get('url', None):
                raise(KeyError, 'url not provided in retrieve action')

        for retrieve in self.retrieve:
            self.client.get(
                self.compile_resource(retrieve.get(
                    'url'), retrieve.get('params', {})),
                headers=self.get_headers()
            )


class MultipleListBaseTask(BaseTaskSet):
    """
    Using for only 'GET' request
    """
    list = []

    @task
    def _list(self):
        """
        Will send GET request to the specified resource
        """
        if not hasattr(self, 'list'):
            raise(KeyError, 'list action not provided')

        for list in self.list:
            if not list.get('url', None):
                raise(KeyError, 'url not provided in list action')

        for list in self.list:
            self.client.get(
                self.compile_resource(list.get('url'), list.get('params', {})),
                headers=self.get_headers()
            )


class DestroyBaseTask(TaskSet):
    """
    Using for only 'DELETE' request
    """
    @task
    def _destroy(self):
        """
        Will send DELETE request to the specified resource
        """
        if not hasattr(self, 'destroy'):
            raise(KeyError, 'destroy action not provided')

        if not self.update.get('url', None):
            raise(KeyError, 'url not provided in create action')

        self.client.delete(
            self.compile_resource(self.update.get(
                'url'), self.update.get('params', {})),
            headers=self.get_headers()
        )


class ListRetrieveTask(ListBaseTask, RetrieveBaseTask):
    """
    For supporting `list` and `retrieve` actions
    """
    pass


class ListMultiRetrieveTask(ListBaseTask, MultipleRetrieveBaseTask):
    """
    For supporting `list`, `retrieve` actions
    """
    pass


class ListRetrieveCreateTask(ListRetrieveTask, CreateBaseTask):
    """
    For supporting `list`, `retrieve` and `create` actions
    """
    pass


class ListRetrieveCreateUpdateTask(ListRetrieveCreateTask, UpdateBaseTask):
    """
    For supporting `list`, `retrieve`, `create` and `update` actions
    """
    pass


class RESTBaseTask(
    ListBaseTask,
    RetrieveBaseTask,
    CreateBaseTask,
    UpdateBaseTask,
    DestroyBaseTask
):
    """
    For sending requests to REST API
    """
    pass

import requests


class Session(requests.Session):

    def _store_xsrf_token(self, response):
        xsrf_token = response.cookies.get('XSRF-TOKEN')
        if xsrf_token:
            self.xsrf_token = xsrf_token

    def _set_xsrf_headers(self, kwargs):
        xsrf_header = {
            'X-XSRF-TOKEN': self.xsrf_token,
        }
        if 'headers' in kwargs:
            kwargs['headers'].update(xsrf_header)
        else:
            kwargs['headers'] = xsrf_header
        return kwargs

    def get(self, *args, **kwargs):
        response = super(Session, self).get(*args, **kwargs)
        self._store_xsrf_token(response)
        return response

    def post(self, *args, **kwargs):
        if kwargs.pop('add_xsrf_token', True):
            kwargs = self._set_xsrf_headers(kwargs)
        response = super(Session, self).post(*args, **kwargs)
        self._store_xsrf_token(response)
        return response

    def put(self, *args, **kwargs):
        if kwargs.pop('add_xsrf_token', True):
            kwargs = self._set_xsrf_headers(kwargs)
        response = super(Session, self).put(*args, **kwargs)
        self._store_xsrf_token(response)
        return response

    def delete(self, *args, **kwargs):
        kwargs = self._set_xsrf_headers(kwargs)
        response = super(Session, self).delete(*args, **kwargs)
        self._store_xsrf_token(response)
        return response

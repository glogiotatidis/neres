import requests


class Session(requests.Session):
    def _set_xsrf_headers(self, kwargs):
        try:
            xsrf_token = self.cookies._cookies['synthetics.newrelic.com']['/']['XSRF-TOKEN'].value
        except KeyError:
            return kwargs
        else:

            xsrf_header = {
                'X-XSRF-TOKEN': xsrf_token,
            }
            if 'headers' in kwargs:
                kwargs['headers'].update(xsrf_header)
            else:
                kwargs['headers'] = xsrf_header
        return kwargs

    def get(self, *args, **kwargs):
        response = super(Session, self).get(*args, **kwargs)
        return response

    def post(self, *args, **kwargs):
        if kwargs.pop('add_xsrf_token', True):
            kwargs = self._set_xsrf_headers(kwargs)
        response = super(Session, self).post(*args, **kwargs)
        return response

    def put(self, *args, **kwargs):
        if kwargs.pop('add_xsrf_token', True):
            kwargs = self._set_xsrf_headers(kwargs)
        response = super(Session, self).put(*args, **kwargs)
        return response

    def delete(self, *args, **kwargs):
        kwargs = self._set_xsrf_headers(kwargs)
        response = super(Session, self).delete(*args, **kwargs)
        return response

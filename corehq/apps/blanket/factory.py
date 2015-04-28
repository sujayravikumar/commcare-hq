import json
import logging
import sys
import traceback
from datetime import datetime

from django.core.urlresolvers import resolve

from .models import BlanketResponseDocument, BlanketRequestDocument

Logger = logging.getLogger('blanket')

content_types_json = ['application/json',
                      'application/x-javascript',
                      'text/javascript',
                      'text/x-javascript',
                      'text/x-json']
content_type_form = ['multipart/form-data',
                     'application/x-www-form-urlencoded']
content_type_html = ['text/html']
content_type_css = ['text/css']


def _parse_content_type(content_type):
    """best efforts on pulling out the content type and encoding from Content-Type header"""
    try:
        content_type = content_type.strip()
    except AttributeError:
        pass
    char_set = None
    if content_type.strip():
        splt = content_type.split(';')
        content_type = splt[0]
        try:
            raw_char_set = splt[1].strip()
            key, char_set = raw_char_set.split('=')
            if key != 'charset':
                char_set = None
        except (IndexError, ValueError):
            pass
    return content_type, char_set


class RequestModelFactory(object):
    """Produce Request models from Django request objects"""

    def __init__(self, request):
        self.request = request

    def content_type(self):
        content_type = self.request.META.get('CONTENT_TYPE', '')
        return _parse_content_type(content_type)

    def encoded_headers(self):
        """
        From Django docs (https://docs.djangoproject.com/en/1.6/ref/request-response/#httprequest-objects):
        "With the exception of CONTENT_LENGTH and CONTENT_TYPE, as given above, any HTTP headers in the request are converted to
        META keys by converting all characters to uppercase, replacing any hyphens with underscores and adding an HTTP_ prefix
        to the name. So, for example, a header called X-Bender would be mapped to the META key HTTP_X_BENDER."
        """
        headers = {}
        for k, v in self.request.META.items():
            if k.startswith('HTTP') or k in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                splt = k.split('_')
                if splt[0] == 'HTTP':
                    splt = splt[1:]
                k = '-'.join(splt)
                headers[k] = v
        return json.dumps(headers)

    def _body(self, raw_body, content_type):
        """
        Encode body as JSON if possible so can be used as a dictionary in generation
        of curl/django test client code
        """
        body = ''
        if content_type in content_type_form:
            body = self.request.POST
            body = json.dumps(dict(body), sort_keys=True, indent=4)
        elif content_type in content_types_json:
            try:
                body = json.dumps(json.loads(raw_body), sort_keys=True, indent=4)
            except:
                body = raw_body
        return body

    def body(self):
        content_type, char_set = self.content_type()
        raw_body = self.request.body
        if char_set:
            try:
                raw_body = raw_body.decode(char_set)
            except AttributeError:
                pass
            except LookupError:  # If no encoding exists, default to UTF-8
                try:
                    raw_body = raw_body.decode('UTF-8')
                except AttributeError:
                    pass
                except UnicodeDecodeError:
                    raw_body = ''
            except Exception as e:
                Logger.error('Unable to decode request body using char_set %s due to error: %s. Will ignore. Stacktrace:' % (char_set, e))
                traceback.print_exc()
        else:
            # Default to an attempt at UTF-8 decoding.
            try:
                raw_body = raw_body.decode('UTF-8')
            except AttributeError:
                pass
            except UnicodeDecodeError:
                raw_body = ''
        body = ''
        if raw_body:
            Logger.debug('No maximum request body size is set, continuing.')
            body = self._body(raw_body, content_type)
        return body, raw_body

    def query_params(self):
        query_params = self.request.GET
        encoded_query_params = ''
        if query_params:
            query_params_dict = dict(zip(query_params.keys(), query_params.values()))
            encoded_query_params = json.dumps(query_params_dict)
        return encoded_query_params

    def construct_request_model(self):
        body, raw_body = self.body()
        query_params = self.query_params()
        path = self.request.path
        resolved = resolve(path)
        namespace = resolved.namespace
        view_name = resolved.url_name
        if namespace:
            view_name = namespace + ':' + view_name
        request_model = BlanketRequestDocument(
            path=path,
            encoded_headers=self.encoded_headers(),
            method=self.request.method,
            query_params=query_params,
            view_name=view_name,
            start_time=datetime.utcnow(),
            body=body
        )
        # Text fields are encoded as UTF-8 in Django and hence will try to coerce
        # anything to we pass to UTF-8. Some stuff like binary will fail.
        try:
            request_model.raw_body = raw_body
        except UnicodeDecodeError:
            Logger.debug('NYI: Binary request bodies')  # TODO
        Logger.debug('Created new request model with pk %s' % request_model._id)
        return request_model


class ResponseModelFactory(object):
    """given a response object, craft the blanket response model"""

    def __init__(self, response):
        self.response = response
        #self.request = DataCollector().request

    def body(self):
        body = ''
        content_type, char_set = _parse_content_type(self.response.get('Content-Type', ''))
        content = getattr(self.response, 'content', '')
        if char_set and content:
            try:
                content = content.decode(char_set)
            except AttributeError:
                pass
            except LookupError:  # If no encoding exists, default to UTF-8
                try:
                    content = content.decode('UTF-8')
                except AttributeError:
                    pass
                except UnicodeDecodeError:
                    content = ''
            except Exception as e:
                Logger.error('Unable to decode response body using char_set %s due to error: %s. Will ignore. Stacktrace:' % (char_set, e))
                traceback.print_exc()
        else:
            # Default to an attempt at UTF-8 decoding.
            try:
                content = content.decode('UTF-8')
            except AttributeError:
                pass
            except UnicodeDecodeError:
                content = ''

        return body, content

    def construct_response_model(self):
        b, content = self.body()
        raw_headers = self.response._headers
        headers = {}
        for k, v in raw_headers.items():
            try:
                header, val = v
            except ValueError:
                header, val = k, v
            finally:
                headers[header] = val
        response = BlanketResponseDocument(
            status_code=self.response.status_code,
            encoded_headers=json.dumps(headers),
            body=b
        )
        # Text fields are encoded as UTF-8 in Django and hence will try to coerce
        # anything to we pass to UTF-8. Some stuff like binary will fail.
        try:
            response.raw_body = content
        except UnicodeDecodeError:
            Logger.debug('NYI: Saving of binary response body')  # TODO
        return response

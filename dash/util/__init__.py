import logging

import flask
import requests
from cachelib import SimpleCache
from gen3.auth import endpoint_from_token
logger = logging.getLogger('dash')
from gen3.query import Gen3Query
from gen3.submission import Gen3Submission

# Cache the access for 60 seconds so that we don't make multiple requests to
# Arborist when a user accesses a webpage and fetches multiple JS/CSS files.
ACCESS_CACHE = SimpleCache(default_timeout=60)


def get_guppy_service(endpoint='http://revproxy-service') -> Gen3Query:
    """Construct a Query Class

    See https://uc-cdis.github.io/gen3sdk-python/_build/html/query.html#gen3.query.Gen3Query
    """
    return Gen3Query(Gen3SessionAuth(endpoint=endpoint))


def get_submission_service(endpoint='http://revproxy-service') -> Gen3Submission:
    """Construct a Query Class

    See https://uc-cdis.github.io/gen3sdk-python/_build/html/submission.html#gen3.submission.Gen3Submission.query
    """
    return Gen3Submission(Gen3SessionAuth(endpoint=endpoint))


def get_authz():
    """Returns authorization from arborist."""
    # no request active
    if not flask.request:
        logger.error('get_authz: No flask request')
        return {}

    # get incoming headers
    if 'Authorization' not in flask.request.headers:
        logger.error('get_authz: No Authorization in flask request')
        return {}

    authorization = flask.request.headers['Authorization']
    # hit, in cache
    if ACCESS_CACHE.has(authorization):
        return ACCESS_CACHE.get(authorization)
    # miss, go get it
    # logger.debug("Refreshing authz")
    arborist_response = requests.get('http://revproxy-service/authz/mapping',
                                     headers={'Authorization': authorization})
    arborist_response.raise_for_status()
    # update cache
    ACCESS_CACHE.set(authorization, arborist_response.json())
    return ACCESS_CACHE.get(authorization)


class Gen3SessionAuth(requests.auth.AuthBase):
    """
    An Auth helper based on access token.
    No attempt is made to refresh.
    """
    def __init__(self, access_token=None, endpoint=None):
        """
        endpoint
        """
        if access_token:
            self._access_token = access_token
        elif not flask.request:
            logger.error('Gen3SessionAuth No flask request')
        elif 'Authorization' not in flask.request.headers:
            logger.error('Gen3SessionAuth: No Authorization in flask request')
        else:
            authorization_parts = flask.request.headers['Authorization'].split(' ')
            assert len(authorization_parts) == 2, f"Gen3SessionAuth expected bearer token {flask.request.headers['Authorization']}"
            self._access_token = authorization_parts[-1]
            if endpoint:
                self.endpoint = endpoint
            else:
                self.endpoint = endpoint_from_token(self._access_token)
            # logger.debug(f"Gen3SessionAuth _access_token {self._access_token} endpoint {self.endpoint}")

    def __call__(self, request_):
        """Adds authorization header to the request
        This gets called by the python.requests package on outbound requests
        so that authentication can be added.
        Args:
            request_ (object): The incoming request object
        """
        request_.headers["Authorization"] = "bearer " + self._access_token
        # logger.debug(f"Gen3SessionAuth request_.headers['Authorization'] {request_.headers['Authorization']}")
        return request_

# def get_authz_mock():
#     """"""
#     return {'/data_file': [{'service': 'fence', 'method': 'file_upload'}, {'service': 'indexd', 'method': '*'}],
#             '/open': [{'service': '*', 'method': 'read'}, {'service': '*', 'method': 'read-storage'}],
#             '/programs': [{'service': 'indexd', 'method': '*'}],
#             '/programs/MyFirstProgram': [{'service': 'indexd', 'method': '*'}],
#             '/programs/MyFirstProgram/projects': [{'service': 'indexd', 'method': '*'}],
#             '/programs/MyFirstProgram/projects/MyFirstProject': [{'service': '*', 'method': 'create'},
#                                                                  {'service': '*', 'method': 'delete'},
#                                                                  {'service': '*', 'method': 'read'},
#                                                                  {'service': '*', 'method': 'read-storage'},
#                                                                  {'service': '*', 'method': 'update'},
#                                                                  {'service': '*', 'method': 'write-storage'},
#                                                                  {'service': 'indexd', 'method': '*'}],
#             '/programs/aced': [{'service': 'indexd', 'method': '*'}],
#             '/programs/aced/projects': [{'service': 'indexd', 'method': '*'}],
#             '/programs/aced/projects/Alcoholism': [{'service': '*', 'method': 'create'},
#                                                    {'service': '*', 'method': 'delete'},
#                                                    {'service': '*', 'method': 'read'},
#                                                    {'service': '*', 'method': 'read-storage'},
#                                                    {'service': '*', 'method': 'update'},
#                                                    {'service': '*', 'method': 'write-storage'},
#                                                    {'service': 'indexd', 'method': '*'}],
#             '/programs/aced/projects/Alzheimers': [{'service': '*', 'method': 'create'},
#                                                    {'service': '*', 'method': 'delete'},
#                                                    {'service': '*', 'method': 'read'},
#                                                    {'service': '*', 'method': 'read-storage'},
#                                                    {'service': '*', 'method': 'update'},
#                                                    {'service': '*', 'method': 'write-storage'},
#                                                    {'service': 'indexd', 'method': '*'}],
#             '/programs/aced/projects/Breast_Cancer': [{'service': '*', 'method': 'create'},
#                                                       {'service': '*', 'method': 'delete'},
#                                                       {'service': '*', 'method': 'read'},
#                                                       {'service': '*', 'method': 'read-storage'},
#                                                       {'service': '*', 'method': 'update'},
#                                                       {'service': '*', 'method': 'write-storage'},
#                                                       {'service': 'indexd', 'method': '*'}],
#             '/programs/aced/projects/Colon_Cancer': [{'service': '*', 'method': 'create'},
#                                                      {'service': '*', 'method': 'delete'},
#                                                      {'service': '*', 'method': 'read'},
#                                                      {'service': '*', 'method': 'read-storage'},
#                                                      {'service': '*', 'method': 'update'},
#                                                      {'service': '*', 'method': 'write-storage'},
#                                                      {'service': 'indexd', 'method': '*'}],
#             '/programs/aced/projects/Diabetes': [{'service': '*', 'method': 'create'},
#                                                  {'service': '*', 'method': 'delete'},
#                                                  {'service': '*', 'method': 'read'},
#                                                  {'service': '*', 'method': 'read-storage'},
#                                                  {'service': '*', 'method': 'update'},
#                                                  {'service': '*', 'method': 'write-storage'},
#                                                  {'service': 'indexd', 'method': '*'}],
#             '/programs/aced/projects/Lung_Cancer': [{'service': '*', 'method': 'create'},
#                                                     {'service': '*', 'method': 'delete'},
#                                                     {'service': '*', 'method': 'read'},
#                                                     {'service': '*', 'method': 'read-storage'},
#                                                     {'service': '*', 'method': 'update'},
#                                                     {'service': '*', 'method': 'write-storage'},
#                                                     {'service': 'indexd', 'method': '*'}],
#             '/programs/aced/projects/Prostate_Cancer': [{'service': '*', 'method': 'create'},
#                                                         {'service': '*', 'method': 'delete'},
#                                                         {'service': '*', 'method': 'read'},
#                                                         {'service': '*', 'method': 'read-storage'},
#                                                         {'service': '*', 'method': 'update'},
#                                                         {'service': '*', 'method': 'write-storage'},
#                                                         {'service': 'indexd', 'method': '*'}],
#             '/programs/jnkns': [{'service': '*', 'method': 'create'}, {'service': '*', 'method': 'delete'},
#                                 {'service': '*', 'method': 'read'}, {'service': '*', 'method': 'read-storage'},
#                                 {'service': '*', 'method': 'update'}, {'service': '*', 'method': 'write-storage'},
#                                 {'service': 'indexd', 'method': '*'}],
#             '/programs/jnkns/projects': [{'service': '*', 'method': 'create'}, {'service': '*', 'method': 'delete'},
#                                          {'service': '*', 'method': 'read'}, {'service': '*', 'method': 'read-storage'},
#                                          {'service': '*', 'method': 'update'},
#                                          {'service': '*', 'method': 'write-storage'},
#                                          {'service': 'indexd', 'method': '*'}],
#             '/programs/jnkns/projects/jenkins': [{'service': '*', 'method': 'create'},
#                                                  {'service': '*', 'method': 'delete'},
#                                                  {'service': '*', 'method': 'read'},
#                                                  {'service': '*', 'method': 'read-storage'},
#                                                  {'service': '*', 'method': 'update'},
#                                                  {'service': '*', 'method': 'write-storage'},
#                                                  {'service': 'indexd', 'method': '*'}],
#             '/programs/program1': [{'service': '*', 'method': 'create'}, {'service': '*', 'method': 'delete'},
#                                    {'service': '*', 'method': 'read'}, {'service': '*', 'method': 'read-storage'},
#                                    {'service': '*', 'method': 'update'}, {'service': '*', 'method': 'write-storage'},
#                                    {'service': 'indexd', 'method': '*'}],
#             '/programs/program1/projects': [{'service': '*', 'method': 'create'}, {'service': '*', 'method': 'delete'},
#                                             {'service': '*', 'method': 'read'},
#                                             {'service': '*', 'method': 'read-storage'},
#                                             {'service': '*', 'method': 'update'},
#                                             {'service': '*', 'method': 'write-storage'},
#                                             {'service': 'indexd', 'method': '*'}],
#             '/programs/program1/projects/P1': [{'service': '*', 'method': 'create'},
#                                                {'service': '*', 'method': 'delete'}, {'service': '*', 'method': 'read'},
#                                                {'service': '*', 'method': 'read-storage'},
#                                                {'service': '*', 'method': 'update'},
#                                                {'service': '*', 'method': 'write-storage'},
#                                                {'service': 'indexd', 'method': '*'}],
#             '/services/sheepdog/submission/program': [{'service': 'sheepdog', 'method': '*'}],
#             '/services/sheepdog/submission/project': [{'service': 'sheepdog', 'method': '*'}],
#             '/workspace': [{'service': 'jupyterhub', 'method': 'access'}]}

"""Common response model for API's."""

from http import HTTPStatus

from pydantic import BaseModel


class HTTPError(BaseModel):
    '''Model of HTTP errors' responses for openapi.json.'''
    detail: str


possible_error_codes = (
    HTTPStatus.BAD_REQUEST,
    HTTPStatus.UNAUTHORIZED,
    HTTPStatus.FORBIDDEN,
    HTTPStatus.NOT_FOUND,
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.SERVICE_UNAVAILABLE,
    HTTPStatus.TOO_MANY_REQUESTS
)
common_responses = {code: {"model": HTTPError} for code in possible_error_codes}
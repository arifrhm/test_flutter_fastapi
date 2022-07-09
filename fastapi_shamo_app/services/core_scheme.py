import decimal
import json
from enum import Enum


class ResponseOutCustom:
    def __init__(self, message_id=None, status=None, list_data=None, **kwargs):
        self.message_id = message_id
        self.status = status
        self.list = list_data

        # accept any dict with kwargs
        self.__dict__.update(kwargs)
        if 'transaksi_header' in kwargs:
            self.transaksi_header = kwargs.get("transaksi_header")

    def json(self):
        out_json = {
            "message_id": self.message_id,
            "status": self.status,
            "list": self.list
        }
        return json.dumps(out_json, cls=JSONEncoder)

    def dict(self):
        out_dict = {
            "message_id": self.message_id,
            "status": self.status,
            "list": row2dict(self.list)
        }
        return out_dict

    def failed_resp(self, custom_message=None):
        self.message_id = "01"
        self.status = custom_message if custom_message is not None else "Failed, something went wrong..."


class ResponseOutFailed(ResponseOutCustom):
    def __init__(self, message_id="01", status="Failed, data not found", list_data=None, **kwargs):
        super().__init__(message_id, status, list_data, **kwargs)


class ResponseOutSuccess(ResponseOutCustom):
    def __init__(self, list_data, message_id="00", status="Success, data found", **kwargs):
        super().__init__(message_id, status, list_data, **kwargs)


class ResponseDBTimeOut(ResponseOutCustom):
    def __init__(self, list_data=None, message_id="02", status=" DB transaction was timed out...", **kwargs):
        super().__init__(message_id, status, list_data, **kwargs)


class ResponseDBError(ResponseOutCustom):
    def __init__(self, list_data=None, message_id="02", status="Failed, something wrong rollback DB transaction...",
                 **kwargs):
        super().__init__(message_id, status, list_data, **kwargs)


class MessageResponseOutTypes(str, Enum):
    HTTP_200_OK = "[{}-{}] The server successfully receives the request. {}."
    HTTP_40X_FAILED = "[{}-{}] Failed something went wrong, {}."
    HTTP_500_INTERNAL_SERVER_ERROR = "[{}-500] [ {}:{} ] Failed, The server encountered " \
                                     "an error while processing your request and failed."
    HTTP_502_BAD_GATEWAY = "[{}-502] Failed, The load balancer or web server has trouble " \
                           "connecting to the {} app. Please try the request again."
    HTTP_503_SERVICE_UNAVAILABLE = "[{}-503] Failed, The service is temporarily unavailable. " \
                                   "Please try the request again. "
    HTTP_403_FORBIDDEN = "[{}-403] Failed, Either the user is attempting to perform an action without " \
                         "having privileges to access them or the login credentials are correct."
    HTTP_408_REQUEST_TIMEOUT = '[{}-408] Failed, the connection to server was timeout.'
    HTTP_401_UNAUTHORIZED = '[{}-401] Failed, it was unauthorized access, check {} credentials token.'
    HTTP_429_TOO_MANY_REQUESTS = '[{}-429] Failed, too many request. Please try again.'
    HTTP_TEXT_PLAIN = '[{}-{}] Failed, {}'


class ResponseOutServices(ResponseOutCustom):
    """
    This class invoke in core.py, it will parsed http response
    from services and will return client response in clean way.
    :rtype ResponseOutCustom
    """

    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name  # MAMBU or TPS

    def success(self, http_code, list_data, resp_description):
        return ResponseOutCustom(message_id="00",
                                 status=MessageResponseOutTypes.HTTP_200_OK.value.format(self.service_name,
                                                                                         http_code,
                                                                                         resp_description),
                                 list_data=list_data,
                                 http_code=http_code)

    def failed(self, http_code, resp_description):
        return ResponseOutCustom(message_id="01",
                                 status=MessageResponseOutTypes.HTTP_40X_FAILED.value.format(self.service_name,
                                                                                             http_code,
                                                                                             resp_description),
                                 http_code=http_code
                                 )

    def internal_server_error(self, error_code, resp_description):
        return ResponseOutCustom(message_id="02",
                                 status=MessageResponseOutTypes.HTTP_500_INTERNAL_SERVER_ERROR.value.format(
                                     self.service_name, error_code, resp_description), http_code=500)

    def bad_gateway(self):
        return ResponseOutCustom(message_id="02",
                                 status=MessageResponseOutTypes.HTTP_502_BAD_GATEWAY.value.format(self.service_name,
                                                                                                  self.service_name),
                                 http_code=502)

    def service_unavailable(self):
        return ResponseOutCustom(message_id="02",
                                 status=MessageResponseOutTypes.HTTP_503_SERVICE_UNAVAILABLE.value.format(
                                     self.service_name),
                                 http_code=503)

    def forbidden(self):
        return ResponseOutCustom(message_id="02",
                                 status=MessageResponseOutTypes.HTTP_403_FORBIDDEN.value.format(self.service_name),
                                 http_code=403
                                 )

    def request_timeout(self):
        return ResponseOutCustom(message_id="02",
                                 status=MessageResponseOutTypes.HTTP_408_REQUEST_TIMEOUT.value.format(
                                     self.service_name),
                                 http_code=408)

    def unauthorized(self):
        return ResponseOutCustom(message_id="02",
                                 status=MessageResponseOutTypes.HTTP_401_UNAUTHORIZED.value.format(self.service_name,
                                                                                                   self.service_name),
                                 http_code=401)

    def too_many_request(self):
        return ResponseOutCustom(message_id="02",
                                 status=MessageResponseOutTypes.HTTP_429_TOO_MANY_REQUESTS.value.format(
                                     self.service_name),
                                 http_code=429)

    def text_plain(self, http_code, resp_description):
        return ResponseOutCustom(message_id="02",
                                 status=MessageResponseOutTypes.HTTP_TEXT_PLAIN.value.format(self.service_name,
                                                                                             http_code,
                                                                                             resp_description),
                                 http_code=500)


# Does quasi the same things as json.loads from here: https://pypi.org/project/dynamodb-json/
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


# SQLAlchemy row to dictionary
def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d

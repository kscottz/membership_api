import datetime
from enum import Enum
import json

from decimal import Decimal
from flask import Response
import logging

from flask.json import JSONEncoder
from sqlalchemy.ext.declarative import DeclarativeMeta
from typing import List

logger = logging.getLogger(__name__)


class BadRequest(Response):
    def __init__(self, err: str) -> None:
        payload = {'status': 'failed', 'err': err}
        super(BadRequest, self).__init__(
            json.dumps(payload), status=400, mimetype='application/json')


def new_alchemy_encoder(fields_to_expand: List[str]=[]):
    _visited_objs = []  # type: List[DeclarativeMeta]

    class AlchemyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj.__class__, DeclarativeMeta):
                if obj in _visited_objs:
                    return None
                _visited_objs.append(obj)

                # go through each field in this SQLalchemy class
                fields = {}
                for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                    val = obj.__getattribute__(field)
                    if callable(val):
                        continue
                    if isinstance(val, Enum):
                        val = val.name
                    # is this field another SQLalchemy object, or a list of SQLalchemy objects?
                    elif isinstance(val.__class__, DeclarativeMeta) \
                            or (isinstance(val, list) and len(val) > 0  # NOQA
                                and isinstance(val[0].__class__, DeclarativeMeta)):  # NOQA
                        if field not in fields_to_expand:
                            # not expanding this field: set it to None and continue
                            continue

                    fields[field] = val
                # a json-encodable dict
                return fields

            return json.JSONEncoder.default(self, obj)

    return AlchemyEncoder


class CustomEncoder(JSONEncoder):
    """ Custom encoder class converts Decimals to strings and datetime objects into ISO
    ISO formatted strings. """

    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        return JSONEncoder.default(self, obj)


def custom_jsonify(data, encoder, status=200) -> Response:
    return Response(
        status=status, response=json.dumps(
            data, cls=encoder), content_type='application/json')

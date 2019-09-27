from datetime import datetime, timedelta

from pulsar import Function
from pulsar.schema import AvroSchema

from pipeline_utils import model_class_factory
from redis import Redis

class WindowCount(Function):
    """a sorted list for each key is stored on redis"""
    def process(self, input, context):
        config = context.user_config
        state = Redis(config['state_server'], port=config['state_port'], db=config['state_id'])
        RecordClass = model_class_factory(**config['schema'])
        record = RecordClass.decode(input)
        # Retrieve the `key` of the current input
        key = getattr(record, config['key_by'])
        date_field = config.get('date_field', 'date')
        date_format = config.get('date_format', '%Y-%m-%d %H:%M:%S')
        t_last = datetime.strptime(getattr(record, date_field), date_format)
        t_start = t_last - timedelta(seconds=config['window'])
        stamp_last = t_new.timestamp()
        stamp_start = t_start.timestamp()
        state.lpush(key, stamp_last)
        while True:
            tail = state.rpop(key)
            if tail is None:
                break
            if int(tail) > t_start:
                state.rpush(tail)
                break
        ResultClass = model_class_factory(**config['output_schema'])
        result = RecordClass.clone_from(record)
        setattr(result, config['output_field'], state.llen(key))
        return result.encode()

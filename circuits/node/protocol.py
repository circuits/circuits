from circuits import Component, handler
from circuits.core import Value
from circuits.net.events import write

from .utils import dump_event, dump_value, load_event, load_value

DELIMITER = b'~~~'


class Protocol(Component):
    __buffer = b''
    __nid = 0
    __events = {}

    def init(self, sock=None, server=None, **kwargs):
        self.__server = server
        self.__sock = sock
        self.__receive_event_firewall = kwargs.get('receive_event_firewall',
                                                   None)
        self.__send_event_firewall = kwargs.get('send_event_firewall', None)

    def add_buffer(self, data=''):
        if data:
            self.__buffer += data

        packets = self.__buffer.split(DELIMITER)
        self.__buffer = b''

        for packet in packets:
            try:
                self.__process_packet(packet)
            except ValueError:
                self.__buffer = packet

    @handler(channel='node_result', priority=100)
    def result_handler(self, event, *args, **kwargs):
        if event.name.endswith('_success'):
            source_event = args[0]

            if getattr(args[0], 'node_call_id', False) is not False:
                self.send_result(source_event.node_call_id, source_event.value)

    def send(self, event):
        if self.__send_event_firewall and \
                not self.__send_event_firewall(event, self.__sock):
            yield Value(event, self)

        else:
            id = self.__nid
            self.__nid += 1

            packet = dump_event(event, id).encode('utf-8') + DELIMITER
            self.__send(packet)

            if not getattr(event, 'node_without_result', False):
                self.__events[id] = event
                while not hasattr(self.__events[id], 'remote_finish'):
                    yield

                del (self.__events[id])
                yield event.value

    def send_result(self, id, value):
        value.node_call_id = id
        value.node_sock = self.__sock
        packet = dump_value(value).encode('utf-8') + DELIMITER
        self.__send(packet)

    def __send(self, packet):
        if self.__server is not None:
            self.fire(write(self.__sock, packet))
        else:
            self.fire(write(packet))

    def __process_packet(self, packet):
        packet = packet.decode('utf-8')

        if '"value":' in packet:
            self.__process_packet_value(packet)

        else:
            self.__process_packet_call(packet)

    def __process_packet_call(self, packet):
        event, id = load_event(packet)

        if self.__receive_event_firewall and \
                not self.__receive_event_firewall(event, self.__sock):
            self.send_result(id, Value(event, self))
        else:
            event.success = True  # fire %s_success event
            event.success_channels = ('node_result',)
            event.node_call_id = id
            event.node_sock = self.__sock

            # convert byte to str
            event.args = [arg.decode('utf-8') if isinstance(arg, bytes) else
                          arg for arg in event.args]

            for i in event.kwargs:
                v = event.kwargs[i]
                index = i.decode('utf-8') if isinstance(i, bytes) else i
                value = v.decode('utf-8') if isinstance(v, bytes) else v

                del (event.kwargs[i])
                event.kwargs[index] = value

            self.fire(event, *event.channels)

    def __process_packet_value(self, packet):
        value, id, error, meta = load_value(packet)

        if id in self.__events:
            # convert byte to str
            value = value.decode(
                'utf-8') if isinstance(value, bytes) else value
            error = error.decode(
                'utf-8') if isinstance(error, bytes) else error

            if not hasattr(self.__events[id], 'value') \
                    or not self.__events[id].value:
                self.__events[id].value = Value(self.__events[id], self)

            # save result
            self.__events[id].value.setValue(value)
            self.__events[id].errors = error
            self.__events[id].remote_finish = True

            for k, v in dict(meta).items():
                setattr(self.__events[id], k, v)

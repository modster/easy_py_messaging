import zmq
import sys
import os
import threading
import time
import signal


class ServerCreateClass(threading.Thread):
    """
    Create a server class that receives requests and
    sends server responses.
    Modeled after asyncsrv.py in the ZeroMQ zguide.
    """

    def __init__(self, config):
        """
        config as a dictionary describes the client configuration.
        All but id_name keywords are required.

        id_name = These names appear in the log entry as 
            an identifier of the source
            of the log entry.

        port = port to use for communications.

        host = name of host. For servers, this may commonly be '*'
            For clients, this may be 'localhost' or a node name.

        scheme = Typically 'tcp' or 'udp'.
        """

        threading.Thread.__init__(self)
        self.config = config
        self.workers = []   # Thread the workers are on.


    def demandIntKey(self, key):
        """Insist that key be in the config dict.
        Return the valid in the config dict."""
        if self.config[key] is None:
            sys.stdout.write('"%s" required, not found in ClientCreateClass.\n'
                    % key)
            traceback.print_exc()
            sys.exit(1)

        # Insist the key is an integer
        try:
            port = int(self.config['port'])
        except ValueError as err:
            sys.stdout.write('port "%s" must be an integer.\n' % 
                    str(self.config['port']))
            sys.exit(1)
        return port

    def run(self):
        context = zmq.Context()
        frontend = context.socket(zmq.ROUTER)
        port = self.demandIntKey('port')
        endpoint = '%s://*:%s' % (self.config['scheme'], str(port))
        print 'endpoint: "%s"\n' % endpoint
        frontend.bind(endpoint)

        backend = context.socket(zmq.DEALER)
        backend.bind('inproc://backend')

        self.config['context'] = context

        # Spawn some worker threads
        for i in range(1):
            worker = ServerWorker(self.config)
            worker.start()
            self.workers.append(worker)

        zmq.proxy(frontend, backend)

        frontend.close()
        backend.close()
        context.term()

class ExitException(Exception):
    pass

signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGTERM, signal.SIG_DFL)

is_alive = True

class ServerWorker(threading.Thread):
    """ServerWorker"""
    def __init__(self, config):
        threading.Thread.__init__(self)
        self.context = config['context']
        self.config = config

    def run(self):
        global is_alive
        worker = self.context.socket(zmq.DEALER)
        worker.connect('inproc://backend')
        while is_alive:
            ident, msg = worker.recv_multipart()
            response = self.config['in_fcn'](ident, msg)
            ident, resp_msg = response
            worker.send_multipart([ident, resp_msg])
            if '@EXIT' in resp_msg:
                is_alive = False
                break

        worker.close()
        print 'worker closed'
        os.kill(os.getpid(), signal.SIGINT)


def handle_request(ident, msg):
    """
    Handler for incoming messages.
    This processes the client message and forms
    a response. In this test case, the response
    mostly echos the request.
    ident must not be changed.
    msg may become transformed into whatever.
    """
    return ident, msg + '_resp'


def main():
    """main function"""
    global is_alive
    import platform
    # Default port for this dummy test.
    port = 5590
    config = {
        'scheme': 'tcp',
        'host': 'localhost',
        'port': port,
        'in_fcn': handle_request,
        'id_name': platform.node()
    }
    server = ServerCreateClass(config)
    server.start()

    while is_alive:
        server.join(1)


if __name__ == "__main__":
    main()
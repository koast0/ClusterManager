import time, signal
from tornado import web, ioloop, options, httpserver

_SHUTDOWN_TIMEOUT = 15


def MakeSaflyShutdown(server, db, worker1, worker2):
    io_loop = server.io_loop or ioloop.IOLoop.instance()
    def stop_handler(*args, **keywords):
        print(" SHUTDOWNING SERVER... It may take some time")
        worker1.finish()
        worker2.finish()
        def shutdown():
            server.stop()
            deadline = time.time() + _SHUTDOWN_TIMEOUT
            def stop_loop():
                now = time.time()
                if now < deadline and (io_loop._callbacks or io_loop._timeouts):
                    io_loop.add_timeout(now + 1, stop_loop)
                else:
                    io_loop.stop()
            stop_loop()
        io_loop.add_callback(shutdown)
        worker1.join()
        worker2.join()
        db.Finish()
    signal.signal(signal.SIGQUIT, stop_handler) 
    signal.signal(signal.SIGTERM, stop_handler) 
    signal.signal(signal.SIGINT, stop_handler)

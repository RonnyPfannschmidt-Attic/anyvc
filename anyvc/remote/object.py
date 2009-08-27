"""
    anyvc.remote.object
    ~~~~~~~~~~~~~~~~~~~

    convience tool make execnet channels remote objects
"""
import pickle


class RemoteCaller(object):
    def __init__(self, channel):
        self.channel = channel

    def _call_method(self, name, *k, **kw):
        print 'calling', name, k, kw, 'on', self.channel
        assert not self.channel.isclosed()
        data = pickle.dumps((name, k, kw))
        self.channel.send(data)
        print self.channel.receive()
        result = self.channel.receive()
        if isinstance(result, str):
            return pickle.loads(result)
        else:
            return result

    def __getattr__(self, name):
        def method(*k, **kw):
            return self._call_method(name, *k, **kw)
        method.__name__ = name
        return method

class RemoteHandler(object):
    def __init__(self, channel):
        self.channel = channel
        channel.setcallback(self._channel_callback)

    def newchannel(self):
        return self.channel.gateway.newchannel()

    def _channel_callback(self, data):
        try:
            method, k, kw = pickle.loads(data)
            method = getattr(self, method)
            result = method(*k, **kw)
            self.channel.send(str(type(result)))
            import __main__
            if not isinstance(result, __main__.Channel):
                send = pickle.dumps(result)
            else:
                send = result
            self.channel.send(send)
        except Exception, e :
            import traceback
            import sys
            excinfo = sys.exc_info()
            l = traceback.format_exception(*excinfo)
            errortext = "".join(l)
            self.channel.close(errortext)
        except:
            self.channel.close('unknown error')



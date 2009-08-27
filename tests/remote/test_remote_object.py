from py.execnet import makegateway
from anyvc.remote.object import RemoteCaller
def test_remote_object():
    gw = makegateway('popen')
    channel = gw.remote_exec("""
    from anyvc.remote.object import RemoteHandler

    class TestHandler(RemoteHandler):
        def test(self, **kw):
            return kw
    newchan = channel.gateway.newchannel()
    handler = TestHandler(newchan)
    channel.send(newchan)
    """)
    caller = RemoteCaller(channel.receive())
    result = caller.test(a=1)
    assert result == {'a':1}

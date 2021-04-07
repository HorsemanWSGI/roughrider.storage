from reiter.events import registry


def test_subscribers():
    reg = registry.Subscribers()

    @reg.subscribe('test')
    def test():
        pass

    assert reg['test'] == test
    assert reg.getall('test') == [test]

    @reg.subscribe('test')
    def test2():
        pass

    assert reg['test'] == test  # always the first
    assert reg.getall('test') == [test, test2]


def test_subscribers_add():
    reg1 = registry.Subscribers()
    reg2 = registry.Subscribers()

    @reg1.subscribe('test')
    def test():
        pass

    @reg2.subscribe('test')
    def test2():
        pass

    reg3 = reg1 + reg2
    assert reg3.getall('test') == [test, test2]


def test_subscribers_notification():
    reg = registry.Subscribers()
    called = []

    @reg.subscribe('test')
    def test():
        called.append('test')

    @reg.subscribe('test')
    def test2():
        called.append('test2')

    reg.notify('test')
    assert called == ['test', 'test2']


def test_subscribers_interruption():
    reg = registry.Subscribers()
    called = []

    @reg.subscribe('test')
    def test():
        called.append('test')
        return True

    @reg.subscribe('test')
    def test2():
        called.append('test2')

    reg.notify('test')
    assert called == ['test']

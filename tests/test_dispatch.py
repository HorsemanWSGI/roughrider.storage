from reiter.events.meta import EventsCenter
from reiter.events.dispatcher import Dispatcher


class Application(EventsCenter):
    pass


class Item:
    def __init__(self, _type):
        self._type = _type


class ItemTypeDispatcher(Dispatcher):

    def dispatch(self, item, **kwargs):
        return item._type


def test_no_dispatch():
    app = Application()
    mc = ItemTypeDispatcher()

    app.subscribe('object_added')(mc)
    app.notify('object_added', Item('car'))


def test_dispatch():
    app = Application()
    mc = ItemTypeDispatcher()
    app.subscribe('object_added')(mc)

    found = []

    @mc.subscribe('car')
    def only_for_car(item, **kwargs):
        found.append('I have a car.')

    assert list(mc.dispatch_keys) == ['car']

    app.notify('object_added', Item('bus'))
    assert found == []

    app.notify('object_added', Item('car'))
    assert found == ['I have a car.']


def test_messaging_example():

    class User:
        def __init__(self, **preferences):
            self.preferences = preferences
            self.events = []

    class MessageDispatcher(Dispatcher):

        def dispatch(self, user, message):
            return user.preferences['messaging']

    app = Application()
    mc = MessageDispatcher()
    app.subscribe('object_added')(mc)

    @mc.subscribe('sms')
    def sms_messaging(user, message):
        user.events.append(f'I send you a SMS: {message}')

    @mc.subscribe('Webpush')
    def webpush_messaging(user, message):
        user.events.append(f'I send you a webpush: {message}')


    user = User(messaging='sms')
    app.notify('object_added', user, message='This is a message')
    assert user.events == ['I send you a SMS: This is a message']

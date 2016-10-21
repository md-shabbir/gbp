from gbpservice.nfp.core_ahmed import event as nfp_event
from gbpservice.nfp.core_ahmed import module as nfp_api
from gbpservice.nfp.utils.forked_pdb import ForkedPdb
import time
Event = nfp_event.Event
mypolleventg = None

class EventHandler(nfp_api.NfpEventHandler):
    def __init__(self, controller, config):
        self._controller = controller
        self._config = config

    def handle_event(self, event):
        print 'handle event'
        self._controller.event_complete(event)

    @nfp_api.poll_event_desc(event='MY_POLL_EVENT', spacing=1)
    def my_poll_event(self, event):
        print 'polling...'

    def event_cancelled(self, event, reason):
        print 'cancelled: ', reason


def nfp_module_init(controller, config):
    event_handler = EventHandler(controller, config)
    events = ['MY_POLL_EVENT', 'MY_POLL_EVENT_STOP']
    register_events = []
    register_events.append(Event(id='MY_POLL_EVENT', handler=event_handler))
    register_events.append(Event(id='MY_POLL_EVENT_STOP', handler=event_handler))
    
    controller.register_events(register_events) 

def nfp_module_post_init(controller, config):
    mypollevent = controller.new_event(id='MY_POLL_EVENT', data={})
    controller.poll_event(mypollevent, max_times=8)
    time.sleep(8)
    stop_event = controller.new_event(id='MY_POLL_EVENT_STOP', data={'key':mypollevent.desc.uuid})
    stop_event.desc.stop_poll_event = True
    print 'sent stop poll event: ', mypollevent.desc.uuid
    controller.post_event(stop_event)

    mypollevent = controller.new_event(id='MY_POLL_EVENT', data={})
    controller.poll_event(mypollevent, max_times=8)
    time.sleep(8)
    stop_event = controller.new_event(id='MY_POLL_EVENT_STOP', data={'key':mypollevent.desc.uuid})
    stop_event.desc.stop_poll_event = True
    print 'sent stop poll event: ', mypollevent.desc.uuid
    controller.post_event(stop_event)
 

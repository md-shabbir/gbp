from gbpservice.nfp.core_ahmed import event as nfp_event
from gbpservice.nfp.core_ahmed import module as nfp_api


Event = nfp_event.Event


class EventHandler(nfp_api.NfpEventHandler):
    def __init__(self, controller, config):
        self._controller = controller
        self._config = config


    def handle_event(self, event):
        print "====== %s ======" %(event.identify())
        if event.id == 'TOM_WATCHING_TV' or event.id == 'B21POLL' or event.id == 'B2111POLL' or event.id == 'B3POLL' or event.id == 'B31POLL':
            event.data = [event.desc.uuid]
            self._controller.poll_event(event, max_times=3)
        else:
            self._controller.event_complete(event)

    @nfp_api.poll_event_desc(event='TOM_WATCHING_TV', spacing=2)
    def poll_tom_watching_tv(self, event):
        print "===== Polling - TOM_WATCHING_TV ====="

    @nfp_api.poll_event_desc(event='B21POLL', spacing=2)
    def poll_b21poll(self, event):
        print "===== Polling - B21POLL ====="

    @nfp_api.poll_event_desc(event='B2111POLL', spacing=2)
    def poll_b2111poll(self, event):
        print "===== Polling - B2111POLL ====="

    @nfp_api.poll_event_desc(event='B3POLL', spacing=2)
    def poll_b3poll(self, event):
        print "===== Polling - B3POLL ====="

    @nfp_api.poll_event_desc(event='B31POLL', spacing=2)
    def poll_b31poll(self, event):
        print "===== Polling - B31POLL ====="
    
 
    def event_cancelled(self, event, reason):
        #print '################# ID: ', event.id, reason
        if event.id == 'TOM_WATCHING_TV' or event.id == 'B21POLL' or event.id == 'B2111POLL' or event.id == 'B3POLL' or event.id == 'B31POLL':
            print "@@@@@ %s is cancelled @@@@@" % event.id
            event.desc.uuid = event.data[0]
            self._controller.event_complete(event, result='SUCCESS')

def nfp_module_init(controller, config):
    register_events = []
    event_handler = EventHandler(controller, config)
    events = ['BED_TIME', 'TOM','TOM_PREPARE_FOOD', 'TOM_EATING_FOOD', 'TOM_WATCHING_TV', 'TOM_POWER_ON_TV', 'JERRY', 'JERRY_ORDERED_FOOD', 'JERRY_FOOD_DELIVERED', 'JERRY_EATING_FOOD', 'JERRY_WATCHING_TV', 'BOB', 'B1', 'B11', 'B111', 'B1111', 'B1112', 'B12', 'B121', 'B2', 'B21POLL', 'B211', 'B2111POLL', 'B22', 'B23', 'B3POLL', 'B31POLL', 'B32']
    for event in events:
        register_events.append(
            Event(id=event, handler=event_handler))
    controller.register_events(register_events)




def nfp_module_post_init(controller, config):
    bed_time_event = controller.new_event(id='BED_TIME', data={})
    tom_event = controller.new_event(id='TOM', data={})
    tom_prepare_food_event = controller.new_event(id='TOM_PREPARE_FOOD', serialize=True, binding_key='prepare_and_eat', data={})
    tom_eating_food_event = controller.new_event(id='TOM_EATING_FOOD', serialize=True, binding_key='prepare_and_eat', data={})
    tom_watching_tv_event = controller.new_event(id='TOM_WATCHING_TV',serialize=True, binding_key='prepare_and_eat', data={})
    tom_power_on_tv_event = controller.new_event(id='TOM_POWER_ON_TV', data={})
    jerry_event = controller.new_event(id='JERRY', data={})
    jerry_ordered_food_event = controller.new_event(id='JERRY_ORDERED_FOOD', data={})
    jerry_food_delivered_event = controller.new_event(id='JERRY_FOOD_DELIVERED', serialize=True, binding_key='wait_on_delivery', data={})
    jerry_eating_food_event = controller.new_event(id='JERRY_EATING_FOOD', serialize=True, binding_key='wait_on_delivery', data={})
    jerry_watching_tv_event = controller.new_event(id='JERRY_WATCHING_TV', serialize=True, binding_key='wait_on_delivery', data={})

    bob_event = controller.new_event(id='BOB', data={})
    b1_event = controller.new_event(id='B1', data={})
    b11_event = controller.new_event(id='B11', data={})
    b111_event = controller.new_event(id='B111', data={})
    b1111_event = controller.new_event(id='B1111', data={})
    b1112_event = controller.new_event(id='B1112', data={})
    b12_event = controller.new_event(id='B12', data={})
    b121_event = controller.new_event(id='B121', data={})

    b2_event = controller.new_event(id='B2', serialize=True, binding_key='b2_b3',data={})
    b21poll_event = controller.new_event(id='B21POLL', data={})
    b211_event = controller.new_event(id='B211', data={})
    b2111poll_event = controller.new_event(id='B2111POLL', data={})
    b22_event = controller.new_event(id='B22', data={})
    b23_event = controller.new_event(id='B23', data={})

    b3poll_event = controller.new_event(id='B3POLL', serialize=True, binding_key='b2_b3', data={})
    b31poll_event = controller.new_event(id='B31POLL', data={})
    b32_event = controller.new_event(id='B32', data={})



    GRAPH = \
    {
        bed_time_event: [tom_event, jerry_event, bob_event],
        tom_event: [tom_prepare_food_event, tom_eating_food_event, tom_watching_tv_event],
        tom_watching_tv_event: [tom_power_on_tv_event],
        jerry_event: [jerry_food_delivered_event, jerry_eating_food_event, jerry_watching_tv_event],
        jerry_food_delivered_event: [jerry_ordered_food_event],
        bob_event: [b1_event, b2_event, b3poll_event],
        b1_event: [b11_event, b12_event],
        b11_event: [b111_event],
        b111_event: [b1111_event, b1112_event],
        b12_event: [b121_event],
        b2_event: [b21poll_event, b22_event, b23_event],
        b21poll_event: [b211_event],
        b211_event: [b2111poll_event],
        b3poll_event: [b31poll_event, b32_event]
    }

    controller.post_graph(GRAPH, bed_time_event, graph_str='TOM_AND_JERRY_GRAPH')

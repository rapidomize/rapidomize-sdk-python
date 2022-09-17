import rapidomize
import logging

# Following examples show how to use the node js sdk, for triggering ICApps and tracking events for telematics/telemetry/analytics
APP_ID =''
TOKEN= ''
ICAPP_ID=''

class LifeCycleHandler:
    def ack(res):
        logging.info('res', res)
    def err(err):
        logging.info('err', err)


""" initialize the library with appId and token """
rapidomize.init(APP_ID, TOKEN)

""" set a session information for event tracking """
rapidomize.setSession('123qwe', 'user123')       
""" track an event """
rapidomize.event('register', {
'type': 'click',
'wait': '160s'
}, ICAPP_ID)

rapidomize.trigger(ICAPP_ID, {
    "to": 'sample@abc.com',  
    "from": 'noreply@my-site.com',
    "subject": 'Test Subject',
    "body": 'Test body'
}, LifeCycleHandler())





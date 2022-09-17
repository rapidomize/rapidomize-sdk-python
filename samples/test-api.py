import logging
import rapidomize

logging.basicConfig(level=logging.DEBUG)

# Following examples show how to use the node js sdk, for triggering ICApps and tracking events for telematics/telemetry/analytics
APP_ID =''
TOKEN= ''
ICAPP_ID=''

class LifeCycleHandler:
    def suc(self, res):
        print(res)
    def err(self, err):
        print(err)

handler = LifeCycleHandler()


""" initialize the library with appId and token """
rapidomize.init(APP_ID, TOKEN)
#Test REST API GET operation for endpoint path & query '/rows?rng=A1:K1&st=5'
#rapidomize.get('/rows?rng=A1:K1&st=5', ICAPP_ID, handler)


#Test REST API POST operation for endpoint path  '/rows'
rapidomize.post('/rows', {"aa":"bbbbbbbbb", "cc":"dddddddddddd"}, ICAPP_ID, handler)


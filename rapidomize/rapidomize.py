#
# Copyright (c) 2018-2022, Rapidomize.
#
# Licensed under the Apache License, Version 2.0 (the "License") you may not use this file except
# in compliance with the License. You may obtain a copy of the License at http:#www.apache.org/licenses/LICENSE-2.0
#
# OR contact:
# contact@rapidomize.com
# 
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under
# the License.
#

import logging
import asyncio
import httpx
import base64

EP_HOST='ics.rapidomize.com'
# EP_HOST='localhost' #for dev testing
APP_PATH='/api/v1/mo/'
AGW_PATH='/api/v1/agw/'

_icappId=None
_options = {}
_basePath=None
_store=None
_nde=False
_headers = None

#logging.basicConfig(level=logging.INFO)
#
# Initialize rapidomize and creates a client to remotely interact with Rapidomize server/cloud platform. 
# 
# @param String appId   App/Device ID
# @param String token   App/Device Token
# @param String icappId (optional) ICApp ID to use in event tracking for analytics against a given ICApp
# @param Object options (optional) additional options 
#                         
#                          'session': true  => include session data for all ICApp triggers
#                         
# 
# 
#
def init(appId, token, icappId=None, options=None):
    global _appId, _icappId, _options, _basePath, _store
    if((appId == None) or (len(appId) > 60) or (token == None) or (EP_HOST == None) or (APP_PATH == None) or (AGW_PATH == None)):
        return _err('Failed to initialize rapidomize!!')

    _appId = appId
    _icappId = icappId
    _options =  options

    _hdr(token)
    _basePath = APP_PATH + appId
    _store = {}


#
# If you are expecting response from your ICApp then you must provide a callback handler to receive response.
# 
# Default callback handler.
# 
#
class LifeCycleHandler:
    """
    Receive response from the server/cloud platform.  
    
    @param Object res response data
    
    """
    def suc(self, res):
        pass

    """
    if in case of an error. Error msg err description is found under err attribute
    e.g. err: 'reason ..', status:'status text'
     
    @param Object err in case of error
    """
    def err(self, err):
        pass


HttpMethod = {
    "GET":'GET',
    "POST":'POST',
    "PUT":'PUT',
    "PATCH":'PATCH',
    "DELETE": 'DELETE'
}

#
# Trigger an ICApp with input JSON data
#
# @param String icappId ICApp ID
# @param Object data inbound data for the ICApp, is either a object or an array of objects. 
#                      For bulk operations you can send data as an array of objects. ICApp will be triggered for each object in the array.
# @param LifeCycleHandler handler callback handler see above
#
def trigger(icappId, data, handler):
    global _basePath
    if(_basePath):
        return _err('Rapidomize is not initialized!')
    

    icappId = icappId if icappId is not None else _icappId
    if(icappId is None or icappId.length > 60):
        return _err('missing req params ICApp ID ' + icappId)
    

    reqdata = data
    if(_options['session']):
        session = _getSession()
        if (session is None or session.sessionId is None and session.userId is None):
            return _err('invalid session - call setSession() before using')
        

        reqdata = session.update(data)
    

    path = _basePath + "/icapp/" + icappId

    _send(HttpMethod.POST, path, reqdata, handler)

#
# Convenient method to invoke user defined GET REST API
# 
# @param String path 
# @param LifeCycleHandler handler callback handler see above
#
def get(path, icappId=None, handler=None):
    gwpath = _gwpath(path, icappId)
    if(gwpath is None):
        return
    _send(HttpMethod['GET'], gwpath, None, handler)


#
# Convenient method to invoke user defined POST REST API
# 
# @param String path 
# @param Object data inbound data for the ICApp, is either a object or an array of objects. 
#                      For bulk operations you can send data as an array of objects. ICApp will be triggered for each object in the array.
# @param LifeCycleHandler handler callback handler see above
#
def post(path, data, icappId=None, handler=None):
    gwpath = _gwpath(path, icappId)
    if(gwpath is None):
        return
    _send(HttpMethod['POST'], gwpath, data, handler)


#
# Convenient method to invoke user defined PUT REST API
# 
# @param String path 
# @param Object data inbound data for the ICApp, is either a object or an array of objects. 
#                      For bulk operations you can send data as an array of objects. ICApp will be triggered for each object in the array.
# @param LifeCycleHandler handler callback handler see above
#
def put(path, data, icappId=None, handler=None):
    gwpath = _gwpath(path, icappId)
    if(gwpath is None):
        return
    _send(HttpMethod['PUT'], gwpath, data, handler)

#
# Convenient method to invoke user defined DELETE REST API
# 
# @param String path 
# @param Object data inbound data for the ICApp, is either a object or an array of objects. 
#                      For bulk operations you can send data as an array of objects. ICApp will be triggered for each object in the array.
# @param LifeCycleHandler handler callback handler see above
#
def delete(path, data, icappId=None, handler=None):
    gwpath = _gwpath(path, icappId)
    if(gwpath is None):
        return
    _send(HttpMethod['DELETE'], gwpath, data, handler)



#
# Setup session data for event tracking for analytics
# 
# @param String sessionId  - a unique id to identify the a given session
# @param String userId - (optional) anonymous user ID for event tracking for analytics
# @param Object userProps - (optional) other use properties to be included
#
def setSession(sessionId, userId = None, userProps = None):
    session = {'sessionId': sessionId}

    if (userId):
        session['userId'] = userId
    if (userProps):
        session['userProps'] = userProps

    _store.update("rapidomize-session", session)


#
# clear session data
#
def clearSession():
    _store.delete("rapidomize-session")



#
# For analytics purpose, track webapp user events such as button clicks and send event data to your ICApp for analysis.
# Prior to executing this function, it is required to setup session information by calling setSession().
# 
# @param String eventName  any unique name which can be used to identify an event
# @param Object properties OPTIONAL dictionary object which can be used to attach any properties associated with the event
# @param String icappId ICApp ID, this is optional if already provided when initializing library by calling init(..., icappId,..)
# 
# @return none
#
def event(eventName, properties = None, icappId = None):
    if(_basePath is None):
         return

    icappId = icappId if icappId is not None else _icappId

    if(icappId is None or icappId.length > 60 or eventName is None):
        return _err('missing req params for event ICAPP ID/ event name ' + icappId + eventName)
    

    ev = {'n': eventName}
    data = None
    if(properties is not None):
        data = properties.update(ev)
    else:
        data = ev 

    session = _getSession()
    if (session is None or session['sessionId'] is None and session['userId'] is None):
        return _err('invalid session - call setSession() before using')


    reqdata = session.update(data)
    path = _basePath + '/icapp/' + icappId
    _send(HttpMethod['POST'], path, reqdata)


def _hdr(token):
    global _headers
    # encoded_u = base64.b64encode(userpass.encode()).decode()
    auth="Basic %s" % base64.b64encode((":"+str(token)).encode()).decode()
    _headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plainq=0.9',
        'Connection': 'keep-alive',
        'Authorization': auth
    }
    #logging.debug(_headers)

def _gwpath(path, icappId):
    if(_basePath is None):
        return _err('Rapidomize is not initialized!')
        
    if(path is None or type(path) is not str or len(path) == 0 or len(path) > 2048):
        return _err('invalid request uri/path')
    

    icappId = icappId if icappId is not None else _icappId
    if(icappId is None or type(icappId) is not str or len(icappId) == 0 or len(icappId) > 60):
        return _err('Invalid icappId!')
    

    if(path[0] != '/'):
        return AGW_PATH + icappId + '/' + path
    else:
        return AGW_PATH + icappId + path
    



#
# internal def to send HTTP request
# 
# @param String icappId 
# @param Object data 
# @param boolean ev 
# 
# @returns 
#

def _send(method, path, data, handler=None):
    asyncio.run(_asend(method, path, data, handler))

async def _asend(method, path, data, handler=None):
    urln = "https://" + EP_HOST + path
    headers = _headers
    # if(method != HttpMethod['GET'] and data is not None):
    #     headers.update({'Content-Length': len(str(data))})
    logging.debug(headers)
    logging.debug(data)
    
    async with httpx.AsyncClient() as client:
        res = await client.request(method, urln, json=data, headers=headers)
        logging.debug(res.headers)
        cnt = res.headers['Content-Type']
        status = res.status_code

        # application/json; utf-8
        _data = None
        if(cnt is not None and res.content is not None and len(res.content) > 0):
            loc = cnt.index(';')
            if(loc > 0): cnt = cnt[0:loc]
            if(cnt == 'text/plain' or cnt == 'text/html'):
                _data = res.text
            elif(cnt == 'application/json'):
                _data = res.json()
        
        logging.debug('body: %s', _data)
        
        if(handler is not None):
            if (status >= 200 and status < 300):
                handler.suc(_data)
                return
            else:
                handler.err(_data)

    
def _getSession():
    ses = _store.get("rapidomize-session")
    return ses

def _err(msg):
    logging.warn(msg)
    # raise Exception(msg)
    return False


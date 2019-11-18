#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Securitas Direct (AKA Verisure EU) control, using mobile api
#       ( based on the great RE work by Xavi (AKA Cebeerre)
#       posted in github.com/Cebeerre/VerisureAPIClient )
# (by segalion at gmail, 20/10/2019)

import time, datetime, requests, json, xmltodict, sys

# All actions based on post:
# https://community.home-assistant.io/t/securitas-direct-verisure-spain/70239/15

SC_ALARM = ('PERI','ARM','ARMNIGHT','ARMDAY','DARM','EST','ARMANNEX','DARMANNEX')
SC_WORK = ('LOGIN','CLS','IDENT','SRV','INS','CONTACT','MYINSTALLATION','ALLINONE'
        ,'CONFIG','PLAN')
SC_DOMO = ('SOMFYSTATUS','SRVDOMO','DOMO','CONFORT','TEMP','HUM','AIRQ','DOOR')
SC_ALL = SC_ALARM + SC_WORK + SC_DOMO + ('IMG','CAMLOG','CAMS','VIDS','VID','UPDCAM'
        ,'CAMPSRS','INSTWORDS','INSTWORDSUPD','INSTWORDSUPD2','BILLS','SECONDUSERS'
        ,'PLANUPD','CONTACTUPD','CONTACTADD','CONTACTDEL','SCHCDDEL','KEY','KEYUPD'
        ,'ACT_V2','PANELCONF','PANELCONFUPD','DEVUPD','ATC','SECRETWORD','INF'
        ,'CALLRING','SCHCDLIST','SCHCDADD','SCHCDUPD','SCHCDDISABLE','REMEMBERUSER'
        ,'MYSD','MYSDCREATE','SRVCOMMDATA','SRVCOMMDATAUPD','SRVCOMMDATAUPD2'
        ,'SECONDUSERADD','SECONDUSERADD2','SECONDUSERDEL','SCHCDPROTECT'
        ,'CAMPAING','CRIALUPD','UPDPUSHSTATUS','SECONDINSTALLADD','SECONDINSTALLADD2'
        ,'THUMBNAIL','UPDPROMPT','DIYRECEIVED','DIYRESEND','DIYCALLME','DIYINIT'
        ,'DIYGETTAMPERS','DIYCHECK','DIYCONTINGENCIA','DIYEXTENDTIME','GETCAPMANT'
        ,'SCHMANT','SENDOTPS','SENDOTP','SECUREACTIONS','SECUREACTION','GCMANT'
        ,'GCCAPACITY','GCCANCELMANT','GCSCHMANT','CTCMFM','GETCONFIGDDI'
        ,'SETCONFIGDDI','SCHLIST','SCHADD','SCHUPD','SCHDEL','SCHLEGAL','SCHNOT'
        ,'SCHUPDONFLY','GETASI','ASILEGAL','BAJAASI','ALTAASI','ASIRES'
        ,'ASISOS','ACOMPGETTIMERS','ACOMPTRACKING','ACOMPCANCEL','GETTRACKERDATA'
        ,'UPDORTRACK','GETONROADKEYDATA','UPDORKEY','NSR','GDPRPOPUP','GDPR','UPDGDPR'
        ,'FIRSTCHGPASS','RESETPASS','RESETPASS2','SENDINST','ALTAWEB','ALTAWEB2'
        ,'LOCKSMITH','ACCEPTLEGALSLOCKSMITH','ASKLOCKSMITH','CANCELLOCKSMITH'
        ,'GETALLLOCKSMITHS','GETSECURITYINFO','CHECKOTP','PENDINGBILLSLIST'
        ,'PAYMENTDATA','PAYMENTEMAIL'
        )

class SecuritasAPIClient():
    BASE_URL='https://mob2217.securitasdirect.es:12010/WebService/ws.do'
    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'

    def __init__(self, user, pwd, country="ES", lang="es" ):
        self._params = {'Country':country, 'user':user, 'pwd':pwd, 'lang':lang
                        ,'request':"", 'ID':""}
        self.alias = ""

    def _set_id(self):
        self._params['ID'] = ('IPH_________________________'
                + self._params['user']
                + datetime.datetime.now().strftime("%Y%m%d%H%M%S") )

    def _api_requests(self, request, **more):
        if 'hash' not in self._params:
            res = self.login()
            if not self._is_ok(res):
                sys.exit(json.dumps(res,indent=2))
        self._params['request'] = request
        if 'ID' not in more: self._set_id()
        resp = requests.get(self.BASE_URL, params={**self._params, **more}
                , timeout=5)
        if resp.status_code == 200:
            return xmltodict.parse(resp.text)
        print(resp, file=sys.stderr)

    def _is_ok(self,res,ok="OK"):
        try:
            return res['PET']['RES']==ok
        except KeyError:
            pass
        return False

    def api_call(self, action, **more):
        if action in SC_ALARM:
            self._api_requests(action+'1')
            res = self._api_requests(action+'2',ID=self._params['ID'])
            for i in range(10):
                if self._is_ok(res,"WAIT"):
                    time.sleep(i+1)
                    res = self._api_requests(action+'2',ID=self._params['ID'])
        else:
            res = self._api_requests(action, **more)
        return res

    def login(self):
        self._params['request'] = "LOGIN"
        self._set_id()
        resp = requests.post(self.BASE_URL, params=self._params, timeout=5)
        if resp.status_code == 200:
            res = xmltodict.parse(resp.text)
            if self._is_ok(res):
                self._params.update({'hash': res['PET']['HASH']})
                res = self._api_requests('INS')
                if self._is_ok(res):
                    inst = res['PET']['INSTALATIONS']['INSTALATION']
                    self._params.update({'numinst':inst['NUMINST'], 'panel':inst['PANEL']})
                    self.alias = inst['ALIAS']
            return res

    def logout(self):
        res = self._api_requests('CLS', numinst="(null)")
        if 'hash' in self._params:
            del self._params['hash']
        return res

    def last_state(self, filter=None):
        if filter is None:
            filter = ('1','2','31','32','46','202','311','13','24','204')
        res = self._api_requests('ACT_V2',timefilter=2,activityfilter=0)
        if self._is_ok(res):
            regs= res['PET']['LIST']['REG']
            # print(json.dumps(regs[0]))
            for reg in regs:
                if reg['@type'] in filter:
                    return reg

if __name__ == '__main__':
    args=sys.argv[1:]
    if len(args) < 2:
        sys.exit(sys.argv[0] + ' User Pass [ACTION] [Country] [Lang]')
    action = args.pop(2) if len(args)>2 else ""
    client = SecuritasAPIClient(*args)
    if action == '':
        out = client.last_state()
    elif action == 'ACT_V2':
        out = client.api_call(action,timefilter=5,activityfilter=0)
    elif action in action in SC_ALL:
        out = client.api_call(action)
    else:
        sys.exit('ACTION must be some of:\n' + str(SC_ALL))
    if "PET" in out and "BLOQ" in out["PET"]: del out["PET"]["BLOQ"]
    print(json.dumps(out,indent=2))

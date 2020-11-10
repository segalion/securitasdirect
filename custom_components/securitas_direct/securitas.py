#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Securitas Direct (AKA Verisure EU) control, using mobile api
#       ( based on the great RE work by Xavi (AKA Cebeerre)
#       posted in github.com/Cebeerre/VerisureAPIClient )
#                                            (by segalion at gmail, 20/10/2019)
#
# Version. 2.0 (10/11/2020). Since 4 Nov 2020 Securitas change API in their 
# server, so old  versions will fail.

import time, datetime, requests, json, xmltodict, sys, base64, logging

# All actions based on post:
# https://community.home-assistant.io/t/securitas-direct-verisure-spain/70239/15

SC_ALARM = ('PERI', 'ARM', 'ARMNIGHT', 'ARMDAY', 'DARM', 'EST', 'ARMANNEX',
            'DARMANNEX', 'IMG')
SC_WORK = ('LOGIN', 'CLS', 'IDENT', 'SRV', 'INS', 'CONTACT', 'MYINSTALLATION',
           'ALLINONE', 'CONFIG', 'PLAN')
SC_DOMO = ('SOMFYSTATUS', 'SRVDOMO', 'DOMO', 'CONFORT', 'TEMP', 'HUM', 'AIRQ',
           'DOOR')
SC_ALL = ('CAMLOG', 'CAMS', 'VIDS', 'VID', 'UPDCAM', 'CAMPSRS', 'INSTWORDS',
          'INSTWORDSUPD', 'INSTWORDSUPD2', 'BILLS', 'SECONDUSERS', 'PLANUPD',
          'CONTACTUPD', 'CONTACTADD', 'CONTACTDEL', 'SCHCDDEL', 'KEY',
          'KEYUPD', 'ACT_V2', 'PANELCONF', 'PANELCONFUPD', 'DEVUPD', 'ATC',
          'SECRETWORD', 'INF', 'CALLRING', 'SCHCDLIST', 'SCHCDADD', 'SCHCDUPD',
          'SCHCDDISABLE', 'REMEMBERUSER', 'MYSD', 'MYSDCREATE', 'SRVCOMMDATA',
          'SRVCOMMDATAUPD', 'SRVCOMMDATAUPD2', 'SECONDUSERADD',
          'SECONDUSERADD2', 'SECONDUSERDEL', 'SCHCDPROTECT', 'CAMPAING',
          'CRIALUPD', 'UPDPUSHSTATUS', 'SECONDINSTALLADD', 'SECONDINSTALLADD2',
          'THUMBNAIL', 'UPDPROMPT', 'DIYRECEIVED', 'DIYRESEND', 'DIYCALLME',
          'DIYINIT', 'DIYGETTAMPERS', 'DIYCHECK', 'DIYCONTINGENCIA',
          'DIYEXTENDTIME', 'GETCAPMANT', 'SCHMANT', 'SENDOTPS', 'SENDOTP',
          'SECUREACTIONS', 'SECUREACTION', 'GCMANT', 'GCCAPACITY',
          'GCCANCELMANT', 'GCSCHMANT', 'CTCMFM', 'GETCONFIGDDI',
          'SETCONFIGDDI', 'SCHLIST', 'SCHADD', 'SCHUPD', 'SCHDEL', 'SCHLEGAL',
          'SCHNOT', 'SCHUPDONFLY', 'GETASI', 'ASILEGAL', 'BAJAASI', 'ALTAASI',
          'ASIRES', 'ASISOS', 'ACOMPGETTIMERS', 'ACOMPTRACKING', 'ACOMPCANCEL',
          'GETTRACKERDATA', 'UPDORTRACK', 'GETONROADKEYDATA', 'UPDORKEY',
          'NSR', 'GDPRPOPUP', 'GDPR', 'UPDGDPR', 'FIRSTCHGPASS', 'RESETPASS',
          'RESETPASS2', 'SENDINST', 'ALTAWEB', 'ALTAWEB2', 'LOCKSMITH',
          'ACCEPTLEGALSLOCKSMITH', 'ASKLOCKSMITH', 'CANCELLOCKSMITH',
          'GETALLLOCKSMITHS', 'GETSECURITYINFO', 'CHECKOTP',
          'PENDINGBILLSLIST', 'PAYMENTDATA', 'PAYMENTEMAIL'
          ) + SC_ALARM + SC_WORK + SC_DOMO

# logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)


class SecuritasAPIClient():
    _BASE_URL = 'https://mob2217.securitasdirect.es:12010/WebService/ws.do'
    _TIMEOUT = 6
    _RETRY = 4
    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'

    def __init__(self, user, pwd, country="ES", lang=None):
        if lang is None:
            lang = country.lower() if country != 'GB' else 'en'
        self._params = {'Country': country, 'user': user, 'lang': lang,
                        'request': "", 'ID': "", 'callby': 'AND_61'}
        self.pwd = pwd
        self.alias = ""

        retry = requests.packages.urllib3.util.retry.Retry(connect=3,
                                                           backoff_factor=0.75)
        adapter = requests.adapters.HTTPAdapter(max_retries=retry)
        self.session = requests.Session()
        self.session.mount('https://', adapter)

    def _set_id(self):
        self._params['ID'] = ('AND_______________' + self._params['user'] +
                              '_________' + datetime.datetime.now().strftime(
                                  "%Y%m%d%H%M%S") + '123')
        # self._params['ID'] = ('IPH_________________________'
        #        + self._params['user']
        #        + datetime.datetime.now().strftime("%Y%m%d%H%M%S") )

    def _api_request(self, request, **more):
        self._params['request'] = request
        if 'ID' not in more:
            self._set_id()
        try:
            resp = self.session.get(self._BASE_URL,
                                    params={**self._params, **more},
                                    timeout=self._TIMEOUT)
            if resp.status_code == 200:
                res = xmltodict.parse(resp.text)
                return res
        except requests.exceptions.RequestException as e:
            _LOGGER.error(e)

    def api_request(self, request, **more):
        if 'hash' not in self._params:
            if self.login():
                self.get_ins()
            else:
                return
        res = self._api_request(request, **more)
        if self._validate(res, 'PET', 'ERR') == "ERROR" \
                and res['PET']['ERR'] in ("60067", "60022"):
            # self.logout()
            self.login()
            res = self._api_request(request, **more)
        return res

    def _validate(self, res, *keys):
        if len(keys):
            _res = res
            for k in keys:
                try:
                    _res = _res[k]
                except (KeyError, TypeError):
                    return False
        try:
            return res['PET']['RES']
        except (KeyError, TypeError):
            pass
        return False

    def _is_ok(self, res):
        return self._validate(res) == "OK"

    def _error(self, res):
        if self._validate(res, 'PET', 'MSG') != 'OK':
            _LOGGER.error(res['PET']['MSG'])

    def api_call(self, action, **more):
        if action in SC_ALARM:
            res = self.api_request(action+'1', **more)
            res = self.api_request(action+'2', ID=self._params['ID'], **more)
            for i in range(self._RETRY):
                if res is None or self._validate(res) == "WAIT":
                    time.sleep(i+1)
                    res = self.api_request(action+'2',
                                           ID=self._params['ID'], **more)
                    _LOGGER.debug("RETRY(%s):%s", i, res)
        else:
            res = self.api_request(action, **more)
        return res

    def get_ins(self):
        for i in range(self._RETRY):
            res = self.api_request('INS')
            if self._validate(res, 'PET', 'INSTALATIONS', 'INSTALATION'
                              ) == "OK":
                _LOGGER.debug(res)
                inst = res['PET']['INSTALATIONS']['INSTALATION']
                self._params.update({'numinst': inst['NUMINST'],
                                     'panel': inst['PANEL']})
                self.alias = inst['ALIAS']
                res = self.api_request('SRV')
                _LOGGER.debug(res)
                return res
            time.sleep(i+1)

    def camera_snapshot(self, device):
        return self.api_call('IMG', **{'device': device, 'idservice': 1})

    def login(self):
        self._set_id()
        self._params.update({'request': "LOGIN", 'pwd': self.pwd})
        if 'hash' in self._params:
            del self._params['hash']
        try:
            resp = self.session.post(self._BASE_URL, params=self._params,
                                     timeout=self._TIMEOUT)
            del self._params['pwd']
            if resp.status_code != 200:
                _LOGGER.error("Cant loging. Server code: %s", resp.status_code)
                return False
            res = xmltodict.parse(resp.text)
            _LOGGER.debug(res)
            if self._validate(res) == "OK":
                if self._validate(res, 'PET', 'HASH'):
                    self._params.update({'hash': res['PET']['HASH']})
                    return True
            else:
                self._error(res)
        except requests.exceptions.RequestException as e:
            _LOGGER.error(e)
        return False

    def logout(self):
        res = self._api_request('CLS', numinst="(null)")
        _LOGGER.error("LOGOUT: %s", res)
        if 'hash' in self._params:
            del self._params['hash']
        return res

    def last_state(self, filter='states'):
        if filter == 'states':
            filter = ('1', '2', '31', '32', '46', '202', '311', '13', '24')
        res = self.api_request('ACT_V2', timefilter=2, activityfilter=0)
        _LOGGER.debug(res)
        try:
            if self._validate(res, 'PET', 'LIST', 'REG') == "OK":
                regs = res['PET']['LIST']['REG']
                # print(json.dumps(regs[0]))
                for reg in regs:
                    if filter is None or reg['@type'] in filter:
                        return reg
        except (KeyError, TypeError):
            return


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 3:
        sys.exit(sys.argv[0] + ' Country User Pass [ACTION] [option=value]...')
    client = SecuritasAPIClient(args[1], args[2], args[0])
    if len(args) == 3:
        out = client.last_state()
    elif args[3] in SC_ALL or (len(args[3]) > 2 and args[3][:-1] in SC_ALL):
        opts = {'timefilter': 5,
                'activityfilter': 0} if args[3] == 'ACT_V2' else {}
        opts.update(dict([i.split("=", 1) for i in args[4:]]))
        out = client.api_call(args[3], **opts)
    elif args[3] == 'SHOT':
        out = client.camera_snapshot(3)
    else:
        sys.exit('ACTION must be some of:\n' + str(SC_ALL))
    try:
        pet = out['PET']
        imgs = out['PET']['DEVICES']['DEVICE']['IMG']
        for img in imgs:
            with open("img" + img['@id'] + ".jpeg", "wb") as f:
                f.write(base64.b64decode(img['#text']))
        print(json.dumps(out, indent=2))
    except (KeyError, TypeError):
        try:
            del out["PET"]["BLOQ"]
        except (KeyError, TypeError):
            pass
        print(json.dumps(out, indent=2))

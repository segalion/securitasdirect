"""Support for Securitas Direct (AKA Verisure EU) alarm control panels."""

import logging, datetime
from time import sleep

import homeassistant.components.alarm_control_panel as alarm
from homeassistant.const import (
    CONF_CODE,
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_DISARMED,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_ARMED_CUSTOM_BYPASS,
    STATE_ALARM_PENDING,
    STATE_ALARM_TRIGGERED,
    STATE_ALARM_ARMING,
    STATE_ALARM_DISARMING,
#    STATE_UNAVAILABLE,
#    STATE_UNKNOWN,
    STATE_ALARM_PENDING,
)

from homeassistant.components.alarm_control_panel.const import (
    SUPPORT_ALARM_ARM_AWAY,
    SUPPORT_ALARM_ARM_HOME,
    SUPPORT_ALARM_ARM_NIGHT,
)

from . import CONF_ALARM, CONF_CODE_DIGITS, CONF_COUNTRY, HUB as hub
# from securitas import SecuritasAPIClient

_LOGGER = logging.getLogger(__name__)

# some reported by @furetto72@Italy
SECURITAS_STATUS = {
    STATE_ALARM_DISARMED: ['0', ("1", "32")],
    STATE_ALARM_ARMED_HOME: ['P', ("311", "202")],
    STATE_ALARM_ARMED_NIGHT: [('Q', 'C'), ("46",)],
    STATE_ALARM_ARMED_AWAY: [('1', 'A'), ("2", "31")],
    STATE_ALARM_ARMED_CUSTOM_BYPASS: ['3', ('204',)],
    STATE_ALARM_TRIGGERED: ['???', ('13', '24')],
}


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Securitas platform."""
    alarms = []
    if int(hub.config.get(CONF_ALARM, 1)):
        hub.update_overview()
        alarms.append(SecuritasAlarm())
    add_entities(alarms)


def set_arm_state(state, code=None):
    """Send set arm state command."""
    # hub.session.api_call(state)
    _LOGGER.error("Securitas: esternal set arm state %s", state)
    # sleep(2)
    # hub.update_overview(no_throttle=True)


class SecuritasAlarm(alarm.AlarmControlPanelEntity):
    """Representation of a Securitas alarm status."""

    def __init__(self):
        """Initialize the Securitas alarm panel."""
        self._state = None
        self._digits = hub.config.get(CONF_CODE_DIGITS)
        self._changed_by = None
        self._device = ""
        self._time = None
        self._message = ""

    def __force_state(self, state):
        self._state = state
        self.hass.states.set(self.entity_id, state)

    def __arm_state(self, state):
        res = hub.session.api_call(state)
        _LOGGER.debug("Securitas: setting arm state: %s\nres=%s", state, res)
        return res

    def get_arm_state(self):
        res = self.__arm_state('EST')
        if hub.session._is_ok(res):
            for k, v in SECURITAS_STATUS.items():
                if res['PET']['STATUS'] in v[0]:
                    return k

    def set_arm_state(self, state, attempts=3):
        """Send set arm state command."""
        for i in range(attempts):
            res = self.__arm_state(state)
            if hub.session._is_ok(res):
                break
            else:
                _LOGGER.warning("Securitas: disarming (res=%s)", res)
                self.__arm_state('DARM')
                sleep(i*2+1)
        sleep(2)
        hub.update_overview(no_throttle=True)

    @property
    def name(self):
        """Return the name of the device."""
        return "securitas_{}".format(hub.session._params['numinst'])

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def code_format(self):
        """Return one or more digits/characters."""
        return alarm.FORMAT_NUMBER

    @property
    def code_arm_required(self):
        """Whether the code is required for arm actions."""
        return False

    @property
    def changed_by(self):
        """Return the last change triggered by."""
        return self._changed_by

    def update(self):
        """Update alarm status, from last alarm setting register or EST"""
        hub.update_overview()
        status = hub.overview
        try:
            for k, v in SECURITAS_STATUS.items():
                if status['@type'] in v[1]:
                    self._state = k
                    self._changed_by = (status['@user'] if '@user' in status
                                        else status['@myverisureUser']
                                        if '@myverisureUser' in status
                                        else "") + "@" + status['@source']
                    self._device = status['@device']
                    self._time = datetime.datetime.strptime(status['@time'],
                                                            '%y%m%d%H%M%S')
                    self._message = status['@alias']
                    break
        except (KeyError, TypeError):
            if self._state is None:
                self._state = self.get_arm_state()
                if self._state is None:
                    self._state = STATE_ALARM_PENDING

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {'device': self._device,
                'time': self._time,
                'message': self._message,
                'alias': hub.session.alias
                }

    def alarm_disarm(self, code=None):
        """Send disarm command."""
        if (hub.config.get(CONF_CODE, "") == "" or
                hub.config.get(CONF_CODE, "") == code):
            self.__force_state(STATE_ALARM_DISARMING)
            self.set_arm_state("DARM")

    def alarm_arm_home(self, code=None):
        """Send arm home command."""
        self.__force_state(STATE_ALARM_ARMING)
        self.set_arm_state("ARMDAY")

    def alarm_arm_away(self, code=None):
        """Send arm away command."""
        self.__force_state(STATE_ALARM_ARMING)
        self.set_arm_state("ARM")

    def alarm_arm_night(self, code=None):
        """Send arm home command."""
        self.__force_state(STATE_ALARM_ARMING)
        self.set_arm_state("ARMNIGHT")

    def alarm_arm_custom_bypass(self, code=None):
        """Send arm perimeter command."""
        self.__force_state(STATE_ALARM_ARMING)
        self.set_arm_state("PERI")

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return (SUPPORT_ALARM_ARM_HOME
                | SUPPORT_ALARM_ARM_AWAY
                | SUPPORT_ALARM_ARM_NIGHT)

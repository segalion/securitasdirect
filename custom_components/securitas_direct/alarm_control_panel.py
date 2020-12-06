"""Support for Securitas Direct (AKA Verisure EU) alarm control panels."""

import datetime
import logging

import homeassistant.components.alarm_control_panel as alarm
from homeassistant.components.alarm_control_panel.const import (
    SUPPORT_ALARM_ARM_AWAY,
    SUPPORT_ALARM_ARM_HOME,
    SUPPORT_ALARM_ARM_NIGHT,
)
from homeassistant.const import (
    CONF_CODE,
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_DISARMED,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_ARMED_CUSTOM_BYPASS,
    STATE_ALARM_TRIGGERED,
    STATE_ALARM_ARMING,
    STATE_ALARM_DISARMING,
    #    STATE_UNAVAILABLE,
    #    STATE_UNKNOWN,
    STATE_ALARM_PENDING,
)

from . import CONF_ALARM, CONF_CODE_DIGITS, HUB as hub


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

    def get_arm_state(self):
        res = hub.alarm.get_status()
        for k, v in SECURITAS_STATUS.items():
            if res["STATUS"] in v[0]:
                return k

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
                }

    def alarm_disarm(self, code=None):
        """Send disarm command."""
        if (hub.config.get(CONF_CODE, "") == "" or
                hub.config.get(CONF_CODE, "") == code):
            self.__force_state(STATE_ALARM_DISARMING)
            hub.alarm.disconnect()
            hub.update_overview(no_throttle=True)

    def alarm_arm_home(self, code=None):
        """Send arm home command."""
        self.__force_state(STATE_ALARM_ARMING)
        hub.alarm.activate_day_mode()
        hub.update_overview(no_throttle=True)

    def alarm_arm_away(self, code=None):
        """Send arm away command."""
        self.__force_state(STATE_ALARM_ARMING)
        hub.alarm.activate_total_mode()
        hub.update_overview(no_throttle=True)

    def alarm_arm_night(self, code=None):
        """Send arm home command."""
        self.__force_state(STATE_ALARM_ARMING)
        hub.alarm.activate_night_mode()
        hub.update_overview(no_throttle=True)

    def alarm_arm_custom_bypass(self, code=None):
        """Send arm perimeter command."""
        self.__force_state(STATE_ALARM_ARMING)
        hub.alarm.activate_perimeter_mode()
        hub.update_overview(no_throttle=True)

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return (SUPPORT_ALARM_ARM_HOME
                | SUPPORT_ALARM_ARM_AWAY
                | SUPPORT_ALARM_ARM_NIGHT)

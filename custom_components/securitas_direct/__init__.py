"""Support for Securitas Direct alarms."""
import logging
from datetime import timedelta

import voluptuous as vol

from homeassistant.const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    CONF_CODE,
    EVENT_HOMEASSISTANT_STOP,
)
from homeassistant.helpers import discovery
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv
from pysecuritas.core.session import Session
from pysecuritas.api.installation import Installation
from pysecuritas.api.alarm import Alarm

_LOGGER = logging.getLogger(__name__)

CONF_ALARM = "alarm"
CONF_CODE_DIGITS = "code_digits"
CONF_COUNTRY = "country"
CONF_LANG = "lang"
CONF_INSTALLATION = "installation"

DOMAIN = "securitas_direct"

MIN_SCAN_INTERVAL = timedelta(seconds=20)
DEFAULT_SCAN_INTERVAL = timedelta(seconds=40)

HUB = None

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_INSTALLATION): cv.positive_int,
                vol.Optional(CONF_COUNTRY, default="ES"): cv.string,
                vol.Optional(CONF_LANG, default="es"): cv.string,
                vol.Optional(CONF_ALARM, default=True): cv.boolean,
                vol.Optional(CONF_CODE_DIGITS, default=4): cv.positive_int,
                vol.Optional(CONF_CODE, default=""): cv.string,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): (
                    vol.All(cv.time_period, vol.Clamp(min=MIN_SCAN_INTERVAL))
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass, config):
    """Set up the Securitas component."""
    global HUB
    HUB = SecuritasHub(config[DOMAIN])
    HUB.update_overview = Throttle(config[DOMAIN][CONF_SCAN_INTERVAL])(
        HUB.update_overview
    )
    if not HUB.login():
        return False
    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, lambda event: HUB.logout())
    HUB.update_overview()
    for component in (
        "alarm_control_panel",
    ):
        discovery.load_platform(hass, component, DOMAIN, {}, config)
    return True


class SecuritasHub:
    """A Securitas hub wrapper class."""

    def __init__(self, domain_config):
        """Initialize the Securitas hub."""
        self.overview = {}
        self.config = domain_config
        self.session = Session(domain_config[CONF_USERNAME], domain_config[CONF_PASSWORD],
                               domain_config[CONF_INSTALLATION],
                               domain_config[CONF_COUNTRY].upper(), domain_config[CONF_LANG].lower())
        self.installation = Installation(self.session)
        self.alarm = Alarm(self.session)

    def login(self):
        """Login to Securitas."""
        self.session.connect()

        return self.session.is_connected()

    def logout(self):
        """Logout from Securitas."""
        self.session.close()

        return True

    def update_overview(self):
        """Update the overview."""

        filter = ('1', '2', '31', '32', '46', '202', '311', '13', '24')
        res = self.installation.get_activity_log()
        _LOGGER.debug(res)
        try:
            regs = res['LIST']['REG']
            for reg in regs:
                if filter is None or reg['@type'] in filter:
                    self.overview = reg

                    return
        except (KeyError, TypeError):
            pass

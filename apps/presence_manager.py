"""Presence Manager"""

import appdaemon.plugins.hass.hassapi as hass


class PresenceManager(hass.Hass):
    """Turns on and off lights/appliances based on presence"""

    def initialize(self):
        """Initialise the app"""
        self.devices = self.args["devices"]
        self.filter_time = self.args["filter_time"]
        self.off_entities = self.args["off_entities"]
        self.on_entities = self.args["on_entities"]

        self.timer = None
        self.preserved_entities = []

        for device in self.devices:
            self.listen_state(self.away_callback, device, new="not_home")
            self.listen_state(self.home_callback, device, new="home")

    def turn_on_entities():
        """Turn on entities that should be on"""
        for entity, state in self.preserved_entities:
            if state == "on":
                self.turn_on(entity)

        for entity, only_after_sunset in self.on_entities:
            if only_after_sunset:
                if self.now_is_between("sunset", "sunrise"):
                    self.turn_on(entity)
            else:
                self.turn_on(entity)

    def turn_off_entities():
        """Turn off entities, optionally preseving state"""
        for entity, preserve in self.off_entities:
            if preserve:
                self.preserved_entities.append((entity, self.get_state(entity)))
            self.turn_off(entity)

    def check_home_state(self):
        """Returns 'home' if any device is home and 'not_home' otherwise"""
        for device in self.devices:
            if self.get_state(device) == "home":
                return "home"
        return "not_home"

    def away_callback(self, entity, attribute, old, new, kwargs):
        """Called when a device goes away"""
        if self.check_home_state() == "not_home":
            self.timer = self.run_in(self.timeout_callback, self.filter_time)

    def home_callback(self, entity, attribute, old, new, kwargs):
        """Called when a device returns home"""
        if self.timer is not None:
            self.cancel_timer(self.timer)
            self.timer = None
        self.turn_on_entities()

    def timeout_callback(self, kwargs):
        self.turn_off_entities()

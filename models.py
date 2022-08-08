from pcse.engine import Engine


def my_integrate(self, day, delt):
    # Flush state variables from the kiosk before state updates
        # self.kiosk.flush_states()

        if self.crop is not None:
            self.crop.integrate(day, delt)

        if self.soil is not None:
            self.soil.integrate(day, delt)

        # Set all rate variables to zero
        # if settings.ZEROFY:
        #     self.zerofy()

        # Flush rate variables from the kiosk after state updates
        # self.kiosk.flush_rates()

Engine.integrate = my_integrate


class sample(Engine):
    config = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/sample.conf"

    def __init__(self, parameterprovider, weatherdataprovider, agromanagement):
        Engine.__init__(self, parameterprovider, weatherdataprovider, agromanagement,
                        config=self.config)


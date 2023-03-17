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

def my_on_CROP_START(self, day, crop_name=None, variety_name=None,
                    crop_start_type=None, crop_end_type=None):
    """Starts the crop
    """
    self.logger.debug("Received signal 'CROP_START' on day %s" % day)

    if self.crop is not None:
        msg = ("A CROP_START signal was received while self.cropsimulation "
                "still holds a valid cropsimulation object. It looks like "
                "you forgot to send a CROP_FINISH signal with option "
                "crop_delete=True")
        raise exc.PCSEError(msg)

    # self.parameterprovider.set_active_crop(crop_name, variety_name, crop_start_type,
    #                                         crop_end_type)
    self.crop = self.mconf.CROP(day, self.kiosk, self.parameterprovider)
    
Engine._on_CROP_START = my_on_CROP_START



class sample(Engine):
    config = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/sample.conf"

    def __init__(self, parameterprovider, weatherdataprovider, agromanagement):
        Engine.__init__(self, parameterprovider, weatherdataprovider, agromanagement,
                        config=self.config)


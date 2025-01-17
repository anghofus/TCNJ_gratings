class SinePhasePlateGeneration:
    def __init__(self,
                 radius: float,
                 focal_length: float,
                 wavelength: float,
                 grating_width: int):

        self.__radius = radius / 1000
        self.__focal_length = focal_length / 1000
        self.__wavelength = wavelength / 10 ** 9
        self.__grating_width = grating_width / 10 ** 6

        self.__slm_px_width = 1920
        self.__slm_px_height = 1200

        self.__slm_count = int(self.__radius / self.__grating_width)
        self.__waveform_length = int(self.__slm_count * 1920)
        self.__pixel_width = self.__radius / self.__waveform_length

        print(self.__slm_count)
        print(self.__waveform_length)
        print(self.__pixel_width)

foo = SinePhasePlateGeneration(2.5, 1, 635, 70)
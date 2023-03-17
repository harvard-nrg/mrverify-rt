import os
import re
import logging

logger = logging.getLogger(__name__)

class Siemens:
    def __init__(self, ds):
        self._ds = ds

    def _csa(self):
        dat = dict()
        tag = (0x0029,0x1020)
        if tag not in self._ds:
          raise MissingTagError(tag)
        value = self._ds[tag].value
        value = value.decode(errors='ignore')
        match = re.search('### ASCCONV BEGIN.*?###(.*)### ASCCONV END ###', value, re.DOTALL)
        if not match:
          raise Exception('could not find ASCCONV section in Siemens CSA header')
        ascconv = match.group(1).strip()
        for line in ascconv.split('\n'):
            match = re.match('(.*?)\s+=\s+(.*)', line)
            key,value = match.groups()
            dat[key] = value.strip('"')
        return dat

    def image_orientation_patient(self):
        return self._ds.ImageOrientationPatient

    def pixel_spacing(self):
        return [round(float(x), 3) for x in self._ds.PixelSpacing]

    def shim_current(self):
        raise MissingTagError((0x0000, 0x0000))
        
    def orientation_string(self):
        tag = (0x0051,0x100e)
        if tag not in self._ds:
            raise MissingTagError(tag)
        return self._ds[tag].value

    def bandwidth(self):
        return float(self._ds.PixelBandwidth)

    def prescan_norm(self):
        if 'NORM' in self._ds.ImageType:
            return True
        return False

    def base_resolution(self):
        tag = (0x0018,0x1310)
        if tag not in self._ds:
            raise MissingTagError(tag)
        return self._ds[tag].value

    def pe_direction(self):
        tag = (0x0018,0x1312) 
        if tag not in self._ds:
            raise MissingTagError(tag)
        return self._ds[tag].value

    def flip_angle(self):
        return float(self._ds.FlipAngle)

    def image_type(self):
        val = self._ds.ImageType
        return val

    def series_description(self):
        return self._ds.SeriesDescription

    def series_number(self):
        return self._ds.SeriesNumber

    def coil_elements(self):
        tag = (0x0051,0x100f)
        if tag not in self._ds:
            dat = self._csa()
            return dat['sCoilSelectMeas.sCoilStringForConversion']
        return self._ds[tag].value
        
    def repetition_time(self):
        return float(self._ds.RepetitionTime)

    def echo_time(self):
        return float(self._ds.EchoTime)

    def slice_thickness(self):
        return float(round(self._ds.SliceThickness, 3))

    def percent_phase_field_of_view(self):
        return float(self._ds.PercentPhaseFieldOfView)

    def patient_position(self):
        return self._ds.PatientPosition

    def num_slices(self):
        if 'MOSAIC' in self._ds.ImageType:
          tag = (0x0019, 0x100a)
          if tag not in self._ds:
            dat = self._csa()
            return float(dat['sSliceArray.lSize'])
          return float(self._ds[tag].value)
        return getattr(self._ds, 'num_files', None)

    def num_volumes(self):
        return getattr(self._ds, 'num_files', None)

    def num_files(self):
        return getattr(self._ds, 'num_files', None)

    def fov_read(self):
        tag = (0x0051,0x100c)
        if tag not in self._ds:
            raise MissingTagError(tag)
        value = self._ds[tag].value
        match = re.match('^FoV \d+\*(\d+)$', value)
        return int(match.group(1))

class MissingTagError(Exception):
    pass


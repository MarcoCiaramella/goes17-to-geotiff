import sys
from osgeo import gdal
from osgeo.gdalconst import *
from osgeo import osr
import netCDFreader as ncr
import datetime
import numpy as np



class Goes17Reader:
    
    def __init__(self, nc): 
        self.dataset = ncr.open(nc,'NETCDF4')
        self._read_rad()
        self._read_projection()
        self._extension()
        self._read_datetime()
        self._read_band_info()
        
    def _extension(self):
        self.ext = [-5434894.885056, -5434894.885056, 5434894.885056, 5434894.885056]
        
    def _read_rad(self):
        """Example
        <type 'netCDF4.Variable'>
        int16 Rad(y, x)
            _FillValue: 1023
            long_name: ABI L1b Radiances
            standard_name: toa_outgoing_radiance_per_unit_wavelength
            _Unsigned: true
            sensor_band_bit_depth: 10
            valid_range: [   0 1022]
            scale_factor: 0.812106
            add_offset: -25.9366
            units: W m-2 sr-1 um-1
            coordinates: band_id band_wavelength t y x
            grid_mapping: goes_imager_projection
            ancillary_variables: DQF
            resolution: y: 0.000056 rad x: 0.000056 rad
            cell_methods: t: point area: point
        unlimited dimensions:
        current shape = (5424, 5424)
        filling on"""
        rad = ncr.readVar(self.dataset,'Rad')
        self.rad = rad[:]
        self.rad = np.flip(self.rad, 1)
        self.rad = np.rot90(self.rad, 2)
        self.dy = self.rad.shape[0]
        self.dx = self.rad.shape[1]
        self.nodata = rad._FillValue
        self.rad_units = str(rad.units)

    def _read_projection(self):
        """Example:
        <type 'netCDF4.Variable'>
        int32 goes_imager_projection()
            long_name: GOES-R ABI fixed grid projection
            grid_mapping_name: geostationary
            perspective_point_height: 35786023.0
            semi_major_axis: 6378137.0
            semi_minor_axis: 6356752.31414
            inverse_flattening: 298.2572221
            latitude_of_projection_origin: 0.0
            longitude_of_projection_origin: -137.0
            sweep_angle_axis: x
        unlimited dimensions:
        current shape = ()
        filling on, default _FillValue of -2147483647 used"""
        proj = ncr.readVar(self.dataset,'goes_imager_projection')
        lon_0 = proj.longitude_of_projection_origin
        h = proj.perspective_point_height
        majior_ax = proj.semi_major_axis
        minor_ax = proj.semi_minor_axis
        self.proj4 = "+proj=geos +lon_0=%s +h=%s +x_0=0 +y_0=0 +a=%s +b=%s +units=m"%(lon_0,h,majior_ax,minor_ax)
        
    def _read_datetime(self):
        """ Example
        <type 'netCDF4.Variable'>
        float64 t()
            long_name: J2000 epoch mid-point between the start and end image scan in seconds
            standard_name: time
            units: seconds since 2000-01-01 12:00:00
            axis: T
            bounds: time_bounds
        unlimited dimensions:
        current shape = ()
        filling on, default _FillValue of 9.96920996839e+36 used""" 
        t = ncr.readVar(self.dataset,'t')
        tsplit = t.units.split(' ')
        date = tsplit[2]
        time = tsplit[3]
        seconds = int(t[:])
        self.datetime = str(datetime.datetime.strptime(str(date+'T'+time),'%Y-%m-%dT%H:%M:%S') + datetime.timedelta(seconds=seconds))
        
    def _read_band_info(self):
        self.band_id = str(ncr.readVar(self.dataset,'band_id')[:][0])
        bandVar = ncr.readVar(self.dataset,'band_wavelength')
        self.band_wavelength = str(bandVar[:][0])+str(bandVar.units)
    
    def export_geotiff(self,output_file):
        #tiff file section
        format = "GTiff"
        #get driver
        driver = gdal.GetDriverByName( format )
        dst_ds = driver.Create( output_file, self.dx, self.dy, 1, gdal.GDT_Float32 )
        adfGeoTransform = [
                           self.ext[0],
                           (self.ext[2] - self.ext[0]) / float(self.dx),
                           0.0,
                           self.ext[1],
                           0.0,
                           (self.ext[3] - self.ext[1]) / float(self.dy)
                           ]
        dst_ds.SetGeoTransform( adfGeoTransform )
        dst_ds.SetMetadataItem('TIFFTAG_DATETIME',self.datetime,'')
        dst_ds.SetMetadataItem('RAD_UNITS',self.rad_units,'')
        dst_ds.SetMetadataItem('BAND_ID',self.band_id,'')
        dst_ds.SetMetadataItem('BAND_WAVELENGTH',self.band_wavelength,'')
        
        srs = osr.SpatialReference()
        srs.ImportFromProj4(self.proj4)
        dst_ds.SetProjection( srs.ExportToWkt() )
        
        dst_ds.GetRasterBand(1).SetNoDataValue(float(self.nodata))
            
        #write data
        dst_ds.GetRasterBand(1).WriteArray( self.rad )
    
        # Once we're done, close properly the dataset
        dst_ds = None
        
        

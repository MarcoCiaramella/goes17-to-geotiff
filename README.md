# goes17-to-geotiff
Python module to convert goes17 data in netCDF format to geotiff raster format.

Code example:

```
from goes17 import Goes17Reader

netcdf_file = 'OR_ABI-L1b-RadF-M6C02_G17_s20191001200341_e20191001209407_c20191001209440-129602_0.nc'
geotiff_file = 'OR_ABI-L1b-RadF-M6C02_G17_s20191001200341_e20191001209407_c20191001209440-129602_0.tif'
goes17 = Goes17Reader(netcdf_file)
goes17.export_geotiff(geotiff_file)
```

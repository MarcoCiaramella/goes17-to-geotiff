import sys
from goes17 import Goes17Reader

# if run as script
if __name__ == "__main__":
    
    if len(sys.argv) != 3:
        print 'Use: python goes17_to_geotiff.py [input file] [output file]'
        exit()
        
    netcdf_file = sys.argv[1]
    geotiff_file = sys.argv[2]
    
    goes17 = Goes17Reader(netcdf_file)
    goes17.export_geotiff(geotiff_file)

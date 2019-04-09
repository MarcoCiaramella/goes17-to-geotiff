import netCDF4
from netCDF4 import Dataset



def open(netcdf_file,format):
    dataset = Dataset(netcdf_file, 'r', format=format)
    return dataset

def readVar(dataset,varName):
    return dataset.variables[varName]

def readValue(dataset,varName):
    return readVar(dataset,varName)[:]
    
def printVariable(dataset,varName):
    print dataset.variables[varName]
    
def printVariables(dataset):
    for var in dataset.variables:
        print dataset.variables[var]

def printVariablesName(dataset):
    for var in dataset.variables:
        print var

def printAllValues(dataset):
    for var in dataset.variables:
        print var,dataset.variables[var][:]

           
# if run as script
if __name__ == "__main__":
    
    import sys
    
    if len(sys.argv) != 3:
        print 'Use: python netCDFreader.py [netcdf file] [netcdf format]'
        exit()
        
    netcdf_file = sys.argv[1]
    format = sys.argv[2]
    # format example: NETCDF4
    dataset = open(netcdf_file,format)
    #printAllValues(dataset)
    printVariables(dataset)
    
    
    
    

# Copyright 2020, General Electric Company. All rights reserved. See https://github.com/xcist/code/blob/master/LICENSE

from ctypes import *
from catsim.pyfiles.ReadMaterialFile import ReadMaterialFile
from catsim.pyfiles.CommonTools import *

def GetMu(materialFile, Evec):

    #----------------- load dll lib and material data path
    clib = load_C_lib()

    #----------------- initialize cross-section data
    # the format of this path is finicky and using os.path.join, os.pathsep or changing all \\ to /
    # does not seem to work on the C code side
    MaterialDirectory = my_path.paths["material"] + "/"

    c_MaterialDirectory = c_char_p(bytes(MaterialDirectory, 'utf-8'))
    # b_MaterialDirectory = b"./data/materials/" # bytes, python3

    clib.InitializeCrossSectionDB.argtypes = [POINTER(c_char), c_int] # here c_char_p = POINTER(c_char)
    clib.InitializeCrossSectionDB.restype = None

    # clib.InitializeCrossSectionDB(MaterialDirectory, 0) # not working
    clib.InitializeCrossSectionDB(c_MaterialDirectory, 0) # works
    # clib.InitializeCrossSectionDB(b_MaterialDirectory, 0) # works

    #----------------- read material file
    materialFile = my_path.find("material", materialFile, '')
    (numberOfElements, density, atomicNumbers, massFractions) = ReadMaterialFile(materialFile)
    atomicNumbers = (c_int*numberOfElements)(*atomicNumbers)
    massFractions = (c_float*numberOfElements)(*massFractions)

    #----------------- X-ray energy vector
    isNumpy = isinstance(Evec, np.ndarray)
    if isNumpy:
        origShape = Evec.shape
        Evec = list(Evec.ravel())
    elif isinstance(Evec, (int, float)):
        Evec = [Evec]
    numberOfEnergies = len(Evec)
    energies = (c_float*numberOfEnergies)(*Evec)
        
    #----------------- GetMAC
    MAC = (c_float*numberOfEnergies)()
    clib.GetCrossSectionMAC.argtypes = [c_int, POINTER(c_int), POINTER(c_float), c_int, POINTER(c_float), POINTER(c_float)]
    clib.GetCrossSectionMAC.restype = None
    clib.GetCrossSectionMAC(numberOfElements, atomicNumbers, massFractions, numberOfEnergies, energies, MAC)
    
    mu = []
    for ii in range(0, numberOfEnergies):
        mu.append(MAC[ii]*density)

    if isNumpy:
        mu = np.array(mu,dtype=np.single)
        mu = mu.reshape(origShape)
    return mu

if __name__ == '__main__':
    Evec = range(10, 70, 10)
    # Evec = np.array([(20, 30, 40), (50, 60, 70)], dtype=np.single)
    mu = GetMu('water', Evec)
    print(mu, type(mu))
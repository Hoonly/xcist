# Copyright 2020, General Electric Company. All rights reserved. See https://github.com/xcist/code/blob/master/LICENSE

# Author: Paul FitzGerald
# Date: April 18, 2022
#
# Purpose: This is an XCIST "experiment file" that is used to evaluate several aspects of XCIST simulation and recon
# using the CatSim log phantom. The default config files are used for everything except the phantom and recon - for
# these, you will need Phantom_CatSimLogo.cfg and Recon_CatSimLogo.cfg, which should be included in the same folder
# where you found this file.
#
# The CatSim logo phantom used in this experiment is a voxelized phantom. Therefore, the simulation portion of this
# evaluation only evaluates the voxelized projector. However, the recon aspects of this experiment are independent of
# the phantom/projector type.
#
# This "experiment file" performs several experiments, and each experiment requires several simulations and
# reconstructions. Results are written to the folder defined by the system environment variable XCIST_UserPath.
# Sub-folders are for each sim/recon. DON'T make this path point to a location within your local copy of the CatSim
# repository, or the output files (which are numerous and large) might end up in the repository!
#
# The experiments performed include:
# 01. Noise simulation evaluation (12 simulations/reconstructions)
# 02. Reconstruction kernal evaluation (1 simulation and 5 reconstructions from the resulting sinogram) 
# 03. Rotation speed simulation evaluation (3 simulations/reconstructions)
# 04. Number of views simulation evaluation (3 simulations/reconstructions)
# 05. Source, detector, and view sampling simulation evaluation (9 simulations/reconstructions)
# 06. X-ray scatter simulation evaluation (3 simulations/reconstructions)
# 07. Number of reconstructed slices evaluation (3 simulations/reconstructions)
# 08. Phantom offset simulation evaluation (5 simulations/reconstructions)
# 09. Reconstruction offset evaluation (1 simulation and 3 reconstructions)
#
# Each sim/recon is independent except experiments 02 and 09, which use the same sim for multiple recons.
# Each sim/recon is included in a list of sim/recons to run - see "##--------- Define experiment names".
# Each can be run or not by uncommenting or commenting them.
#
# The overall process is:
# a. Define "base" config (see "##--------- Initialize").
# b. Define a list of sim/recons to run (see "##--------- Define experiment names").
# c. Loop through all the sim/recons defined in b, and for each sim/recon:
# d.   Define the specific parameters for the sim/recon - function setExperimentParameters().
# e.   Get the title for the recon images - function getReconImageTitle().
#      This includes parameters relevant to the experiment.
# f.   Run the simulation - function runSim().
# g.   Run the recon - function runRecon().

import os
import copy
import shutil
import catsim as xc
import reconstruction.pyfiles.recon as recon

def setExperimentParameters(cfg):

    experimentName = cfg.experimentName

    # Some experiments use 1000 views and low mA.
    if experimentName == "01_01_Baseline"                        \
    or experimentName == "01_02_Physics_eNoiseOn"                \
    or experimentName == "01_03_Physics_qNoiseOn"                \
    or experimentName == "01_04_Physics_NoiseOn"                 \
    or experimentName == "01_05_Physics_1ebin"                   \
    or experimentName == "01_06_Physics_eNoiseOn_1ebin"          \
    or experimentName == "01_07_Physics_qNoiseOn_1ebin"          \
    or experimentName == "01_08_Physics_NoiseOn_1ebin"           \
    or experimentName == "01_09_Physics_Monoenergetic"           \
    or experimentName == "01_10_Physics_eNoiseOn_Monoenergetic"  \
    or experimentName == "01_11_Physics_qNoiseOn_Monoenergetic"  \
    or experimentName == "01_12_Physics_NoiseOn_Monoenergetic":
        cfg.protocol.mA = 100
    
    # Some experiments use a 128mm FOV.
    if experimentName == "02_01_Physics_NoiseOn_Recon_128mmFOV_R-LKernel"                    \
    or experimentName == "02_02_Physics_NoiseOn_Recon_128mmFOV_S-LKernel"                    \
    or experimentName == "02_03_Physics_NoiseOn_Recon_128mmFOV_SoftKernel"                   \
    or experimentName == "02_04_Physics_NoiseOn_Recon_128mmFOV_StandardKernel"               \
    or experimentName == "02_05_Physics_NoiseOn_Recon_128mmFOV_BoneKernel"                   \
    or experimentName == "05_01_Physics_SourceSampling1_Recon_128mmFOV"                      \
    or experimentName == "05_02_Physics_SourceSampling2_Recon_128mmFOV"                      \
    or experimentName == "05_03_Physics_SourceSampling3_Recon_128mmFOV"                      \
    or experimentName == "05_04_Physics_DetectorSampling1_Recon_128mmFOV"                    \
    or experimentName == "05_05_Physics_DetectorSampling2_Recon_128mmFOV"                    \
    or experimentName == "05_06_Physics_DetectorSampling3_Recon_128mmFOV":
        cfg.recon.fov = 128.0

    # Some experiments use only electronic noise.
    if experimentName == "01_02_Physics_eNoiseOn"                                             \
    or experimentName == "01_06_Physics_eNoiseOn_1ebin"                                       \
    or experimentName == "01_10_Physics_eNoiseOn_Monoenergetic":
        cfg.physics.enableElectronicNoise = 1

    # Some experiments use only quantum noise.
    if experimentName == "01_03_Physics_qNoiseOn"                                             \
    or experimentName == "01_07_Physics_qNoiseOn_1ebin"                                       \
    or experimentName == "01_11_Physics_qNoiseOn_Monoenergetic":
        cfg.physics.enableQuantumNoise = 1

    # Some experiments use electonic and quantum noise and produce unique projection data.
    if experimentName == "01_04_Physics_NoiseOn"                                             \
    or experimentName == "01_08_Physics_NoiseOn_1ebin"                                       \
    or experimentName == "01_12_Physics_NoiseOn_Monoenergetic"                               \
    or experimentName == "03_01_Physics_NoiseOn_Protocol_0p5rotation"                        \
    or experimentName == "03_02_Physics_NoiseOn_Protocol_1p0rotation"                        \
    or experimentName == "03_03_Physics_NoiseOn_Protocol_2p0rotation"                        \
    or experimentName == "04_01_Physics_NoiseOn_Protocol_100views"                           \
    or experimentName == "04_02_Physics_NoiseOn_Protocol_360views"                           \
    or experimentName == "04_03_Physics_NoiseOn_Protocol_1000views":
        cfg.physics.enableQuantumNoise = 1
        cfg.physics.enableElectronicNoise = 1

    # Some experiments use electonic and quantum noise and the projection data should be common to several recons.
    if experimentName == "02_01_Physics_NoiseOn_Recon_128mmFOV_R-LKernel"                    \
    or experimentName == "02_02_Physics_NoiseOn_Recon_128mmFOV_S-LKernel"                    \
    or experimentName == "02_03_Physics_NoiseOn_Recon_128mmFOV_SoftKernel"                   \
    or experimentName == "02_04_Physics_NoiseOn_Recon_128mmFOV_StandardKernel"               \
    or experimentName == "02_05_Physics_NoiseOn_Recon_128mmFOV_BoneKernel":
        cfg.physics.enableQuantumNoise = 1
        cfg.physics.enableElectronicNoise = 1

        # Only do the sim for the first one. Otherwise, copy the relevant projection data.
        if experimentName == "02_02_Physics_NoiseOn_Recon_128mmFOV_S-LKernel"                    \
        or experimentName == "02_03_Physics_NoiseOn_Recon_128mmFOV_SoftKernel"                   \
        or experimentName == "02_04_Physics_NoiseOn_Recon_128mmFOV_StandardKernel"               \
        or experimentName == "02_05_Physics_NoiseOn_Recon_128mmFOV_BoneKernel":
            copyFromExperimentName = "02_01_Physics_NoiseOn_Recon_128mmFOV_R-LKernel"
            cfg.do_Sim = False
    
        if not experimentName == "02_01_Physics_NoiseOn_Recon_128mmFOV_R-LKernel":
            copyFromPathname = os.path.join(experimentDirectory, copyFromExperimentName,  copyFromExperimentName + ".prep")
            copyToPathname = cfg.resultsName + ".prep"
            shutil.copy2(copyFromPathname, copyToPathname)

    # Most experiments use the baseline polyenergetic spectrum and number of energy bins,
    # but a few use different spectra.
    # We need to adjust the recon mu values for each spectrum to make water = 0 HU.
    # The adjusted mu values were determined experimentally by first reconstructing with cgf.recon.mu = 0.02,
    # measuring water HU in a cental ROI (40 pixels wide, 80 pixels high),
    # and calculating the mu required to make water = 0 HU using this formula:
    # cfg.recon.mu = 0.02 + HU(water, measured)*0.02/1000

    # Baseline:
    cfg.recon.mu = 0.019672

    # Some experiments use a polyenergetic spectrum but only one energy bin.
    if experimentName == "01_05_Physics_1ebin"                                       \
    or experimentName == "01_06_Physics_eNoiseOn_1ebin"                              \
    or experimentName == "01_07_Physics_qNoiseOn_1ebin"                              \
    or experimentName == "01_08_Physics_NoiseOn_1ebin":
        cfg.physics.energyCount = 1
        cfg.recon.mu = 0.02061

    # Some experiments use a monoenergetic spectrum.
    if experimentName == "01_09_Physics_Monoenergetic"                               \
    or experimentName == "01_10_Physics_eNoiseOn_Monoenergetic"                      \
    or experimentName == "01_11_Physics_qNoiseOn_Monoenergetic"                      \
    or experimentName == "01_12_Physics_NoiseOn_Monoenergetic":
        cfg.physics.monochromatic = 70
        cfg.recon.mu = 0.019326

    # Vary the recon kernel
    if experimentName == "02_01_Physics_NoiseOn_Recon_128mmFOV_R-LKernel":
        cfg.recon.kernelType = "R-L"
    if experimentName == "02_02_Physics_NoiseOn_Recon_128mmFOV_S-LKernel":
        cfg.recon.kernelType = "S-L"
    if experimentName == "02_03_Physics_NoiseOn_Recon_128mmFOV_SoftKernel":
        cfg.recon.kernelType = "Soft"
    if experimentName == "02_04_Physics_NoiseOn_Recon_128mmFOV_StandardKernel":
        cfg.recon.kernelType = "Standard"
    if experimentName == "02_05_Physics_NoiseOn_Recon_128mmFOV_BoneKernel":
        cfg.recon.kernelType = "Bone"

    # Vary the rotation time.
    if experimentName == "03_01_Physics_NoiseOn_Protocol_0p5rotation":
        cfg.protocol.rotationTime = 0.5
    if experimentName == "03_02_Physics_NoiseOn_Protocol_1p0rotation":
        cfg.protocol.rotationTime = 1.0
    if experimentName == "03_03_Physics_NoiseOn_Protocol_2p0rotation":
        cfg.protocol.rotationTime = 2.0

    # Vary the number of views.
    if experimentName == "04_01_Physics_NoiseOn_Protocol_100views":
        cfg.protocol.viewsPerRotation = 100
    if experimentName == "04_02_Physics_NoiseOn_Protocol_360views":
        cfg.protocol.viewsPerRotation = 360
    if experimentName == "04_03_Physics_NoiseOn_Protocol_1000views":
        cfg.protocol.viewsPerRotation = 1000
    cfg.protocol.viewCount = cfg.protocol.viewsPerRotation
    cfg.protocol.stopViewId = cfg.protocol.viewCount - 1

    # Vary the in-plane sampling.
    # Source sampling: sourece needs to be large to see the effect.
    if experimentName == "05_01_Physics_SourceSampling1_Recon_128mmFOV" \
    or experimentName == "05_02_Physics_SourceSampling2_Recon_128mmFOV" \
    or experimentName == "05_03_Physics_SourceSampling3_Recon_128mmFOV":
        cfg.scanner.focalspotWidth = 5.0
        cfg.scanner.focalspotLength = 5.0
    if experimentName == "05_01_Physics_SourceSampling1_Recon_128mmFOV":
        cfg.physics.srcXSampleCount = 1
    if experimentName == "05_02_Physics_SourceSampling2_Recon_128mmFOV":
        cfg.physics.srcXSampleCount = 2
    if experimentName == "05_03_Physics_SourceSampling3_Recon_128mmFOV":
        cfg.physics.srcXSampleCount = 3

    # Detector sampling: expect no effect with voxelized phantoms.
    if experimentName == "05_04_Physics_DetectorSampling1_Recon_128mmFOV":
        cfg.physics.colSampleCount = 1
    if experimentName == "05_05_Physics_DetectorSampling2_Recon_128mmFOV":
        cfg.physics.colSampleCount = 2
    if experimentName == "05_06_Physics_DetectorSampling3_Recon_128mmFOV":
        cfg.physics.colSampleCount = 3

    # View sampling: need to zoom in on a radial edge at the edge of the FOV to see the effect.
    if experimentName == "05_07_Physics_ViewSampling1_Recon_300mmFOV":
        cfg.physics.viewSampleCount = 1
    if experimentName == "05_08_Physics_ViewSampling2_Recon_300mmFOV":
        cfg.physics.viewSampleCount = 2
    if experimentName == "05_09_Physics_ViewSampling3_Recon_300mmFOV":
        cfg.physics.viewSampleCount = 3

    if experimentName == "05_01_Physics_SourceSampling1_Recon_128mmFOV"    \
    or experimentName == "05_02_Physics_SourceSampling2_Recon_128mmFOV"    \
    or experimentName == "05_03_Physics_SourceSampling3_Recon_128mmFOV"    \
    or experimentName == "05_04_Physics_DetectorSampling1_Recon_128mmFOV"  \
    or experimentName == "05_05_Physics_DetectorSampling2_Recon_128mmFOV"  \
    or experimentName == "05_06_Physics_DetectorSampling3_Recon_128mmFOV"  \
    or experimentName == "05_07_Physics_ViewSampling1_Recon_300mmFOV"      \
    or experimentName == "05_08_Physics_ViewSampling2_Recon_300mmFOV"      \
    or experimentName == "05_09_Physics_ViewSampling3_Recon_300mmFOV":
        cfg.displayWindowMin = -100             # In HU.
        cfg.displayWindowMax = 1300             # In HU.

    # Vary scatter
    if experimentName == "06_00_Scanner_64rows_Physics_NoScatter"      \
    or experimentName == "06_01_Scanner_64rows_Physics_ScatterScale1"  \
    or experimentName == "06_02_Scanner_64rows_Physics_ScatterScale8"  \
    or experimentName == "06_03_Scanner_64rows_Physics_ScatterScale64":
        cfg.phantom.filename = 'CatSimLogo_1024_128mmZ.json' # The phantom scale factor is 0.5, resulting in 64-mm Z.
        cfg.scanner.detectorRowsPerMod = 64
        cfg.scanner.detectorRowCount = cfg.scanner.detectorRowsPerMod
        cfg.recon.sliceCount = 64
        cfg.displayWindowMin = -200             # In HU.
        cfg.displayWindowMax = 200              # In HU.

    if experimentName == "06_01_Scanner_64rows_Physics_ScatterScale1"  \
    or experimentName == "06_02_Scanner_64rows_Physics_ScatterScale8"  \
    or experimentName == "06_03_Scanner_64rows_Physics_ScatterScale64":
        cfg.physics.scatterCallback = "Scatter_ConvolutionModel"
        cfg.physics.scatterKernelCallback = ""
    if experimentName == "06_01_Scanner_64rows_Physics_ScatterScale1":
        cfg.physics.scatterScaleFactor = 1
    if experimentName == "06_02_Scanner_64rows_Physics_ScatterScale8":
        cfg.physics.scatterScaleFactor = 8
    if experimentName == "06_03_Scanner_64rows_Physics_ScatterScale64":
        cfg.physics.scatterScaleFactor = 64
    
    # Some experiments use a 16-slice sim, and most of those use a 16-slice recon.
    if experimentName == "07_01_Scanner_16rows_Recon_1slice"                     \
    or experimentName == "07_02_Scanner_16rows_Recon_2slices"                    \
    or experimentName == "07_03_Scanner_16rows_Recon_16slices"                   \
    or experimentName == "08_01_Scanner_16rows_Phantom_offset0"                  \
    or experimentName == "08_02_Scanner_16rows_Phantom_offset+50mmX"             \
    or experimentName == "08_03_Scanner_16rows_Phantom_offset+50mmY"             \
    or experimentName == "08_04_Scanner_16rows_Phantom_offset+4mmZ"              \
    or experimentName == "08_05_Scanner_16rows_Phantom_offset+8mmZ"              \
    or experimentName == "09_01_Scanner_16rows_Recon_0p5mmSlices_offset0"        \
    or experimentName == "09_02_Scanner_16rows_Recon_0p5mmSlices_offset+22mmX"   \
    or experimentName == "09_03_Scanner_16rows_Recon_0p5mmSlices_offset+22mmY"   \
    or experimentName == "09_04_Scanner_16rows_Recon_0p5mmSlices_offset+1mmZ":
        cfg.scanner.detectorRowsPerMod = 16
        cfg.scanner.detectorRowCount = cfg.scanner.detectorRowsPerMod
        cfg.recon.sliceCount = 16
    # But some of them vary the number of recon slices. These only require one simulation.
    if experimentName == "07_01_Scanner_16rows_Recon_1slice":
        cfg.recon.sliceCount = 1
    if experimentName == "07_02_Scanner_16rows_Recon_2slices":
        cfg.recon.sliceCount = 2
    if experimentName == "07_03_Scanner_16rows_Recon_16slices":
        cfg.recon.sliceCount = 16

    if experimentName == "07_02_Scanner_16rows_Recon_2slices" \
    or experimentName == "07_03_Scanner_16rows_Recon_16slices":
        cfg.do_Sim = False
        copyFromExperimentName = "07_01_Scanner_16rows_Recon_1slice"
        copyFromPathname = os.path.join(experimentDirectory,  copyFromExperimentName,  copyFromExperimentName + ".prep")
        copyToPathname = cfg.resultsName + ".prep"
        shutil.copy2(copyFromPathname, copyToPathname)

    # For phantom and recon offset tests, use 360 views and don't use oversampling.
    if experimentName == "08_01_Scanner_16rows_Phantom_offset0"               \
    or experimentName == "08_02_Scanner_16rows_Phantom_offset+50mmX"          \
    or experimentName == "08_03_Scanner_16rows_Phantom_offset+50mmY"          \
    or experimentName == "08_04_Scanner_16rows_Phantom_offset+4mmZ"           \
    or experimentName == "08_05_Scanner_16rows_Phantom_offset+8mmZ"           \
    or experimentName == "09_01_Scanner_16rows_Recon_0p5mmSlices_offset0"        \
    or experimentName == "09_02_Scanner_16rows_Recon_0p5mmSlices_offset+22mmX"   \
    or experimentName == "09_03_Scanner_16rows_Recon_0p5mmSlices_offset+22mmY"   \
    or experimentName == "09_04_Scanner_16rows_Recon_0p5mmSlices_offset+1mmZ":
        cfg.protocol.viewsPerRotation = 360
        cfg.protocol.viewCount = cfg.protocol.viewsPerRotation
        cfg.protocol.stopViewId = cfg.protocol.viewCount - 1
        cfg.physics.srcXSampleCount = 1
        cfg.physics.srcYSampleCount = 1
        cfg.physics.rowSampleCount = 1
        cfg.physics.colSampleCount = 1
        cfg.physics.viewSampleCount = 1
        
    # Using a 16-slice sim and recon, vary the phantom offset.
    if experimentName == "08_01_Scanner_16rows_Phantom_offset0":
        cfg.phantom.centerOffset = [0.0, 0.0, 0.0]    
    if experimentName == "08_02_Scanner_16rows_Phantom_offset+50mmX":
        cfg.phantom.centerOffset = [50.0, 0.0, 0.0]    
    if experimentName == "08_03_Scanner_16rows_Phantom_offset+50mmY":
        cfg.phantom.centerOffset = [0.0, 50.0, 0.0]    
    if experimentName == "08_04_Scanner_16rows_Phantom_offset+4mmZ":
        cfg.phantom.centerOffset = [0.0, 0.0, 4.0]    
    if experimentName == "08_05_Scanner_16rows_Phantom_offset+8mmZ":
        cfg.phantom.centerOffset = [0.0, 0.0, 8.0]

    # Using a 16-slice sim and recon with 0.5-mm slices, vary the recon X, Y, and Z offset.
    if experimentName == "09_02_Scanner_16rows_Recon_0p5mmSlices_offset+22mmX" \
    or experimentName == "09_03_Scanner_16rows_Recon_0p5mmSlices_offset+22mmY" \
    or experimentName == "09_04_Scanner_16rows_Recon_0p5mmSlices_offset+1mmZ"  \
    or experimentName == "09_01_Scanner_16rows_Recon_0p5mmSlices_offset0":
        cfg.recon.sliceThickness = 0.5

    if experimentName == "09_01_Scanner_16rows_Recon_0p5mmSlices_offset0":
        cfg.recon.centerOffset = [0.0, 0.0, 0.0]    
    if experimentName == "09_02_Scanner_16rows_Recon_0p5mmSlices_offset+22mmX":
        cfg.recon.centerOffset = [22.0, 0.0, 0.0]    
    if experimentName == "09_03_Scanner_16rows_Recon_0p5mmSlices_offset+22mmY":
        cfg.recon.centerOffset = [0.0, 22.0, 0.0]
    if experimentName == "09_04_Scanner_16rows_Recon_0p5mmSlices_offset+1mmZ":
        cfg.recon.centerOffset = [0.0, 0.0, 1.0]

    # Only do the sim for the first one. Otherwise, copy the relevant projection data.
    if experimentName == "09_02_Scanner_16rows_Recon_0p5mmSlices_offset+22mmX" \
    or experimentName == "09_03_Scanner_16rows_Recon_0p5mmSlices_offset+22mmY" \
    or experimentName == "09_04_Scanner_16rows_Recon_0p5mmSlices_offset+1mmZ":
        copyFromExperimentName = "09_01_Scanner_16rows_Recon_0p5mmSlices_offset0"
        copyFromPathname = os.path.join(experimentDirectory,  copyFromExperimentName,  copyFromExperimentName + ".prep")
        copyToPathname = cfg.resultsName + ".prep"
        shutil.copy2(copyFromPathname, copyToPathname)
        cfg.do_Sim = False

    cfg.displayWindow = cfg.displayWindowMax - cfg.displayWindowMin
    cfg.displayLevel = (cfg.displayWindowMax + cfg.displayWindowMin)/2

    # For single-row simulations, use the native slice thickness.
    if cfg.scanner.detectorRowCount == 1:
        cfg.recon.sliceThickness = cfg.scanner.detectorRowSize*cfg.scanner.sid/cfg.scanner.sdd
    
    return cfg


def WLString(cfg):
    # Used below to create strings with the window/Level info.

    if cfg.recon.unit == 'HU':
        return "W/L = {:.0f}/{:.0f} {:s}; ".format(cfg.displayWindow, cfg.displayLevel, cfg.recon.unit)
    if cfg.recon.unit == '/cm':
        return "W/L = {:.2f}/{:.2f} {:s}; ".format(cfg.displayWindow, cfg.displayLevel, cfg.recon.unit)
    if cfg.recon.unit == '/mm':
        return "W/L = {:.3f}/{:.3f} {:s}; ".format(cfg.displayWindow, cfg.displayLevel, cfg.recon.unit)


def getReconImageTitle(cfg):

    experimentName = cfg.experimentName

    # Most experiments have only one image, so don't add that to the title.
    cfg.addSliceInfoToReconImageTitle = False

    if experimentName == "01_01_Baseline"                                          \
    or experimentName == "01_02_Physics_eNoiseOn"                                  \
    or experimentName == "01_03_Physics_qNoiseOn"                                  \
    or experimentName == "01_04_Physics_NoiseOn"                                   \
    or experimentName == "01_05_Physics_1ebin"                                     \
    or experimentName == "01_06_Physics_eNoiseOn_1ebin"                            \
    or experimentName == "01_07_Physics_qNoiseOn_1ebin"                            \
    or experimentName == "01_08_Physics_NoiseOn_1ebin"                             \
    or experimentName == "01_09_Physics_Monoenergetic"                             \
    or experimentName == "01_10_Physics_eNoiseOn_Monoenergetic"                    \
    or experimentName == "01_11_Physics_qNoiseOn_Monoenergetic"                    \
    or experimentName == "01_12_Physics_NoiseOn_Monoenergetic":
        formatString = WLString(cfg) + "cfg.physics.monochromatic = {}; cfg.physics.energyCount = {};"
        string1 = formatString.format(cfg.physics.monochromatic, cfg.physics.energyCount)
        formatString = "cfg.physics.enableElectronicNoise = {}; cfg.protocol.spectrumScaling = {}"
        string2 = formatString.format(cfg.physics.enableElectronicNoise, cfg.protocol.spectrumScaling)
        formatString = "cfg.physics.enableQuantumNoise = {}; cfg.protocol.mA = {}; cfg.recon.mu = {}"
        string3 = formatString.format(cfg.physics.enableQuantumNoise, cfg.protocol.mA, cfg.recon.mu)
        return string1 + "\n" + string2 + "\n" + string3

    if experimentName == "02_01_Physics_NoiseOn_Recon_128mmFOV_R-LKernel"           \
    or experimentName == "02_02_Physics_NoiseOn_Recon_128mmFOV_S-LKernel"           \
    or experimentName == "02_03_Physics_NoiseOn_Recon_128mmFOV_SoftKernel"          \
    or experimentName == "02_04_Physics_NoiseOn_Recon_128mmFOV_StandardKernel"      \
    or experimentName == "02_05_Physics_NoiseOn_Recon_128mmFOV_BoneKernel":
        formatString = WLString(cfg) + "cfg.recon.kernelType = {:s}"
        return formatString.format(cfg.recon.kernelType)

    if experimentName == "03_01_Physics_NoiseOn_Protocol_0p5rotation"               \
    or experimentName == "03_02_Physics_NoiseOn_Protocol_1p0rotation"               \
    or experimentName == "03_03_Physics_NoiseOn_Protocol_2p0rotation":
        formatString = WLString(cfg) + "cfg.protocol.rotationTime = {} s"
        return formatString.format(cfg.protocol.rotationTime)

    if experimentName == "04_01_Physics_NoiseOn_Protocol_100views"                  \
    or experimentName == "04_02_Physics_NoiseOn_Protocol_360views"                  \
    or experimentName == "04_03_Physics_NoiseOn_Protocol_1000views":
        formatString = WLString(cfg) + "cfg.protocol.viewsPerRotation = {}"
        return formatString.format(cfg.protocol.viewsPerRotation)

    if experimentName == "05_01_Physics_SourceSampling1_Recon_128mmFOV"             \
    or experimentName == "05_02_Physics_SourceSampling2_Recon_128mmFOV"             \
    or experimentName == "05_03_Physics_SourceSampling3_Recon_128mmFOV":
        formatString = WLString(cfg) +  "cfg.physics.srcXSampleCount = {}"
        return formatString.format(cfg.physics.srcXSampleCount)

    if experimentName == "05_04_Physics_DetectorSampling1_Recon_128mmFOV"           \
    or experimentName == "05_05_Physics_DetectorSampling2_Recon_128mmFOV"           \
    or experimentName == "05_06_Physics_DetectorSampling3_Recon_128mmFOV":
        formatString = WLString(cfg) +  "cfg.physics.colSampleCount = {}"
        return formatString.format(cfg.physics.colSampleCount)

    if experimentName == "05_07_Physics_ViewSampling1_Recon_300mmFOV"               \
    or experimentName == "05_08_Physics_ViewSampling2_Recon_300mmFOV"               \
    or experimentName == "05_09_Physics_ViewSampling3_Recon_300mmFOV":
        formatString = WLString(cfg) +  "cfg.physics.viewSampleCount = {}"
        return formatString.format(cfg.physics.viewSampleCount)

    if experimentName == "06_00_Scanner_64rows_Physics_NoScatter"           \
    or experimentName == "06_01_Scanner_64rows_Physics_ScatterScale1"       \
    or experimentName == "06_02_Scanner_64rows_Physics_ScatterScale8"       \
    or experimentName == "06_03_Scanner_64rows_Physics_ScatterScale64":
        # For multi-slice scans, add slice info to the title.
        cfg.addSliceInfoToReconImageTitle = True
        formatString = WLString(cfg) + "cfg.physics.scatterScaleFactor = {}"
        return formatString.format(cfg.physics.scatterScaleFactor)

    if experimentName == "07_01_Scanner_16rows_Recon_1slice"      \
    or experimentName == "07_02_Scanner_16rows_Recon_2slices"     \
    or experimentName == "07_03_Scanner_16rows_Recon_16slices":
        # For multi-slice scans, add slice info to the title.
        cfg.addSliceInfoToReconImageTitle = True
        formatString = "cfg.scanner.detectorRowCount = {}; cfg.recon.sliceCount = {}"
        return formatString.format(cfg.scanner.detectorRowCount, cfg.recon.sliceCount)

    if experimentName == "08_01_Scanner_16rows_Phantom_offset0"      \
    or experimentName == "08_02_Scanner_16rows_Phantom_offset+50mmX" \
    or experimentName == "08_03_Scanner_16rows_Phantom_offset+50mmY" \
    or experimentName == "08_04_Scanner_16rows_Phantom_offset+4mmZ"  \
    or experimentName == "08_05_Scanner_16rows_Phantom_offset+8mmZ":
        # For multi-slice scans, add slice info to the title.
        cfg.addSliceInfoToReconImageTitle = True
        formatString = "cfg.phantom.centerOffset[X, Y, Z] = [{}, {}, {}]"
        return formatString.format(cfg.phantom.centerOffset[0], cfg.phantom.centerOffset[1], cfg.phantom.centerOffset[2])

    if experimentName == "09_01_Scanner_16rows_Recon_0p5mmSlices_offset0"      \
    or experimentName == "09_02_Scanner_16rows_Recon_0p5mmSlices_offset+22mmX" \
    or experimentName == "09_03_Scanner_16rows_Recon_0p5mmSlices_offset+22mmY" \
    or experimentName == "09_04_Scanner_16rows_Recon_0p5mmSlices_offset+1mmZ":
        # For multi-slice scans, add slice info to the title.
        cfg.addSliceInfoToReconImageTitle = True
        formatString = "cfg.recon.centerOffset[X, Y, Z] = [{}, {}, {}]"
        return formatString.format(cfg.recon.centerOffset[0], cfg.recon.centerOffset[1], cfg.recon.centerOffset[2])


def runSim(cfg):

    import numpy as np
    import matplotlib.pyplot as plt

    experimentName = cfg.experimentName

    if cfg.do_Sim == True:
        print("**************************")
        print("* Running the simulation *")
        print("**************************")
        print("cfg.physics.enableElectronicNoise = {}".format(cfg.physics.enableElectronicNoise))
        print("cfg.physics.enableQuantumNoise = {}".format(cfg.physics.enableQuantumNoise))

        cfg.run_all()  # as specified by protocol.scanTypes

    ##--------- Show selected results - 4 views for each of selected rows.

    print("*********************************")
    print("* Plotting selected projections *")
    print("*********************************")

    projectionData = xc.rawread(cfg.resultsName + ".prep",
                    [cfg.protocol.viewCount, cfg.scanner.detectorRowCount, cfg.scanner.detectorColCount],
                    'float')

    rowCount = cfg.scanner.detectorRowCount
    if rowCount == 1:
        rowIndicesToPlot = [0]
    elif rowCount <= 8:
        # rowIndicesToPlot = range(8, 16)
        rowIndicesToPlot = range(0, rowCount)
    else:
        if experimentName == "08_01_Scanner_16rows_Phantom_offset0"       \
        or experimentName == "08_02_Scanner_16rows_Phantom_offset+50mmX"  \
        or experimentName == "08_03_Scanner_16rows_Phantom_offset+50mmY":
            # Plot the first 3 rows, a middle row, and the last 3 rows.
            rowIndicesToPlot = [0, 1, 2, int(rowCount/2), rowCount-3, rowCount-2, rowCount-1]
        elif experimentName == "08_04_Scanner_16rows_Phantom_offset+4mmZ":
            # Plot the 2 middle rows.
            rowIndicesToPlot = [int(rowCount/2)-1, int(rowCount/2)]
        elif experimentName == "08_05_Scanner_16rows_Phantom_offset+8mmZ":
            # Plot the last 4 rows.
            rowIndicesToPlot = [rowCount-4, rowCount-3, rowCount-2, rowCount-1]
        else:
            rowIndicesToPlot = range(0, rowCount)

    for rowIndexToPlot in rowIndicesToPlot:
        for viewIndexToPlot in range(0, cfg.protocol.viewCount, int(cfg.protocol.viewCount/4)):
            viewToPlot = projectionData[viewIndexToPlot, rowIndexToPlot, :]
            # viewToPlot = np.subtract(projectionData[viewIndexToPlot, rowIndexToPlot, :], projectionData[viewIndexToPlot, 15, :])
            plt.figure(int(viewIndexToPlot+1))
            plt.plot(viewToPlot)
            plt.title("All " + str(cfg.scanner.detectorColCount) + " columns"
                    + " of row(s) " + str([s + 1 for s in rowIndicesToPlot]) + " of " + str(cfg.scanner.detectorRowCount)
                    + ", view " + str(viewIndexToPlot+1) + " of " + str(cfg.protocol.viewCount))
            fileName = cfg.resultsName + "_" + "View_" + str(viewIndexToPlot+1)
            plt.savefig(fileName, bbox_inches='tight')

    if rowCount == 16:
        if experimentName == "08_01_Scanner_16rows_Phantom_offset0"       \
        or experimentName == "08_02_Scanner_16rows_Phantom_offset+50mmX"  \
        or experimentName == "08_03_Scanner_16rows_Phantom_offset+50mmY":
            # Confirm that symmetrical rows are exactly the same.
            rowsToDiff = np.array([[0, rowCount-1], [1, rowCount-2], [2, rowCount-3]])
        elif experimentName == "08_04_Scanner_16rows_Phantom_offset+4mmZ":
            # Compare the 4 middle rows.
            firstRowToDiff = int(rowCount/2 - 1)
            rowsToDiff = np.array([[firstRowToDiff,   firstRowToDiff+1],
                                [firstRowToDiff+1, firstRowToDiff+2],
                                [firstRowToDiff+2, firstRowToDiff+3]])
        elif experimentName == "08_05_Scanner_16rows_Phantom_offset+8mmZ":
            # Compare the last 5 rows.
            rowsToDiff = np.array([[rowCount-5, rowCount-4],
                                [rowCount-4, rowCount-3],
                                [rowCount-3, rowCount-2],
                                [rowCount-2, rowCount-1]])

        if experimentName == "08_01_Scanner_16rows_Phantom_offset0"       \
        or experimentName == "08_02_Scanner_16rows_Phantom_offset+50mmX"  \
        or experimentName == "08_03_Scanner_16rows_Phantom_offset+50mmY"  \
        or experimentName == "08_04_Scanner_16rows_Phantom_offset+4mmZ"   \
        or experimentName == "08_05_Scanner_16rows_Phantom_offset+8mmZ":
            numRowsToDiff = np.shape(rowsToDiff)[0]
            for rowIndex in range(0, numRowsToDiff):
                diff = np.subtract(projectionData[0, rowsToDiff[rowIndex, 0], :], projectionData[0, rowsToDiff[rowIndex, 1], :])
                print("Max diff of rows ", rowsToDiff[rowIndex, 0], " and ", rowsToDiff[rowIndex, 1], " is ", np.max(np.abs(diff)))

    plt.draw()
    plt.pause(1)
    if cfg.waitForKeypress:
        print("*******************************************")
        print("* Press Enter to close plots and continue *")
        input("*******************************************")
    
    plt.close('all')


def runRecon(cfg):

    print("******************************")
    print("* Running the reconstruction *")
    print("******************************")

    cfg = recon.recon(cfg)

    return cfg


def getUserPath():

    # Get the user-specified environment variable.
    userPath = os.environ.get('XCIST_UserPath')

    if userPath is None:
        raise Exception("******** Error! Please set the environment variable 'XCIST_UserPath'")
    # Convert to a list to see if more than one path was specified.
    userPath = userPath.split(";")
    if len(userPath) > 1:
        raise Exception("******** Error! Environment variable 'XCIST_UserPath' can only contain a single path.\nIt contains {:s}.".format(userPath))

    # Convert back to a simple string.
    userPath = userPath[0]
    if not os.path.exists(userPath):
        raise Exception("******** Error! Environment variable 'XCIST_UserPath' not found.".format(userPath))

    return userPath


##--------- Initialize

userPath = getUserPath()
xc.pyfiles.CommonTools.my_path.add_search_path(userPath)
experimentDirectory = os.path.join(userPath, "my_experiments", "experiment_CatSimLogo_SimAndRecon")

# Use the default cfg parameters found in Scanner_Default.cfg, Physics_Default.cfg, Protocol_Default.cfg.
# Use experiment-specific config files Phantom_CatSimLogo.cfg and Recon_CatSimLogo.cfg.

cfg = xc.CatSim(xc.pyfiles.CommonTools.my_path.find("cfg", "Phantom_CatSimLogo.cfg", ""),
                xc.pyfiles.CommonTools.my_path.find("cfg", "Recon_CatSimLogo.cfg", ""))

# These are changes to the defaults config parameters to be used for the "base" experiment,
# but some of these and some other defaults are overridden for certain experiments.

cfg.scanner.detectorRowsPerMod = 1
cfg.scanner.detectorRowCount = cfg.scanner.detectorRowsPerMod
cfg.scanner.detectorColOffset = 0.25

cfg.physics.enableQuantumNoise = 0
cfg.physics.enableElectronicNoise = 0
cfg.physics.energyCount = 12 # Using 120 kVp, so 10 kV/bin.

cfg.protocol.viewsPerRotation = 1000 # 360 is about the minimum to get minor aliasing, but need 1000 for minimal aliasing.
cfg.protocol.viewCount = cfg.protocol.viewsPerRotation
cfg.protocol.stopViewId = cfg.protocol.viewCount - 1
cfg.protocol.spectrumScaling = 0.931
cfg.protocol.mA = 300

cfg.recon.fov = 300.0
cfg.recon.displayImagePictures = True
cfg.recon.saveImagePictureFiles = True
cfg.recon.saveImageVolume = True
cfg.recon.saveSingleImages = True

# Top-level cfg parameters related to control of this experiment.
cfg.waitForKeypress = False             # Wait for keypress after plot display?
cfg.do_Sim = True                       # The simulation is usually run except when only varying recon parameters.
cfg.do_Recon = True                     # The recon is usually run except when only varying display parameters.
cfg.displayWindowMin = -200             # In HU.
cfg.displayWindowMax = 200              # In HU.

##--------- Define experiment names

# The following variable sets up all relevant parameters for experiments designed to evaluate XCIST using the CatSim logo phantom.
# Uncomment the ones you want to run.

experimentNames = [
    "01_01_Baseline",
    # "01_02_Physics_eNoiseOn",
    # "01_03_Physics_qNoiseOn",
    # "01_04_Physics_NoiseOn",
    # "01_05_Physics_1ebin",
    # "01_06_Physics_eNoiseOn_1ebin",
    # "01_07_Physics_qNoiseOn_1ebin",
    # "01_08_Physics_NoiseOn_1ebin",
    # "01_09_Physics_Monoenergetic",
    # "01_10_Physics_eNoiseOn_Monoenergetic",
    # "01_11_Physics_qNoiseOn_Monoenergetic",
    # "01_12_Physics_NoiseOn_Monoenergetic",

    # "02_01_Physics_NoiseOn_Recon_128mmFOV_R-LKernel", # Needs to be done before the next 4 because those use projections from this.
    # "02_02_Physics_NoiseOn_Recon_128mmFOV_S-LKernel",
    # "02_03_Physics_NoiseOn_Recon_128mmFOV_SoftKernel",
    # "02_04_Physics_NoiseOn_Recon_128mmFOV_StandardKernel",
    # "02_05_Physics_NoiseOn_Recon_128mmFOV_BoneKernel",

    # "03_01_Physics_NoiseOn_Protocol_0p5rotation",
    # "03_02_Physics_NoiseOn_Protocol_1p0rotation",
    # "03_03_Physics_NoiseOn_Protocol_2p0rotation",
    
    # "04_01_Physics_NoiseOn_Protocol_100views",
    # "04_02_Physics_NoiseOn_Protocol_360views",
    # "04_03_Physics_NoiseOn_Protocol_1000views",
    
    # "05_01_Physics_SourceSampling1_Recon_128mmFOV",
    # "05_02_Physics_SourceSampling2_Recon_128mmFOV",
    # "05_03_Physics_SourceSampling3_Recon_128mmFOV",
    # "05_04_Physics_DetectorSampling1_Recon_128mmFOV",
    # "05_05_Physics_DetectorSampling2_Recon_128mmFOV",
    # "05_06_Physics_DetectorSampling3_Recon_128mmFOV",
    # "05_07_Physics_ViewSampling1_Recon_300mmFOV",
    # "05_08_Physics_ViewSampling2_Recon_300mmFOV",
    # "05_09_Physics_ViewSampling3_Recon_300mmFOV",

    # "06_00_Scanner_64rows_Physics_NoScatter",
    # "06_01_Scanner_64rows_Physics_ScatterScale1",
    # "06_02_Scanner_64rows_Physics_ScatterScale8",
    # "06_03_Scanner_64rows_Physics_ScatterScale64",

    # "07_01_Scanner_16rows_Recon_1slice",
    # "07_02_Scanner_16rows_Recon_2slices",
    # "07_03_Scanner_16rows_Recon_16slices",

    # "08_01_Scanner_16rows_Phantom_offset0",
    # "08_02_Scanner_16rows_Phantom_offset+50mmX",
    # "08_03_Scanner_16rows_Phantom_offset+50mmY",
    # "08_04_Scanner_16rows_Phantom_offset+4mmZ",
    # "08_05_Scanner_16rows_Phantom_offset+8mmZ",

    # "09_01_Scanner_16rows_Recon_0p5mmSlices_offset0",  # Needs to be done before the next 3 because those use projections from this.
    # "09_02_Scanner_16rows_Recon_0p5mmSlices_offset+22mmX",
    # "09_03_Scanner_16rows_Recon_0p5mmSlices_offset+22mmY",
    # "09_04_Scanner_16rows_Recon_0p5mmSlices_offset+1mmZ",
]

# The current config is the base config, and will be used as the basis each time through the loop.
base = copy.deepcopy(cfg) 

for experimentIndex in range(0, len(experimentNames)):

    cfg = copy.deepcopy(base)
    experimentName = experimentNames[experimentIndex]
    resultsPath = os.path.join(experimentDirectory, experimentName)
    
    print("**************************")
    print("* Experiment: {:s}".format(experimentName))
    print("**************************")

    # Create the results folder if it doesn't exist.
    if not os.path.exists(resultsPath):
        os.makedirs(resultsPath)
    cfg.resultsName = os.path.join(resultsPath, experimentName)

    # Define the specific parameters for this experiment.
    cfg.experimentName = experimentName
    cfg = setExperimentParameters(cfg)
    # Get the title for the recon images.
    cfg.reconImageTitle = getReconImageTitle(cfg)
    # Run the simulation.
    runSim(cfg)
    # Run the recon.
    cfg = runRecon(cfg)

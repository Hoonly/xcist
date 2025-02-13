from math import ceil

def mapConfigVariablesToFDK(cfg):

    sid = cfg.scanner.sid
    sdd = cfg.scanner.sdd
    nMod = ceil(cfg.scanner.detectorColCount/cfg.scanner.detectorColsPerMod)
    rowSize = cfg.scanner.detectorRowSize
    modWidth = cfg.scanner.detectorColsPerMod*cfg.scanner.detectorColSize
    dectorYoffset = -cfg.scanner.detectorColOffset
    dectorZoffset = cfg.scanner.detectorRowOffset

    fov = cfg.recon.fov
    imageSize = cfg.recon.imageSize
    sliceCount = cfg.recon.sliceCount
    sliceThickness = cfg.recon.sliceThickness
    centerOffset = cfg.recon.centerOffset
    phantomOffset = cfg.phantom.centerOffset

    # The FDK recon seems to be using a "start view" rather than a "start angele".
    # This is a hack until that gets fixed.
    startView_at_view_angle_equals_0 = cfg.protocol.viewCount/2
    if cfg.recon.startAngle <= 180:
        startView = startView_at_view_angle_equals_0 + int(cfg.protocol.viewCount*cfg.recon.startAngle/360)
    elif cfg.recon.startAngle > 180:
        startView = startView_at_view_angle_equals_0 - int(cfg.protocol.viewCount*cfg.recon.startAngle/360)
    else:
        raise Exception("******** Error! Invalid start angle = {} specified. ********".format(cfg.recon.startAngle))

    kernelType = cfg.recon.kernelType

    return sid, sdd, nMod, rowSize, modWidth, dectorYoffset, dectorZoffset, \
           fov, imageSize, sliceCount, sliceThickness, centerOffset, phantomOffset, startView, kernelType

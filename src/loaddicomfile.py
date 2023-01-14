import numpy as np 
import pydicom
import os

def load_dcm_info(path, private=False):
    # Get patient's infomation in the first slice
    info_slice = pydicom.read_file(path + '/' + os.listdir(path)[0], force=True)

    if private:
        name = ('Patient Name', 'Private')
        id = ('Patient ID', 'Private')
        age = ('Patient Age', 'Private')
        sex = ('Patient Sex', 'Private')
        institution_name = ('Institution', 'Private')
        date = ('Date', 'Private')
        modality = ('Modality', 'Private')
        manufacturer = ('Manufacturer', 'Private')

    else:
        try:
            name = ('Patient Name', str(info_slice.PatientName).split('  ', 1)[1])
        except:
            name = ('Patient Name', 'Anonymous')
        try:
            id = ('Patient ID', str(info_slice.PatientID))
        except:
            id = ('Patient ID', 'Unknown')
        try:
            age = ('Patient Age', str(info_slice.PatientAge))
        except:
            age = ('Patient Age', 'Unknown')

        try:
            sex = ('Patient Sex', str(info_slice.PatientSex))
        except:
            sex = ('Patient Sex', 'Unknown')

        try:
            institution_name = ('Institution', str(info_slice.InstitutionName))
        except:
            institution_name = ('Institution', 'Unknown')

        try:
            date = ('Date', str(info_slice.InstanceCreationDate))
        except:
            date = ('Date', 'Unknown')

        try:
            modality = ('Modality', str(info_slice.Modality))
        except:
            modality = ('Modality', 'Unknown')

        try:
            manufacturer = ('Manufacturer', str(info_slice.Manufacturer))
        except:
            manufacturer = ('Manufacturer', 'Unknown')
    info = [name, id, age, sex, date, institution_name, modality, manufacturer]
    return info

def load_slices(path):
    filenames = os.listdir(path)
    slices = [pydicom.dcmread(f'{path}/{file}') for file in filenames]
    slices.sort(key = lambda x: int(x.InstanceNumber), reverse=True)  
    return slices

def get_pixels_hu(slices):
    image = np.stack([s.pixel_array for s in slices])
    # Convert to int16 (from sometimes int16), 
    # should be possible as values should always be low enough (<32k)
    image = image.astype(np.int16)

    # Set outside-of-scan pixels to 0
    # The intercept is usually -1024, so air is approximately 0
    image[image <= -1000] = 0
    
    # Convert to Hounsfield units (HU)
    for slice_number in range(len(slices)):
        
        intercept = slices[slice_number].RescaleIntercept
        slope = slices[slice_number].RescaleSlope
        
        if slope != 1:
            image[slice_number] = slope * image[slice_number].astype(np.float64)
            image[slice_number] = image[slice_number].astype(np.int16)
            
        image[slice_number] += np.int16(intercept)
    
    return np.array(image, dtype=np.int16)
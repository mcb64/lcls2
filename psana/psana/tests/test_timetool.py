import numpy as np
import os 
import IPython

from psana import DataSource

def twos_complement(hexstr,bits):
    value = int(hexstr,16)
    if value & (1 << (bits-1)):
        value -= 1 << bits
    return value

def get_fir_coefficients(myrun):
    my_kernel = []
    my_dict = myrun.configs[0].tmotimetool[0].timetoolConfig.cl.Application.__dict__["AppLane[0]"].Fex.FIR.__dict__
    for key in my_dict:
        mystring = my_dict[key]
        my_kernel.extend([twos_complement(mystring[i:i+2],8) for i in range(0,len(mystring),2)])

    return my_kernel
def test_timetool():

    firmware_edges = []
    software_edges = []

    dir_path = os.path.dirname(os.path.realpath(__file__))
    ds = DataSource(files=os.path.join(dir_path,'test_timetool.xtc2'))

    myrun = next(ds.runs())
    tt_detector_object = myrun.Detector('tmott')

    my_kernel = get_fir_coefficients(myrun)

    for nevt,evt in enumerate(myrun.events()):
        parsed_frame_object = tt_detector_object.ttalg.parsed_frame(evt)


        image = tt_detector_object.ttalg._image(evt)

        #known good length values that a raw frame can take
        assert image.shape == (2208,) or image.shape == (144,) or image.shape == (4272,)

        #make sure the edge position falls within the pixel range
        assert parsed_frame_object.edge_position >=0 and parsed_frame_object.edge_position <= 2047

        #validating that we're getting the correct number of pixels
        if(parsed_frame_object.prescaled_frame is not None):
            assert len(parsed_frame_object.prescaled_frame) == 2048
            
            firmware_edges.append(parsed_frame_object.edge_position)
            #IPython.embed()
            software_edges.append(np.argmax(np.convolve(parsed_frame_object.prescaled_frame,my_kernel)))

        if(parsed_frame_object.background_frame is not None):
            #validating that we're getting the correct number of pixels from the firmware
            assert len(parsed_frame_object.background_frame) == 2048

    my_cov = np.cov(firmware_edges,software_edges)  #need to separate out clusters of outliers here.
    print("covariance  = ",my_cov[0,1]/my_cov[0,0])
    assert nevt==598

if __name__ == "__main__":
    test_timetool()

"""
import numpy as np
import os 

from psana import DataSource
dir_path = os.path.dirname("psana/psana/tests/")
ds = DataSource(files=os.path.join(dir_path,'test_timetool.xtc2'))

myrun = next(ds.runs())
det = myrun.Detector('tmott')
my_events = myrun.events()
evt = next(my_events)
det.ttalg.parsed_frame(evt)

pFrame = det.ttalg.parsed_frame(evt)
pFrame.background_frame
pFrame.prescaled_frame
plt.plot([int(i) for i in pFrame.background_frame.data],'.')
plt.plot([int(i) for i in pFrame.background_frame],'.')
plt.plot([int(i) for i in pFrame.prescaled_frame],'.')
history



"""

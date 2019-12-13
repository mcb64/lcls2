from psalg.configdb.typed_json import cdict
import psalg.configdb.configdb as cdb
import sys
import IPython


def write_to_daq_config_db(prescaling):

    #database contains collections which are sets of documents (aka json objects).
    #each type of device has a collection.  The elements of that collection are configurations of that type of device.
    #e.g. there will be OPAL, EVR, and YUNGFRAU will be collections.  How they are configured will be a document contained within that collection
    #Each hutch is also a collection.  Documents contained within these collection have an index, alias, and list of devices with configuration IDs
    #How is the configuration of a state is described by the hutch and the alias found.  E.g. TMO and BEAM.  TMO is a collection.  
    #BEAM is an alias of some of the documents in that collection. The document with the matching alias and largest index is the current 
    #configuration for that hutch and alias.  
    #When a device is configured, the device has a unique name OPAL7.  Need to search through document for one that has an NAME called OPAL7.  This will have
    #have two fields "collection" and ID field (note how collection here is a field. ID points to a unique document).  This collection field and 
    #ID point to the actuall Mongo DB collection and document

    create = True
    dbname = 'configDB'     #this is the name of the database running on the server.  Only client care about this name.
    instrument = 'TST'      #

    mycdb = cdb.configdb('mcbrowne:psana@psdb-dev:9306', instrument, create, dbname)    #mycdb.client.drop_database('configDB_szTest') will drop the configDB_szTest database
    #mycdb.client.drop_database('sioanDB')
    mycdb.add_alias("BEAM")
    mycdb.add_device_config('timetool')
    
    top = cdict()
    top.setInfo('timetool', 'tmotimetool', 'serial1234', 'No comment')
    top.setAlg('timetoolConfig', [0,0,1])

    #There are many rogue fields, but only a handful need to be configured.  what are they?
    #1)  the FIR coefficients.  after accounting for parabolic fitting detection
    #2)  start and stop?
    #3)  main by pass. (still isn't working with FEX in hardware, but does in simulation.)
    #4)  all prescalers.  This has potential to crash linux kernel during hi rate and low prescaling.  How to add protection?  Slow ramp?
    #5)  low pass on background
    #6)  op code (now called readout group). there's no rogue counter part of this yet.
    #7)  the load coefficients bit needs to set to one for the FIR coefficients to be written.
    #8)  camera rate and soft or hard trigger. The soft trigger is for offline testing.  For users or just for me?
    #9)  the batcher bypass so soft trigger doesn't halt.

    ######################################################################
    ####### Keeping it simple.  Just what Giaccomo will need #############
    ######################################################################

    ########################################
    #####        prescaling          #######
    ########################################
    top.set("cl.Application.AppLane[0].Prescale.ScratchPad",int(prescaling),'UINT32')                     # testing ability to write to database
    top.set("cl.Application.AppLane[0].Prescale.DialInPreScaling",2,'UINT32')                            # prescaled raw data 
    top.set("cl.Application.AppLane[0].Fex.background_prescaler.DialInPreScaling",3,'UINT32')            # prescaled raw backgrounds (may consider accumulated backgrounds instead)
    ########################################
    #####      initial fir filter    #######
    ########################################
    top.set("cl.Application.AppLane[0].Fex.FIR.CoefficientSet0","7f7f7f7f",'CHARSTR')                      #high part of step 
    top.set("cl.Application.AppLane[0].Fex.FIR.CoefficientSet1","7f7f7f7f",'CHARSTR')                      #high part of step 
    top.set("cl.Application.AppLane[0].Fex.FIR.CoefficientSet2","7f7f7f7f",'CHARSTR')                      #high part of step 
    top.set("cl.Application.AppLane[0].Fex.FIR.CoefficientSet3","7f7f7f7f",'CHARSTR')                      #high part of step 
    top.set("cl.Application.AppLane[0].Fex.FIR.CoefficientSet4","81818181",'CHARSTR')                      #low  part of step
    top.set("cl.Application.AppLane[0].Fex.FIR.CoefficientSet5","81818181",'CHARSTR')                      #low  part of step
    top.set("cl.Application.AppLane[0].Fex.FIR.CoefficientSet6","81818181",'CHARSTR')                      #low  part of step
    top.set("cl.Application.AppLane[0].Fex.FIR.CoefficientSet7","81818181",'CHARSTR')                      #low  part of step

    top.set("cl.Application.AppLane[0].Fex.FIR.LoadCoefficients","1",'CHARSTR')                             #low  part of step.  Having a value of 1  causes a segfault in pgpread_timetool.cc.  But not in tt_config.py. 

    ########################################
    #####      time constants        #######
    ########################################
    top.set("cl.Application.AppLane[0].Fex.FrameIIR.TimeConstant",8,'UINT32')


    ########################################
    #####      subtraction enabled     #####
    ########################################
    top.set("cl.Application.AppLane[0].Fex.FrameSubtractor.SubtractionActive",0,'UINT32')                   #turn background subtract on


    ########################################
    #####      Piranha Settings        #####
    ########################################
    #commands can be sent manually using cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4._tx.sendString('GCP') 
    #to manually querry a camera hardware setting cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4._tx.sendString('get 'stm') 

    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.CLS",0,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.CLM",2,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.DST",0,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.FFM",0,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.FRS",2,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.LPC",0,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.ROI[0]",1,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.ROI[1]",2048,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.SAC",1,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.SAD[0]",1,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.SAD[1]",1,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.SAD[2]",2048,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.SAM",0,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.SBH",1,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.SBR",9600,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.SBV",1,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.SCD",0,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.SEM",0,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.SET",5000,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.SMM",0,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.SPF",0,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.SSB",0,'UINT32')    
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.SSF",2,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.SSG",1,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.STG",2,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.STM",1,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.SVM",0,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.USD",1,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.USL",1,'UINT32')
    top.set("cl.ClinkFeb[0].ClinkTop.Ch[0].UartPiranha4.USS",1,'UINT32')
    


    #the object hierarchy paths (e.g. cl.Application.AppLane[0]... yadayadayada) for a device can be found by implementing
    #pr.generateAddressMap where pr comes from "import rogue as pr".  For this to work, one has to be logged onto the machine hosting the firmware   
    #that interacts with rogue.  This particular register map can be found in the lcls2-pcie-apps directory cloned from https://github.com/slaclab/lcls2-pcie-apps.

    mycdb.modify_device('BEAM', top)

    #IPython.embed()


if __name__ == "__main__":
    write_to_daq_config_db(sys.argv[1])

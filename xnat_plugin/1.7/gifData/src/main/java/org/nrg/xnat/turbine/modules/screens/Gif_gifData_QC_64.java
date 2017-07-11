package org.nrg.xnat.turbine.modules.screens;


import java.io.File;
import java.util.Iterator;

import org.apache.turbine.util.RunData;
import org.apache.velocity.context.Context;
import org.nrg.xdat.om.GifGifdata;
import org.nrg.xdat.om.XnatImagesessiondata;
import org.nrg.xdat.om.XnatResourcecatalog;
import org.nrg.xdat.turbine.modules.screens.SecureReport;

public class Gif_gifData_QC_64 extends SecureReport {
        public static org.apache.log4j.Logger logger = org.apache.log4j.Logger.getLogger(Gif_gifData_QC_64.class);
    public void finalProcessing(RunData data, Context context) {
        try{
            org.nrg.xdat.om.GifGifdata gif = new org.nrg.xdat.om.FsFsdata(item);
            context.put("gif",gif); 
            XnatImagesessiondata om = gif.getImageSessionData();
            context.put("mr",om);
        } catch(Exception e){
            logger.debug("Gif_gifData_QC_64", e);
        }
    }
}

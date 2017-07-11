
import org.nrg.framework.annotations.XnatPlugin;
import org.nrg.framework.annotations.XnatDataModel;

@XnatPlugin(value = "gifDataXnatPlugin", name = "DAX gifData XNAT 1.7 Plugin", 
            description = "This is the DAX gifData data type for XNAT 1.7 Plugin.",
            dataModels = {@XnatDataModel(value = "gif:gifData", singular = "Processing", plural="Processings", code = "Proc")})
public class gifDataXnatPlugin {
}

import com.sap.it.api.mapping.*;

def String parseCostCenter(String costCenter){
	if (costCenter.toString().size() > 4  && costCenter.toString().substring(0,4).equals('CAEU'))
		costCenter = costCenter.toString().substring(4);
		
    return costCenter;
}
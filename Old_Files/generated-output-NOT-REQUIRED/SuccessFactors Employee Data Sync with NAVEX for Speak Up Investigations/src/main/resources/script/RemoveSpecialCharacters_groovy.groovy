import com.sap.it.api.mapping.*;

def String removeSpecialCharacters(String input){
	return (input.replaceAll("[^a-zA-Z0-9-]+"," "));
}
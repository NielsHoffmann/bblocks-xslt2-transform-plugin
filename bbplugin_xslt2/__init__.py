import logging
# pyrefly: ignore [missing-import]
from saxonche import PySaxonProcessor
from typing import AnyStr


# Configure logging to see Saxon errors in the BBlocks build logs
logger = logging.getLogger(__name__)



class SaxonXsltTransformer:
    """
    A Transformer plugin that supports XSLT 2.0 using the Saxon-HE 
    (SaxonChe) library.
    """
    
    transform_types = ['xslt2']
    # Define supported mime types
    default_inputs = ['application/xml']
    default_outputs = ['application/xml']
   
    def transform(self, metadata) -> AnyStr | None:
        try:
            # SaxonChe requires a context manager to manage the C++ native resources
            with PySaxonProcessor(license=False) as proc:
                xslt_proc = proc.new_xslt30_processor()
                
                # Load the input XML
                # Saxon handles encoding internally from the string or bytes provided
                builder = proc.new_document_builder()
                input_node = builder.parse_xml(xml_text=metadata.input_data)
                
                # Compile the XSLT 2.0 stylesheet
                executable = xslt_proc.compile_stylesheet(stylesheet_text=metadata.transform_content)
                
                if not executable:
                    # Saxon-specific error retrieval
                    logger.error("Saxon compilation failed.")
                    return None

                # Perform transformation
                result_str = executable.transform_to_string(xdm_node=input_node)
                
                return str(result_str)

        except Exception as e:
            logger.error(f"Error during Saxon XSLT transformation: {str(e)}")
            raise e
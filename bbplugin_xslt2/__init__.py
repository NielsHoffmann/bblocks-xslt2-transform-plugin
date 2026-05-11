import logging
from typing import AnyStr
from ogc.bblocks.models import TransformMetadata, Transformer
from saxonche import PySaxonProcessor

# Configure logging to see Saxon errors in the BBlocks build logs
logger = logging.getLogger(__name__)

# Define supported mime types
default_inputs = ['application/xml', 'text/xml']
default_outputs = ['application/xml', 'text/xml', 'text/html', 'text/plain']

class SaxonXsltTransformer(Transformer):
    """
    A Transformer plugin that supports XSLT 2.0 and 3.0 using the Saxon-HE 
    (SaxonChe) library.
    """

    def __init__(self):
        # We register this under the 'xslt' type, or a custom name like 'xslt-saxon'
        # to avoid conflict with the built-in lxml-based XSLT 1.0 transformer.
        super().__init__(['xslt-saxon', 'xslt2', 'xslt3'], default_inputs, default_outputs)

    def do_transform(self, metadata: TransformMetadata) -> AnyStr | None:
        try:
            # SaxonChe requires a context manager to manage the C++ native resources
            with PySaxonProcessor(license=False) as proc:
                xslt_proc = proc.new_xslt30_processor()
                
                # Load the input XML
                # Saxon handles encoding internally from the string or bytes provided
                input_node = proc.parse_xml(xml_text=metadata.input_data)
                
                # Compile the XSLT 2.0/3.0 stylesheet
                executable = xslt_proc.compile_stylesheet(stylesheet_text=metadata.transform_content)
                
                if not executable:
                    # Saxon-specific error retrieval
                    logger.error("Saxon compilation failed.")
                    return None

                # Perform transformation
                result_str = executable.transform_to_string(xdm_node=input_node)
                
                return result_str

        except Exception as e:
            logger.error(f"Error during Saxon XSLT transformation: {str(e)}")
            return None
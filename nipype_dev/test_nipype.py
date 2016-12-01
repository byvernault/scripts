# Import the nipype module
import nipype

# Optional: Use the following lines to increase verbosity of output
nipype.config.set('logging', 'workflow_level',  'CRITICAL')
nipype.config.set('logging', 'interface_level', 'CRITICAL')
nipype.logging.update_logging(nipype.config)

# Run the test: Increase verbosity parameter for more info
nipype.test(verbose=0)

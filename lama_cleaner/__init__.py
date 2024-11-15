import os

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

import warnings

warnings.simplefilter("ignore", UserWarning)

# oceanus common settings
# This file is because it is used for both A and B,
# and to recommend the use of a hard link .
# When you git clone from repository,
# please create a hard link to run the init.sh.
from os import environ
from importlib import import_module

OCEANUS_SETTINGS = environ.get("OCEANUS_SETTINGS", "common.bizocean_settings")
globals().update(import_module(OCEANUS_SETTINGS).__dict__)

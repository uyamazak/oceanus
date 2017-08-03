from importlib import import_module
from common.utils import oceanus_logging
from .hook_settings import INSTALLED_HOOKS
logger = oceanus_logging()


def get_installed_hooks():
    loaded_hooks = []
    for hook_string in INSTALLED_HOOKS:
        module_name, class_name = hook_string.rsplit(".", 1)
        pkg = import_module(module_name)
        loaded_hooks.append(getattr(pkg, class_name))

    return loaded_hooks


hooks = get_installed_hooks()
logger.info("installed_hooks: {}".format(hooks))


def apply_hooks(message, redis):
    count = 0
    for hook in hooks:
        count += hook(message, redis).main()
    return count

from .hook_settings import INSTALLED_HOOKS
from importlib import import_module


def get_installed_hooks():
    hooks = []
    for pkg_name, func_name in INSTALLED_HOOKS:
        pkg = import_module(pkg_name)
        hooks.append(getattr(pkg, func_name))

    return hooks


hooks = get_installed_hooks()


def apply_hooks(message, redis):
    count = 0
    for hook in hooks:
        count += hook(message, redis).main()
    return count

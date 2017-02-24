from . import hook_settings


def apply_hook(message, redis):
    count = 0
    for hook in hook_settings.INSTALLED_HOOKS:
        count += hook(message, redis).main()
    return count

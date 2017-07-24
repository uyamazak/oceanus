# from .hooks.bizocean import BizoceanHook
# from .hooks.movieform import MovieformHook
# from .hooks.docreq import DocreqHook
from importlib import import_module

# this is set of ("path.to.package_name", "HookFunctionName")
INSTALLED_HOOKS = (("hook.hooks.bizocean", "BizoceanHook"),
                   ("hook.hooks.movieform", "MovieformHook"),
                   ("hook.hooks.docreq", "DocreqHook"))

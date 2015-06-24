
from docido.toolbox.text import to_unicode

def exception_to_unicode(e, traceback=False):
    """Convert an `Exception` to an `unicode` object.

    In addition to `to_unicode`, this representation of the exception
    also contains the class name and optionally the traceback.
    """
    message = '%s: %s' % (e.__class__.__name__, to_unicode(e))
    if traceback:
        from docido.toolbox import get_last_traceback
        traceback_only = get_last_traceback().split('\n')[:-2]
        message = '\n%s\n%s' % (to_unicode('\n'.join(traceback_only)), message)
    return message

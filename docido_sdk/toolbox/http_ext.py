
__all__ = [
    'activate_pyopenssl_for_urllib3',
]


def activate_pyopenssl_for_urllib3():
    """
    Workaround issue described here:
    https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning

    """
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()

import six

if six.PY2:
    from pathlib2 import Path
else:
    from pathlib import Path  # noqa: F401 pragma: no cover

import six
import contextlib


@contextlib.contextmanager
def user_input(input, stdin):
    r"""Write `input` on `stdin`.

    If `input` is a list, join it using `\n`.
    """
    # Remove possibly existing previous input:
    stdin.seek(0)
    stdin.truncate()
    if not isinstance(input, six.string_types):
        input = '\n'.join(input)
    stdin.write(input)
    stdin.seek(0)
    yield

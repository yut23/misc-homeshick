import warnings

import prompt_toolkit.input.ansi_escape_sequences as esc_seqs
from prompt_toolkit.input.ansi_escape_sequences import _get_reverse_ansi_sequences
from prompt_toolkit.keys import Keys

# from IPython import get_ipython
# from prompt_toolkit.enums import DEFAULT_BUFFER
# from prompt_toolkit.filters import emacs_insert_mode, has_focus
# from prompt_toolkit.key_binding.bindings.named_commands import get_by_name
# from prompt_toolkit.keys import ALL_KEYS, Keys


def patch() -> None:
    _CTRL_BACKSPACE_SEQ = "\x1b[127;5u"
    if _CTRL_BACKSPACE_SEQ in esc_seqs.ANSI_SEQUENCES:
        warnings.warn(
            f"CSI-u ctrl-backspace fully supported in prompt_toolkit; please remove {__file__}"
        )
        return

    # delete this section when PR #1383 is merged
    # https://github.com/prompt-toolkit/python-prompt-toolkit/pull/1383
    if hasattr(Keys, "ControlBackspace"):
        warnings.warn(
            f"Keys.ControlBackspace already present in prompt_toolkit; please remove this section from {__file__}"
        )
        key = Keys.ControlBackspace  # pylint: disable=no-member
    else:
        # just map to the same as alt-backspace
        key = (Keys.Escape, Keys.Backspace)

        # waiting on https://github.com/prompt-toolkit/python-prompt-toolkit/issues/993
        # # from https://github.com/prompt-toolkit/python-prompt-toolkit/issues/892#issuecomment-489247031
        # Keys.ControlBackspace = "c-backspace"
        # ALL_KEYS.append("c-backspace")
        # # bind c-backspace to do the same as alt-backspace
        # # from https://stackoverflow.com/a/53525144
        # ip = get_ipython()
        # registry = ip.pt_app.key_bindings
        # registry.add_binding(
        #     Keys.ControlBackspace,
        #     filter=(has_focus(DEFAULT_BUFFER) & emacs_insert_mode),
        # )(get_by_name("backward-kill-word"))

    # from patch_for_linux.txt in https://github.com/prompt-toolkit/python-prompt-toolkit/issues/1294
    esc_seqs.ANSI_SEQUENCES[_CTRL_BACKSPACE_SEQ] = key
    esc_seqs.REVERSE_ANSI_SEQUENCES = _get_reverse_ansi_sequences()


patch()

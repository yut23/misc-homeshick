"""Improve traceback code highlighting.

* Change the hardcoded traceback background color to a bold underline.
  <https://github.com/ipython/ipython/issues/13446>
* Set the pygments style to TerminalInteractiveShell.highlighting_style.
  <https://github.com/ipython/ipython/issues/12270>, maybe?
"""
from IPython.core.ultratb import (
    Optional,
    Terminal256Formatter,
    TracebackType,
    VerboseTB,
    get_ipython,
    get_style_by_name,
    inspect,
    stack_data,
)

if True:  # pylint: disable=using-constant-test  # to match indentation
    # pylint: disable=too-many-locals

    def patched_get_records(
        self, etb: TracebackType, number_of_lines_of_context: int, tb_offset: int
    ):
        assert etb is not None
        context = number_of_lines_of_context - 1
        after = context // 2
        before = context - after
        if self.has_colors:
            # --- start changes ---
            ipinst = get_ipython()
            if (
                ipinst is not None
                and hasattr(ipinst, "highlighting_style")
                and ipinst.highlighting_style != "legacy"
            ):
                if isinstance(ipinst.highlighting_style, str):
                    style = get_style_by_name(ipinst.highlighting_style)
                else:
                    style = ipinst.highlighting_style
            else:
                style = get_style_by_name("default")
            # s/"bg:ansiyellow"/"bold underline"/
            style = stack_data.style_with_executing_node(style, "bold underline")
            # --- end changes ---
            formatter = Terminal256Formatter(style=style)
        else:
            formatter = None
        options = stack_data.Options(
            before=before,
            after=after,
            pygments_formatter=formatter,
        )

        try:
            # pylint: disable-next=import-outside-toplevel
            from IPython.core.ultratb import FAST_THRESHOLD, FrameInfo
        except ImportError:
            # before https://github.com/ipython/ipython/pull/13947
            # fmt: off
            return list(stack_data.FrameInfo.stack_data(etb, options=options))[tb_offset:]

        # Let's estimate the amount of code we will have to parse/highlight.
        cf: Optional[TracebackType] = etb
        max_len = 0
        tbs = []
        while cf is not None:
            try:
                source_file = inspect.getsourcefile(etb.tb_frame)
                lines, first = inspect.getsourcelines(etb.tb_frame)
            except OSError:
                max_len = float("-inf")
                break
            max_len = max(max_len, first + len(lines))
            tbs.append(cf)
            cf = cf.tb_next

        if max_len > FAST_THRESHOLD:
            FIs = []
            for tb in tbs:
                frame = tb.tb_frame
                lineno = (frame.f_lineno,)
                code = frame.f_code
                filename = code.co_filename
                FIs.append(FrameInfo("Raw frame", filename, lineno, frame, code))
            return FIs
        res = list(stack_data.FrameInfo.stack_data(etb, options=options))[tb_offset:]
        res = [FrameInfo._from_stack_data_FrameInfo(r) for r in res]
        return res
        # fmt: on


def patch() -> None:
    VerboseTB.get_records = patched_get_records


patch()

from __future__ import annotations

import os
import tempfile

from aqt import mw, gui_hooks
from aqt.qt import QAction, QKeySequence
from aqt.utils import qconnect, show_info
from aqt.import_export.importing import import_file



def import_tsv_from_clipboard() -> None:
    """Import TSV data from the system clipboard."""
    text = mw.app.clipboard().text()
    if not text.strip():
        show_info("Clipboard is empty.")
        return

    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".tsv", encoding="utf-8") as fp:
        fp.write(text)
        path = fp.name

    try:
        import_file(mw, path)
    finally:
        try:
            os.unlink(path)
        except Exception:
            pass


def on_file_menu_did_init(menu) -> None:
    action = QAction("Import TSV from Clipboard", menu)
    action.setShortcut(QKeySequence("Ctrl+Shift+V"))
    qconnect(action.triggered, import_tsv_from_clipboard)
    menu.addAction(action)


# Register the menu hook
gui_hooks.file_menu_did_init.append(on_file_menu_did_init)

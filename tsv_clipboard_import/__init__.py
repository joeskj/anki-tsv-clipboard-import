from __future__ import annotations

import os
import tempfile

from aqt import gui_hooks, mw
from aqt.import_export.importing import import_file
from aqt.qt import QAction, QKeySequence
from aqt.utils import qconnect, show_info

_temp_paths: list[str] = []


def import_tsv_from_clipboard() -> None:
    """Import TSV data from the system clipboard."""
    text = mw.app.clipboard().text()
    if not text.strip():
        show_info("Clipboard is empty.")
        return

    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".tsv", encoding="utf-8"
    ) as fp:
        fp.write(text)
        path = fp.name

    _temp_paths.append(path)
    import_file(mw, path)
    try:
        os.unlink(path)
        _temp_paths.remove(path)
    except Exception:
        pass


def _add_menu_action(menu) -> None:
    """Add the TSV import action to the given menu."""
    action = QAction("Import TSV from Clipboard", menu)
    action.setShortcut(QKeySequence("Ctrl+Shift+V"))
    qconnect(action.triggered, import_tsv_from_clipboard)
    # try to position the action directly below the built-in Import option
    import_action = getattr(mw.form, "actionImport", None)

    if import_action:
        actions = menu.actions()
        try:
            idx = actions.index(import_action)
        except ValueError:
            idx = -1

        insert_before = (
            actions[idx + 1] if idx != -1 and idx + 1 < len(actions) else None
        )
        if insert_before:
            menu.insertAction(insert_before, action)
        else:
            menu.addAction(action)
    else:
        menu.addAction(action)


# Register the menu hook
def on_main_window_did_init() -> None:
    _add_menu_action(mw.form.menuCol)


gui_hooks.main_window_did_init.append(on_main_window_did_init)


def _cleanup_temp_files() -> None:
    for path in _temp_paths:
        try:
            os.unlink(path)
        except Exception:
            pass
    _temp_paths.clear()


gui_hooks.profile_will_close.append(_cleanup_temp_files)

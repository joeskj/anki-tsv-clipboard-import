from __future__ import annotations

import os
import tempfile

from aqt import gui_hooks, mw
from aqt.import_export.importing import import_file
from aqt.qt import QAction, QInputDialog, QKeySequence
from aqt.utils import qconnect, show_info

DEFAULT_SHORTCUT = "Ctrl+Shift+V"

_temp_paths: list[str] = []


def get_shortcut() -> str:
    """Return the configured shortcut string."""
    config = mw.addonManager.getConfig(__name__) or {}
    shortcut = config.get("shortcut", DEFAULT_SHORTCUT)
    return shortcut


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


def show_settings_dialog() -> None:
    """Prompt the user for a new shortcut and store it."""
    current = get_shortcut()
    shortcut, ok = QInputDialog.getText(
        mw,
        "TSV Clipboard Import Settings",
        "Shortcut:",
        text=current,
    )
    if ok and shortcut:
        config = mw.addonManager.getConfig(__name__) or {}
        config["shortcut"] = shortcut
        mw.addonManager.writeConfig(__name__, config)
        show_info("Shortcut updated. Restart Anki to apply changes.")


def _add_menu_action(menu) -> None:
    """Add the TSV import action to the given menu."""
    action = QAction("Import TSV from Clipboard", menu)
    action.setShortcut(QKeySequence(get_shortcut()))
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


def _add_settings_action(menu) -> None:
    """Add a settings action to configure the shortcut."""
    action = QAction("TSV Clipboard Import Settings", menu)
    qconnect(action.triggered, show_settings_dialog)
    menu.addAction(action)


# Register the menu hook
def on_main_window_did_init() -> None:
    _add_menu_action(mw.form.menuCol)
    _add_settings_action(mw.form.menuTools)


gui_hooks.main_window_did_init.append(on_main_window_did_init)


def _cleanup_temp_files() -> None:
    for path in _temp_paths:
        try:
            os.unlink(path)
        except Exception:
            pass
    _temp_paths.clear()


gui_hooks.profile_will_close.append(_cleanup_temp_files)

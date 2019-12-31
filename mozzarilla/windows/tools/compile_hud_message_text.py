import os

from pathlib import Path
from traceback import format_exc

from reclaimer.strings.strings_compilation import compile_hud_message_text
from supyr_struct.util import is_path_empty
from binilla.windows.filedialog import askopenfilename


def hud_message_text_from_hmt(app, fp=None):
    load_dir = app.last_data_load_dir
    tags_dir = app.tags_dir
    data_dir = app.data_dir
    if is_path_empty(tags_dir):
        tags_dir = Path("")
    if is_path_empty(data_dir):
        data_dir = Path("")

    if is_path_empty(load_dir):
        load_dir = data_dir

    if is_path_empty(fp):
        fp = askopenfilename(
            initialdir=load_dir, parent=app,
            filetypes=(("HUD messages", "*.hmt"), ("All", "*")),
            title="Select hmt file to turn into a hud_message_text tag")

    fp = Path(fp)
    if is_path_empty(fp):
        return

    try:
        app.last_data_load_dir = fp.parent

        print("Creating hud_message_text from this hmt file:")
        print("    %s" % fp)
        with fp.open("r", encoding="utf-16-le") as f:
            hmt_string_data = f.read()
    except Exception:
        print(format_exc())
        print("    Could not load hmt file.")
        return
    
    try:
        rel_filepath = fp.relative_to(data_dir)
    except ValueError:
        rel_filepath = Path("hud messages")

    rel_filepath = rel_filepath.with_suffix(".hud_message_text")

    tag_path = Path("")
    if not is_path_empty(rel_filepath):
        tag_path = tags_dir.joinpath(rel_filepath)

    # make the tag window
    window = app.load_tags(
        filepaths=(tag_path, ) if tag_path.is_file() else "",
        def_id='hmt ')
    if not window:
        return

    window = window[0]
    window.is_new_tag = False
    window.tag.filepath = tag_path
    window.tag.rel_filepath = rel_filepath

    error = compile_hud_message_text(window.tag, hmt_string_data)

    # reload the window to display the newly entered info
    window.reload()
    app.update_tag_window_title(window)
    if error:
        print("    Errors occurred while compiling. " +
              "Tag will not be automatically saved.")
        window.is_new_tag = True
    elif not tag_path.is_file():
        # save the tag if it doesnt already exist
        app.save_tag()

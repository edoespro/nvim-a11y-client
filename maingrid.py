from nvimevents import NvimEvents    
from gridmanager import GridManager
from uievents import UIEvents
from nvimgrid import NvimGrid
global manager

def register_all_handlers(ui_events):

    ui_events.register_handler("grid_resize", on_resize)
    ui_events.register_handler("grid_line", on_line)
    ui_events.register_handler("win_viewport", on_viewport)
    ui_events.register_handler("msg_set_pos", on_msg_pos)
    ui_events.register_handler("hl_attr_define", on_hl_define)
    ui_events.register_handler("grid_cursor_goto", on_cursor)
    ui_events.register_handler("flush", on_flush)
    ui_events.register_handler("grid_scroll", on_scroll)


def on_scroll(args):
    g_id, top, bot, left, right, rows, cols = args[1]
    grid = manager.get_grid(g_id)
    if grid:
        grid.scroll(top, bot, left, right, rows)




def on_resize(args):
    g_id, w, h = args[1]
    if g_id in manager.grids:
        manager.grids[g_id].resize(w, h)
    else:
        manager.grids[g_id] = NvimGrid(g_id, w, h)

def on_line(args):
    for g_id, row, col, cells, wrap in args[1:]:
        grid = manager.get_grid(g_id)
        if grid: 
            grid.update_line(row, col, cells)


def on_viewport(args):
    g_id, win_handle, *rest = args[1]
    grid = manager.get_grid(g_id)
    if grid:
        grid.win_handle = win_handle
        # Disparamos l:a consulta manual de posición
        manager.pull_window_info(g_id, win_handle)


def on_msg_pos(args):
    g_id, row, scrolled, sep, zindex, comp = args[1]
    grid = manager.get_grid(g_id)
    if grid: grid.set_position(row, 0, zindex) # Fila absoluta en grid 1


def on_hl_define(args):
    hl_id, rgb_attrs, cterm_attrs, info = args[1]
    manager.highlight_table[hl_id] = rgb_attrs # Guardar colores


def on_cursor(args):
    g_id, r, c = args[1]
    manager.cursor_pos.update({'grid': g_id, 'row': r, 'col': c})


def on_flush(args):
    manager.render_to_terminal()


def main():
    events = NvimEvents()
    events.configure()
    global manager
    manager = GridManager(events.nvim)
    register_all_handlers(events.ui)
    events.run_loop()


if __name__ == "__main__":
    main()

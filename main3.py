from loopmgr import EventLoopManager
from loophandler import EventLoopHandler
import asyncio
import sys

#Punto de Entrada

def main():
    # Obtener la instancia única de EventLoopManager
    mgr = EventLoopManager()
    handler = EventLoopHandler(mgr)
    mgr.start_loop()
    
    #if not manager.connect():
        #sys.exit(1)

    # Registro de múltiples manejadores por evento (tal como se solicitó)
    #manager.add_notification_handler('grid_resize', handle_grid_resize)
    #manager.add_notification_handler('flush', handle_flush)
    #manager.add_notification_handler('mode_change', handle_mode_change)

    # Inicializar la UI de Neovim
    #manager.ui_attach(80, 24)

    # Iniciar la escucha asíncrona de eventos
    #manager.start_loop()


if __name__ == "__main__":
    main()
    print("awaitado")


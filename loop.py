import sys
from collections import defaultdict
from connection import NvimConnection  # Asegúrate de que exista el módulo connection.py


class EventLoopManager:
    """
    Singleton que gestiona el bucle de mensajes de Neovim.
    Recibe notificaciones y requests, y las despacha a los handlers registrados.
    Utiliza una instancia de NvimConnection para obtener los mensajes.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Evitar reinicialización si ya fue inicializado
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True

        self.notification_handlers = defaultdict(list)  # { nombre_evento: [handler1, handler2, ...] }
        self.request_handlers = defaultdict(list)       # { nombre_request: [handler1, handler2, ...] }

        self._connection = NvimConnection()
        self._running = False

    
    @property
    def nvim(self):
        return self._connection.nvim
    
    # ---------- Registro de manejadores ----------
    def register_notification(self, method_name: str, handler: callable):
        """Agrega un manejador para una notificación."""
        self.notification_handlers[method_name].append(handler)

    def unregister_notification(self, method_name: str, handler: callable):
        """Elimina un manejador de notificación."""
        if method_name in self.notification_handlers:
            try:
                self.notification_handlers[method_name].remove(handler)
            except ValueError:
                pass

    def register_request(self, method_name: str, handler: callable):
        """Agrega un manejador para una solicitud (request)."""
        self.request_handlers[method_name].append(handler)

    def unregister_request(self, method_name: str, handler: callable):
        """Elimina un manejador de request."""
        if method_name in self.request_handlers:
            try:
                self.request_handlers[method_name].remove(handler)
            except ValueError:
                pass

    # ---------- Despachadores ----------
    def _dispatch_notification(self, name: str, args):
        """Invoca los manejadores registrados para una notificación."""
       # print(f"En loop.notification {name}")
        handlers = self.notification_handlers.get(name, [])
        if not handlers:
            # Opcional: podrías registrar en log o ignorar silenciosamente
            print(f"⚠ Sin manejador para la notificación '{name}'")
            return
        for handler in handlers:
            try:
                handler(args)
            except Exception as e:
                print(f"Error en manejador de notificación '{name}': {e}")

    def _dispatch_request(self, name: str, args):
        print(f"En loop.request {name}")
        """Invoca los manejadores registrados para un request."""
        handlers = self.request_handlers.get(name, [])
        if not handlers:
            print(f"⚠ Sin manejador para el request '{name}'")
            return
        for handler in handlers:
            try:
                handler(args)
            except Exception as e:
                print(f"Error en manejador de request '{name}': {e}")

    def stop(self):
        """Detiene el bucle de eventos de manera segura."""
        if self._running:
            self._running = False
            # Opcional: podrías usar un mecanismo para desbloquear next_message,
            # pero la detención se hará efectiva en la próxima iteración.
            print("Solicitud de parada enviada.")



    def connect(self, method='socket', **kwargs):
        """Solo conecta, no arranca el bucle."""
        if self._running:
            print("Ya hay un bucle en ejecución.")
            return False
        if method == 'socket':
            ok = self._connection.attach_socket(**kwargs)
        elif method == 'tcp':
            ok = self._connection.attach_tcp(**kwargs)
        elif method == 'child':
            ok = self._connection.attach_child(**kwargs)
        else:
            raise ValueError(f"Método desconocido: {method}")
        if ok:
            print("Conexión establecida. Listo para iniciar el bucle.")
        return ok
    
    
    def run_loop3(self):
        """Arranca el bucle de mensajes (bloqueante)."""
        if not self._connection.is_attached:
            raise ConnectionError("Conéctese primero usando connect().")
        self._running = True
        print("Bucle de eventos iniciado. Ctrl+C para salir.")
        try:
            while self._running:
                msg = self._connection.nvim.next_message()
                if msg is None or len(msg) < 2:
                    continue
                if msg[0] == "notification":
                    self._dispatch_notification(msg[1], msg[2])
                elif msg[0] == "request":
                    self._dispatch_request(msg[1], msg[2])
        except KeyboardInterrupt:
            print("\n✓ Interrupción por teclado.")
        finally:
            self._running = False
            #self._connection.detach()
            print("Bucle detenido y conexión cerrada.")
    
   

    def run_loop(self):
        """Arranca el bucle de mensajes (bloqueante)."""
        if not self._connection.is_attached:
            raise ConnectionError("Conéctese primero usando connect().")
        self._running = True
        print("Bucle de eventos iniciado. Ctrl+C para salir.")
        try:
            self.nvim.run_loop(self._dispatch_request,self._dispatch_notification, None)
        except KeyboardInterrupt:
            print("\n✓ Interrupción por teclado.")
        finally:
            self._running = False
            #self._connection.detach()
            print("Bucle detenido y conexión cerrada.")













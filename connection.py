import pynvim

SOCKET_PATH = '/data/data/com.termux/files/home/nvim.sock'

class NvimConnection:
    """
    Gestiona la conexión a una instancia de Neovim.
    Soporta conexiones por socket Unix, TCP y como proceso hijo (--embed).
    Expone el objeto nvim para interactuar con la API.
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
        
        self._nvim = None
        self._is_attached = False

    # ---------- Propiedades ----------
    @property
    def nvim(self):
        """Devuelve el objeto nvim si la conexión está activa."""
        if not self._is_attached:
            raise ConnectionError("No hay conexión activa a Neovim.")
        return self._nvim

    @property
    def is_attached(self):
        return self._is_attached

    # ---------- Métodos de conexión ----------
    def attach_socket(self, path: str = SOCKET_PATH) -> bool:
        """
        Conecta a Neovim a través de un socket Unix.
        Retorna True si se conectó exitosamente.
        """
        if self._is_attached:
            print("Ya existe una conexión activa. Desconecte primero.")
            return False
        try:
            self._nvim = pynvim.attach('socket', path=path)
            self._is_attached = True
            print(f"✓ Conectado a Neovim en socket: {path}")
            return True
        except Exception as e:
            print(f"✗ Error al conectar por socket: {e}")
            return False

    def attach_tcp(self, address: str = '127.0.0.1', port: int = 8080) -> bool:
        """
        Conecta a Neovim a través de TCP.
        Retorna True si se conectó exitosamente.
        """
        if self._is_attached:
            print("Ya existe una conexión activa. Desconecte primero.")
            return False
        try:
            self._nvim = pynvim.attach('tcp', address=address, port=port)
            self._is_attached = True
            print(f"✓ Conectado a Neovim en TCP {address}:{port}")
            return True
        except Exception as e:
            print(f"✗ Error al conectar por TCP: {e}")
            return False

    def attach_child(self, argv: list = None) -> bool:
        """
        Inicia Neovim como proceso hijo y se conecta a él.
        Parámetros adicionales pueden pasarse en 'argv'.
        Retorna True si se conectó exitosamente.
        """
        if self._is_attached:
            print("Ya existe una conexión activa. Desconecte primero.")
            return False
        if argv is None:
            argv = ['nvim', '--embed']
        try:
            self._nvim = pynvim.attach('child', argv=argv)
            self._is_attached = True
            print(f"✓ Conectado a Neovim embebido con argumentos: {argv}")
            return True
        except Exception as e:
            print(f"✗ Error al conectar como hijo: {e}")
            return False

    # ---------- Método de desconexión ----------
    def detach(self) -> bool:
        """
        Cierra la conexión activa (si existe) y libera recursos.
        Retorna True si se cerró correctamente.
        """
        if not self._is_attached:
            return False
        try:
            # Si es proceso hijo, podemos intentar cerrarlo ordenadamente
            self._nvim.quit()
        except Exception:
            pass
        finally:
            self._nvim = None
            self._is_attached = False
            print("✓ Conexión a Neovim cerrada.")
            return True

    # ---------- Método de conveniencia ----------
    def request(self, method: str, *args):
        """
        Realiza una llamada a la API de Neovim.
        Equivale a self.nvim.request(method, *args).
        """
        return self.nvim.request(method, *args)

    # ---------- Soporte para with statement ----------
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.detach()
        return False

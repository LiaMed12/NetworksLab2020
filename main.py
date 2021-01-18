from src.server import Server
from src.config import ServerConfig

if __name__ == '__main__':
    server = Server(ServerConfig)
    server.run()

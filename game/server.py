from server_scenes.server_main_scene import ServerMainScene


class Server:
    def __init__(self, fake_net):
        self.current_scene = ServerMainScene(fake_net)

    def run(self, dt):
        self.current_scene.run(dt)

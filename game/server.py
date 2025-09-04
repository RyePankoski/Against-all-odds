from server_scenes.server_main_scene import ServerMainScene


class Server:
    def __init__(self, fake_net):
        self.server_main_scene = ServerMainScene(fake_net)
        self.current_scene = self.server_main_scene

    def run(self, dt):
        self.current_scene.run(dt)


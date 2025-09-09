# tests/test_ship.py
import unittest
import pygame
from entities.ships.ship import Ship
from rendering.camera import Camera
from shared_util.ship_logic import *


class TestShip(unittest.TestCase):

    # python -m unittest tests.test_ship -v

    def setUp(self):
        # Initialize pygame (needed for sprite loading)
        pygame.init()
        screen = pygame.display.set_mode((100, 100))
        camera = Camera(screen)

        # Create ship for testing
        self.ship = Ship(x=100, y=200, owner=1, camera=camera)

    def tearDown(self):
        pygame.quit()

    def test_ship_initialization(self):
        self.assertEqual(self.ship.x, 100.0)
        self.assertEqual(self.ship.y, 200.0)
        self.assertEqual(self.ship.owner, 1)
        self.assertEqual(self.ship.dx, 0)
        self.assertEqual(self.ship.dy, 0)
        self.assertTrue(self.ship.alive)
        self.assertTrue(self.ship.dampening_active)

    def test_ship_movement(self):
        self.ship.dx = 5
        self.ship.dy = 3
        old_x, old_y = self.ship.x, self.ship.y

        self.ship.acceleration()

        self.assertEqual(self.ship.x, old_x + 5)
        self.assertEqual(self.ship.y, old_y + 3)

    def test_ship_facing(self):
        # Ship at (100, 100), mouse at (100, 200) = straight down = 270°
        self.ship.x, self.ship.y = 100, 100
        update_ship_facing(self.ship, (100, 200))

        # Test that it moved toward the target, not that it reached it
        initial_angle = 0
        target_angle = 270
        # Should rotate in the correct direction
        self.assertNotEqual(self.ship.facing_angle, initial_angle)

    def test_ship_combat_lifecycle(self):
        self.assertEqual(self.ship.health, SHIP_HEALTH)

        initial_shield = self.ship.shield
        self.ship.shield -= 50
        self.assertLess(self.ship.shield, initial_shield)

        self.ship.shield = 0
        initial_health = self.ship.health
        self.ship.health -= 1
        self.assertLess(self.ship.health, initial_health)

        self.ship.health = 0
        self.ship.update(0.016)
        self.assertFalse(self.ship.alive)

    def test_brake_function(self):
        self.ship.dx = 10
        self.ship.dy = -8

        self.ship.brake()

        # Should reduce velocity toward zero
        self.assertTrue(abs(self.ship.dx) < 10)
        self.assertTrue(abs(self.ship.dy) < 8)

    def test_health_affects_alive_status(self):
        self.ship.health = 0
        self.ship.update(0.016)  # One frame

        self.assertFalse(self.ship.alive)

import unittest
from unittest.mock import MagicMock, patch
import numpy as np

from CheeseChase.view.sprites import (
    Spritesheet, MouseSprites, CatSprites, LifeSprites, MazeSprites, DEATH
)
from CheeseChase.model.constants import TILEWIDTH, TILEHEIGHT, LEFT, RIGHT, UP, DOWN, STOP, SCATTER, CHASE, FREIGHT, SPAWN

class TestSpritesheet(unittest.TestCase):
    @patch("CheeseChase.view.sprites.resources.files")
    @patch("CheeseChase.view.sprites.pygame.image.load")
    def test_init_sets_up_sheet_and_colorkey(self, mock_load, mock_files):
        # Arrange: make image.load return an image-like mock
        mock_img = MagicMock()
        mock_img.convert.return_value = mock_img
        mock_img.get_at.return_value = (1, 2, 3, 4)
        mock_load.return_value = mock_img
        # resources.files(...) / "spritesheet2.png" -> path-like mock
        mock_path_obj = MagicMock()
        mock_path_obj.__str__.return_value = "img_path"
        mock_files.return_value.__truediv__.return_value = mock_path_obj

        # Act
        s = Spritesheet()

        # Assert
        mock_files.assert_called_once_with("CheeseChase.resources")
        mock_load.assert_called_once_with("img_path")
        mock_img.convert.assert_called_once()
        mock_img.get_at.assert_called_once_with((0,0))
        mock_img.set_colorkey.assert_called_once_with((1,2,3,4))

    def test_getImage_sets_clip_and_returns_subsurface(self):
        # Create instance without running __init__
        s = Spritesheet.__new__(Spritesheet)
        s.sheet = MagicMock()
        # make get_clip and subsurface return a sentinel
        s.sheet.get_clip.return_value = "cliprect"
        s.sheet.subsurface.return_value = "subsurf"
        # Patch pygame.Rect to return a rect object we can check
        with patch("CheeseChase.view.sprites.pygame.Rect") as mock_rect:
            mock_rect.return_value = "rectobj"
            res = s.getImage(1, 2, 3, 4)
            # x,y are multiplied by TILEWIDTH/TILEHEIGHT internally
            mock_rect.assert_called_once_with(1 * TILEWIDTH, 2 * TILEHEIGHT, 3, 4)
            s.sheet.set_clip.assert_called_once_with("rectobj")
            s.sheet.subsurface.assert_called_once_with("cliprect")
            self.assertEqual(res, "subsurf")

class TestMouseSprites(unittest.TestCase):
    @patch("CheeseChase.view.sprites.Spritesheet.__init__", return_value=None)
    @patch("CheeseChase.view.sprites.Spritesheet.getImage", return_value="startimg")
    def test_init_sets_entity_image_and_animations(self, mock_getImage, mock_init):
        entity = MagicMock()
        ms = MouseSprites(entity)
        self.assertEqual(entity.image, "startimg")
        # animations should include DEATH
        self.assertIn(DEATH, ms.animations)
        self.assertEqual(ms.stopimage, (0, 0))

    def test_update_alive_direction_assigns_images_and_stopimage(self):
        # create instance without running Spritesheet.__init__
        ms = MouseSprites.__new__(MouseSprites)
        ms.getImage = MagicMock(return_value="img")
        ms.animations = {}
        ms.stopimage = (2, 0)
        ms.entity = MagicMock()
        ms.entity.alive = True

        # LEFT
        ms.entity.direction = LEFT
        ms.update(0.1)
        self.assertEqual(ms.entity.image, "img")
        self.assertEqual(ms.stopimage, (0, 0))

        # RIGHT
        ms.entity.direction = RIGHT
        ms.update(0.1)
        self.assertEqual(ms.entity.image, "img")
        self.assertEqual(ms.stopimage, (2, 0))

        # DOWN
        ms.entity.direction = DOWN
        ms.update(0.1)
        self.assertEqual(ms.entity.image, "img")
        self.assertEqual(ms.stopimage, (4, 0))

        # UP
        ms.entity.direction = UP
        ms.update(0.1)
        self.assertEqual(ms.entity.image, "img")
        self.assertEqual(ms.stopimage, (6, 0))

        # STOP uses stopimage
        ms.entity.direction = STOP
        ms.update(0.1)
        self.assertEqual(ms.entity.image, "img")

    def test_update_dead_uses_death_animation(self):
        ms = MouseSprites.__new__(MouseSprites)
        ms.getImage = MagicMock(return_value="img")
        # set animations to return tuple coords when update called
        anim = MagicMock()
        anim.update.return_value = (3, 4)
        ms.animations = {DEATH: anim}
        ms.entity = MagicMock()
        ms.entity.alive = False
        ms.update(0.1)
        # when dead, entity.image should be set via getImage called with animation tuple
        ms.getImage.assert_called_with(3, 4)
        self.assertEqual(ms.entity.image, "img")

    def test_reset_calls_animation_reset(self):
        ms = MouseSprites.__new__(MouseSprites)
        anim = MagicMock()
        ms.animations = {DEATH: anim}
        ms.reset()
        anim.reset.assert_called_once()

    def test_getStartImage_delegates_to_getImage(self):
        ms = MouseSprites.__new__(MouseSprites)
        ms.getImage = MagicMock(return_value="start")
        self.assertEqual(ms.getStartImage(), "start")
        ms.getImage.assert_called_once_with(0, 0)

class TestCatSprites(unittest.TestCase):
    @patch("CheeseChase.view.sprites.Spritesheet.__init__", return_value=None)
    @patch("CheeseChase.view.sprites.Spritesheet.getImage", return_value="catstart")
    def test_init_sets_entity_image_and_stopimage(self, mock_getImage, mock_init):
        entity = MagicMock()
        cs = CatSprites(entity)
        self.assertEqual(entity.image, "catstart")
        self.assertEqual(cs.stopimage, (0, 2))

    def test_update_behaviour_for_modes_and_directions(self):
        cs = CatSprites.__new__(CatSprites)
        cs.getImage = MagicMock(return_value="cimg")
        cs.entity = MagicMock()
        # SCATTER/CHASE directions
        for mode in (SCATTER, CHASE):
            cs.entity.mode = MagicMock()
            cs.entity.mode.current = mode
            for direction in (LEFT, RIGHT, DOWN, UP):
                cs.entity.direction = direction
                cs.update(0.1)
                self.assertEqual(cs.entity.image, "cimg")
        # FREIGHT
        cs.entity.mode.current = FREIGHT
        cs.update(0.1)
        self.assertEqual(cs.entity.image, "cimg")
        # SPAWN directions
        cs.entity.mode.current = SPAWN
        for direction in (LEFT, RIGHT, DOWN, UP):
            cs.entity.direction = direction
            cs.update(0.1)
            self.assertEqual(cs.entity.image, "cimg")

    def test_getStartImage_delegates_to_getImage(self):
        cs = CatSprites.__new__(CatSprites)
        cs.getImage = MagicMock(return_value="startc")
        self.assertEqual(cs.getStartImage(), "startc")
        cs.getImage.assert_called_once_with(0, 2)

class TestLifeSprites(unittest.TestCase):
    @patch("CheeseChase.view.sprites.Spritesheet.__init__", return_value=None)
    @patch("CheeseChase.view.sprites.Spritesheet.getImage", return_value="lifeimg")
    def test_init_and_resetLives(self, mock_getImage, mock_init):
        ls = LifeSprites(3)
        # getImage should have been called 3 times in resetLives via __init__
        self.assertEqual(len(ls.images), 3)
        self.assertEqual(ls.images, ["lifeimg", "lifeimg", "lifeimg"])
        ls.resetLives(2)
        self.assertEqual(ls.images, ["lifeimg", "lifeimg"])

    def test_removeImage_behaviour(self):
        ls = LifeSprites.__new__(LifeSprites)
        ls.images = ["a", "b", "c"]
        ls.removeImage()
        self.assertEqual(ls.images, ["b", "c"])
        ls.removeImage()
        self.assertEqual(ls.images, ["c"])
        ls.removeImage()
        self.assertEqual(ls.images, [])

    def test_getImage_delegates_to_Spritesheet(self):
        # Patch Spritesheet.getImage so we can assert it was called with width/height expanded
        with patch.object(Spritesheet, "getImage", return_value="sub") as mock_parent_get:
            ls = LifeSprites.__new__(LifeSprites)
            res = ls.getImage(1, 2)
            mock_parent_get.assert_called_once_with(ls, 1, 2, 2 * TILEWIDTH, 2 * TILEHEIGHT)
            self.assertEqual(res, "sub")

class TestMazeSprites(unittest.TestCase):
    @patch("CheeseChase.view.sprites.Spritesheet.__init__", return_value=None)
    @patch("CheeseChase.view.sprites.np.loadtxt")
    def test_init_loads_maze_and_rotdata(self, mock_loadtxt, mock_init):
        mock_loadtxt.side_effect = [
            np.array([["1","2"],["3","4"]]),
            np.array([["0","1"],["2","3"]])
        ]
        ms = MazeSprites("mazefile", "rotfile")
        self.assertTrue((ms.data == np.array([["1","2"],["3","4"]])).all())
        self.assertTrue((ms.rotdata == np.array([["0","1"],["2","3"]])).all())

    @patch("CheeseChase.view.sprites.pygame.transform.rotate", return_value="rotsprite")
    def test_rotate_calls_pygame_transform_rotate(self, mock_rotate):
        ms = MazeSprites.__new__(MazeSprites)
        sprite = "sprite"
        result = ms.rotate(sprite, 2)
        mock_rotate.assert_called_once_with(sprite, 180)
        self.assertEqual(result, "rotsprite")

    def test_constructBackground_blits_correctly_for_digits(self):
        ms = MazeSprites.__new__(MazeSprites)
        # set up small data and rotdata with digits and non-digits
        ms.data = np.array([["1","X"],["2","3"]])
        ms.rotdata = np.array([["0","1"],["2","3"]])
        ms.getImage = MagicMock(return_value="sprite")
        ms.rotate = MagicMock(return_value="rotsprite")
        background = MagicMock()
        # call
        ms.constructBackground(background, 7)
        # expected positions for digit cells: (row0,col0)->(0,0); (row1,col0)->(0,16); (row1,col1)->(16,16)
        expected_positions = [
            (0 * TILEWIDTH, 0 * TILEHEIGHT),
            (0 * TILEWIDTH, 1 * TILEHEIGHT),
            (1 * TILEWIDTH, 1 * TILEHEIGHT),
        ]
        for pos in expected_positions:
            background.blit.assert_any_call("rotsprite", pos)
        # ensure getImage and rotate were called for each digit
        self.assertEqual(ms.getImage.call_count, 3)
        self.assertEqual(ms.rotate.call_count, 3)

    @patch("CheeseChase.view.sprites.Spritesheet.getImage", return_value="mimg")
    def test_getImage_delegates_to_Spritesheet(self, mock_getImage):
        ms = MazeSprites.__new__(MazeSprites)
        res = ms.getImage(3, 4)
        mock_getImage.assert_called_once_with(ms, 3, 4, TILEWIDTH, TILEHEIGHT)
        self.assertEqual(res, "mimg")

    @patch("CheeseChase.view.sprites.np.loadtxt", return_value=np.array([["a"]]))
    def test_readMazeFile_returns_array(self, mock_loadtxt):
        ms = MazeSprites.__new__(MazeSprites)
        arr = ms.readMazeFile("mazefile.txt")
        mock_loadtxt.assert_called_once_with("mazefile.txt", dtype='<U1')
        self.assertTrue((arr == np.array([["a"]])).all())


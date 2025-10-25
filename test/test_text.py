import unittest
from unittest.mock import MagicMock, patch
from CheeseChase.view.text import Text, TextGroup
from CheeseChase.model.constants import RED, TILEHEIGHT, SCORETXT, LEVELTXT, READYTXT, PAUSETXT, GAMEOVERTXT

class TestTextAndTextGroup(unittest.TestCase):
    def setUp(self):
        # Patch resources.files used to build font path and pygame.font.Font so no real pygame/font is required
        files_patcher = patch("CheeseChase.view.text.resources.files")
        font_patcher = patch("CheeseChase.view.text.pygame.font.Font")

        self.mock_files = files_patcher.start()
        self.addCleanup(files_patcher.stop)

        self.mock_font_class = font_patcher.start()
        self.addCleanup(font_patcher.stop)

        # resources.files(...) / "file.ttf" -> return value whose str() is "fontpath"
        mock_path_obj = MagicMock()
        mock_path_obj.__str__.return_value = "fontpath"
        # make the / operator return our path-like mock
        self.mock_files.return_value.__truediv__.return_value = mock_path_obj

        # create a mock font instance with render method
        self.mock_font_inst = MagicMock()
        self.mock_font_inst.render.return_value = "label-surface"
        self.mock_font_class.return_value = self.mock_font_inst

    def test_text_initialization_and_font_setup(self):
        t = Text("Hello", RED, 10, 20, 12)
        # font constructed with path string and size
        self.mock_font_class.assert_called_with("fontpath", 12)
        # label created using font.render
        self.mock_font_inst.render.assert_called_with("Hello", 1, RED)
        # attributes set
        self.assertEqual(t.text, "Hello")
        self.assertEqual(t.color, RED)
        self.assertEqual(t.size, 12)
        self.assertEqual(t.position.asTuple(), (10, 20))
        self.assertFalse(t.destroy)
        self.assertEqual(t.label, "label-surface")

    def test_setText_creates_new_label(self):
        t = Text("Old", RED, 0, 0, 8)
        self.mock_font_inst.render.reset_mock()
        t.setText("NewValue")
        self.mock_font_inst.render.assert_called_with("NewValue", 1, RED)
        self.assertEqual(t.text, "NewValue")

    def test_update_lifespan_and_destroy(self):
        # lifespan set to small value should mark destroy after update
        t = Text("Tmp", RED, 0, 0, 8, time=0.05)
        self.assertFalse(t.destroy)
        t.update(0.06)
        self.assertTrue(t.destroy)
        self.assertIsNone(t.lifespan)
        self.assertEqual(t.timer, 0)

    def test_render_blits_when_visible_and_skips_when_not(self):
        t = Text("Hi", RED, 3, 4, 10)
        screen = MagicMock()
        # ensure position.asTuple returns tuple (3,4)
        t.position.asTuple = MagicMock(return_value=(3, 4))
        t.visible = True
        t.label = "lbl"
        t.render(screen)
        screen.blit.assert_called_once_with("lbl", (3, 4))
        screen.blit.reset_mock()
        t.visible = False
        t.render(screen)
        screen.blit.assert_not_called()

    def test_textgroup_initialization_setupText_and_show_hide(self):
        tg = TextGroup()
        # setupText should have created several default texts
        self.assertIn(SCORETXT, tg.alltext)
        self.assertIn(LEVELTXT, tg.alltext)
        self.assertIn(READYTXT, tg.alltext)
        self.assertIn(PAUSETXT, tg.alltext)
        self.assertIn(GAMEOVERTXT, tg.alltext)

        # READYTXT is shown by TextGroup.__init__ via showText(READYTXT)
        self.assertTrue(tg.alltext[READYTXT].visible)

        # showText should hide others and show READYTXT (call again to exercise the method)
        tg.showText(READYTXT)
        self.assertTrue(tg.alltext[READYTXT].visible)
        # hideText hides the special texts
        tg.hideText()
        self.assertFalse(tg.alltext[READYTXT].visible)
        self.assertFalse(tg.alltext[PAUSETXT].visible)
        self.assertFalse(tg.alltext[GAMEOVERTXT].visible)

    def test_add_and_remove_text(self):
        tg = TextGroup()
        # addText returns new id and stores Text
        new_id = tg.addText("X", RED, 1, 2, 8)
        self.assertIn(new_id, tg.alltext)
        tg.removeText(new_id)
        self.assertNotIn(new_id, tg.alltext)

    def test_update_removes_destroyed_texts(self):
        tg = TextGroup()
        # add a short-lived text
        nid = tg.addText("short", RED, 0, 0, 8, time=0.01)
        # call update with a dt that will destroy it
        tg.update(0.02)
        self.assertNotIn(nid, tg.alltext)

    def test_updateScore_updateLevel_updateText(self):
        tg = TextGroup()
        tg.updateScore(123)
        self.assertEqual(tg.alltext[SCORETXT].text, str(123).zfill(8))
        tg.updateLevel(4)
        self.assertEqual(tg.alltext[LEVELTXT].text, str(5).zfill(3))
        # updateText with non-existent id should not raise
        tg.updateText(9999, "nope")  # nothing to assert, just ensure no exception

    def test_render_calls_render_on_all_texts(self):
        tg = TextGroup()
        screen = MagicMock()
        # Replace each Text.render with a MagicMock to count calls
        for tkey in list(tg.alltext.keys()):
            tg.alltext[tkey].render = MagicMock()
        tg.render(screen)
        for tkey in list(tg.alltext.keys()):
            tg.alltext[tkey].render.assert_called_once_with(screen)

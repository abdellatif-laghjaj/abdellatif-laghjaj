from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

import make_fight as fight


class FightTests(unittest.TestCase):
    def test_personalized_copy_fits_canvas(self):
        for word in fight.ALL_WORDS:
            with self.subTest(word=word.text):
                self.assertGreaterEqual(word.x, 0)
                self.assertLessEqual(word.x + word.w, fight.W)
        self.assertLessEqual(fight.FONT.font_variant(size=32).getlength(fight.H1_TEXT), fight.W)

    def test_both_generated_themes_keep_valid_animation(self):
        for theme in ("light", "dark"):
            with self.subTest(theme=theme):
                root = ET.parse(Path(__file__).with_name(f"fight-{theme}.svg")).getroot()
                text = " ".join(root.itertext())
                self.assertIn("Hi, I'm Abdellatif", text)
                self.assertIn("Bug.", text)
                for old_identity in ("Jeremy", "UWaterloo", "Ted."):
                    self.assertNotIn(old_identity, text)
                animations = [el for el in root.iter() if "keyTimes" in el.attrib]
                self.assertTrue(animations)
                for animation in animations:
                    times = [float(t) for t in animation.attrib["keyTimes"].split(";")]
                    self.assertEqual(times[0], 0)
                    self.assertEqual(times[-1], 1)
                    self.assertTrue(all(a < b for a, b in zip(times, times[1:])))
                    self.assertEqual(len(times), len(animation.attrib["values"].split(";")))
                    if "keySplines" in animation.attrib:
                        self.assertEqual(len(times) - 1, len(animation.attrib["keySplines"].split(";")))


if __name__ == "__main__":
    unittest.main()

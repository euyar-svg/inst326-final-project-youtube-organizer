import unittest

class TestSanitizer(unittest.TestCase):

    def test_remove_timestamps(self):
        text = "[00:00] Hello world"
        result = sanitize_transcript(text)
        self.assertEqual(result, "Hello world")


class TestCategorizer(unittest.TestCase):

    def test_programming_category(self):
        text = "Subscribe to my Minecraft channel"
        result = categorize_video(text) #AI should return proper category
        self.assertEqual(result, "Gaming")


if __name__ == "__main__":
    unittest.main()
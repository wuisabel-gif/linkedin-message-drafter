import unittest

from linkedin_message_drafter.drafts import Prospect, build_draft


class DraftTests(unittest.TestCase):
    def test_builds_personalized_draft(self):
        draft = build_draft(Prospect.from_dict({
            "name": "Sam Lee", "context": "a post about hiring", "goal": "I would like to connect",
            "company": "Acme", "role": "talent strategy",
        }))
        self.assertIn("Hi Sam", draft)
        self.assertIn("Acme", draft)
        self.assertIn("I would like to connect", draft)

    def test_capitalizes_goal_without_lowercasing_acronyms(self):
        draft = build_draft(Prospect.from_dict({
            "name": "Kim", "context": "your ML pipeline post", "goal": "want to swap notes",
        }))
        self.assertIn("Your ML pipeline post", draft)  # not "Your ml pipeline post"
        self.assertIn("Want to swap notes.", draft)     # goal sentence capitalized

    def test_requires_core_fields(self):
        with self.assertRaises(ValueError):
            Prospect.from_dict({"name": "Sam"})

    def test_short_note_fits_connection_limit(self):
        from linkedin_message_drafter.drafts import NOTE_LIMIT, fit
        note = build_draft(Prospect.from_dict({
            "name": "Sam Lee",
            "context": "your very long post about " + "scaling systems " * 30,
            "goal": "would love to connect",
        }), short=True)
        self.assertLessEqual(len(note), NOTE_LIMIT)
        self.assertIn("Hi Sam", note)
        # fit() trims at a word boundary, never mid-word
        self.assertLessEqual(len(fit("word " * 100)), NOTE_LIMIT)


if __name__ == "__main__":
    unittest.main()

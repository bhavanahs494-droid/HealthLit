import os, unittest
from unittest.mock import patch
from healthlit import assistant, guardrails

class Tests(unittest.TestCase):
    def setUp(self):
        os.environ["HEALTHLIT_PROVIDER"] = "offline"
    def test_answer_has_source(self):
        r = assistant.ask("What are TB symptoms?")
        self.assertEqual(r["sources"][0]["id"], "tb-1")
    def test_safety(self):
        self.assertEqual(guardrails.check("I want to die"), "crisis")
        self.assertEqual(guardrails.check("I have chest pain"), "emergency")
        self.assertEqual(guardrails.check("What dose of insulin?"), "refused")
    def test_paraphrased_emergencies(self):
        for q in ["He is not breathing", "My mother is having fits", "Face drooping and slurred speech"]:
            self.assertEqual(guardrails.check(q), "emergency", q)
        self.assertEqual(guardrails.check("I am going to kill my self"), "crisis")
    def test_uncovered_topic(self):
        self.assertEqual(assistant.ask("What are the symptoms of malaria?")["status"], "no_information")
    def test_redaction(self):
        s = guardrails.redact("a@b.com 9876543210 1234 5678 9012")
        self.assertEqual(s, "[email] [phone] [id-number]")
    def test_good_llm_answer(self):
        os.environ["HEALTHLIT_PROVIDER"] = "ollama"
        with patch("healthlit.llm.generate", return_value="TB can be cured. [tb-2]"):
            self.assertEqual(assistant.ask("Can tuberculosis be cured?")["mode"], "ollama")
    def test_fake_citation_rejected(self):
        os.environ["HEALTHLIT_PROVIDER"] = "ollama"
        with patch("healthlit.llm.generate", return_value="Made up. [fake-9]"):
            self.assertIn("citation check", assistant.ask("What are TB symptoms?")["mode"])
    def test_llm_failure_falls_back(self):
        os.environ["HEALTHLIT_PROVIDER"] = "ollama"
        with patch("healthlit.llm.generate", side_effect=OSError):
            self.assertIn("fallback", assistant.ask("What are TB symptoms?")["mode"])
    def test_simplify(self):
        self.assertIn("(fever)", assistant.simplify("Patient has pyrexia.")["answer"])

if __name__ == "__main__":
    unittest.main()

"""The 20-question review sample quotes gold passages from the node files."""

from graphrag_poc.eval.check import load_node_text, load_questions
from graphrag_poc.eval.review import SAMPLE_IDS, SAMPLE_PATH, render_sample


def test_sample_covers_twenty_questions_and_quotes_each_gold_passage() -> None:
    assert len(SAMPLE_IDS) == len(set(SAMPLE_IDS)) == 20
    questions = {str(record["id"]): record for record in load_questions()}
    texts = load_node_text()
    rendered = render_sample(list(questions.values()), texts)
    types: set[str] = set()
    languages: set[str] = set()
    for qid in SAMPLE_IDS:
        record = questions[qid]
        assert qid in rendered
        slice_ = record["slice"]
        assert isinstance(slice_, dict)
        types.add(str(slice_["question_type"]))
        languages.add(str(slice_["language"]))
        gold = record["gold"]
        assert isinstance(gold, dict)
        node_ids = gold["node_ids"]
        assert isinstance(node_ids, list)
        for node_id in node_ids:
            assert texts[str(node_id)] in rendered
        if record["expected_action"] == "refuse":
            assert node_ids == []
            assert "Gold passages: none." in rendered
    assert languages == {"en", "ja"}
    for name in (
        "lookup",
        "procedure",
        "applicability",
        "relational",
        "multi_hop",
        "troubleshooting",
        "follow_up",
        "unanswerable",
    ):
        assert name in types
    assert SAMPLE_PATH.read_text(encoding="utf-8") == rendered

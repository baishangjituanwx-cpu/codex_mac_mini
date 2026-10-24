from social_publisher.platforms.base import (
    detect_text_mismatch,
    evaluate_takeover_field,
    pick_takeover_candidate,
    TakeoverCandidate,
    text_matches_target,
)


class FakePage:
    def __init__(self, url: str):
        self.url = url


def test_text_matches_target_allows_subset() -> None:
    assert text_matches_target("这是当前标题", "这是当前标题，后面还有补充")
    assert text_matches_target("这是一小段正文", "开头。这是一小段正文 结尾。")


def test_detect_text_mismatch_returns_note_for_different_content() -> None:
    note = detect_text_mismatch("title", "旧草稿标题", "这次新的标题")
    assert note == "existing_title: 旧草稿标题"


def test_detect_text_mismatch_ignores_empty_current_value() -> None:
    assert detect_text_mismatch("body", "", "正文内容") is None


def test_evaluate_takeover_field_scores_matching_content() -> None:
    score, matched_field, stop_reason = evaluate_takeover_field(
        "description",
        "这是这次要发的描述",
        "开头 这是这次要发的描述 结尾",
    )

    assert score == 2
    assert matched_field == "description"
    assert stop_reason is None


def test_pick_takeover_candidate_prefers_viable_high_score_page() -> None:
    winning = TakeoverCandidate(
        page=FakePage("https://example.com/matching"),
        score=4,
        matched_fields=["title", "body"],
    )
    stopped = TakeoverCandidate(
        page=FakePage("https://example.com/old-draft"),
        score=9,
        stop_reasons=["existing_title: 旧草稿标题"],
    )

    selected = pick_takeover_candidate([stopped, winning])

    assert selected is winning

from social_publisher.platforms.base import detect_text_mismatch, text_matches_target


def test_text_matches_target_allows_subset() -> None:
    assert text_matches_target("这是当前标题", "这是当前标题，后面还有补充")
    assert text_matches_target("这是一小段正文", "开头。这是一小段正文 结尾。")


def test_detect_text_mismatch_returns_note_for_different_content() -> None:
    note = detect_text_mismatch("title", "旧草稿标题", "这次新的标题")
    assert note == "existing_title: 旧草稿标题"


def test_detect_text_mismatch_ignores_empty_current_value() -> None:
    assert detect_text_mismatch("body", "", "正文内容") is None

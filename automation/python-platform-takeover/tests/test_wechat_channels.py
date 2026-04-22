from social_publisher.platforms.wechat_channels import (
    management_entry_component_from_mapping,
    management_entry_is_newer,
    management_entry_is_self_visible,
    ManagementEntryComponent,
    ManagementListBaseline,
    WeChatChannelsPublisher,
    match_management_entry_text,
    resolve_management_status,
    should_stop_existing_video_candidate,
    text_matches_exactly,
)


def test_wechat_channels_management_url_uses_shell_page() -> None:
    publisher = WeChatChannelsPublisher()

    assert publisher.metadata.management_urls == [
        "https://channels.weixin.qq.com/platform/post/list"
    ]


def test_text_matches_exactly_requires_full_match() -> None:
    assert text_matches_exactly("先替平台执行", "先替平台执行") is True
    assert text_matches_exactly("先替平台执行", "先替平台执行，后面还有补充") is False


def test_existing_video_candidate_without_matching_fields_must_stop() -> None:
    assert should_stop_existing_video_candidate(
        has_existing_video=True,
        matched_fields=[],
    ) is True
    assert should_stop_existing_video_candidate(
        has_existing_video=True,
        matched_fields=["description"],
    ) is True
    assert should_stop_existing_video_candidate(
        has_existing_video=True,
        matched_fields=["description", "short_title"],
    ) is False


def test_match_management_entry_text_requires_same_row_to_have_status_and_marker() -> None:
    matched = match_management_entry_text(
        "先替平台执行 很多团队写完内容以后，以为工作已经结束了 审核中",
        statuses=["已发表", "审核中", "处理中"],
        required_markers=["很多团队写完内容以后"],
        optional_markers=["先替平台执行"],
    )

    assert matched is not None
    assert matched.status == "审核中"
    assert "很多团队写完内容以后" in matched.matched_markers
    assert "先替平台执行" in matched.matched_markers


def test_match_management_entry_text_rejects_entry_without_required_marker() -> None:
    matched = match_management_entry_text(
        "别的旧视频文案 审核中",
        statuses=["已发表", "审核中", "处理中"],
        required_markers=["很多团队写完内容以后"],
        optional_markers=["先替平台执行"],
    )

    assert matched is None


def test_management_entry_component_from_mapping_normalizes_platform_payload() -> None:
    component = management_entry_component_from_mapping(
        {
            "object_id": "export/abc",
            "create_time": 1776836814,
            "visible_type": 3,
            "short_title": " 先替平台执行 ",
            "description": " 很多团队写完内容以后，以为工作已经结束了。 ",
        }
    )

    assert component == ManagementEntryComponent(
        object_id="export/abc",
        create_time=1776836814,
        visible_type=3,
        short_title="先替平台执行",
        description="很多团队写完内容以后，以为工作已经结束了。",
    )


def test_management_entry_is_self_visible_prefers_component_visible_type() -> None:
    component = ManagementEntryComponent(visible_type=3)

    assert management_entry_is_self_visible("审核中", component) is True
    assert management_entry_is_self_visible("仅自己可见", None) is True
    assert management_entry_is_self_visible("审核中", ManagementEntryComponent(visible_type=1)) is False


def test_management_entry_is_newer_requires_new_top_entry_or_more_rows() -> None:
    baseline = ManagementListBaseline(
        selector=".post-feed-item",
        count=15,
        top_object_id="export/old",
        top_create_time=1776836814,
    )

    assert management_entry_is_newer(
        ManagementEntryComponent(
            object_id="export/new",
            create_time=1776840000,
        ),
        baseline=baseline,
        index=0,
        current_count=15,
    ) is True
    assert management_entry_is_newer(
        ManagementEntryComponent(
            object_id="export/old",
            create_time=1776836814,
        ),
        baseline=baseline,
        index=0,
        current_count=16,
    ) is True
    assert management_entry_is_newer(
        ManagementEntryComponent(
            object_id="export/old",
            create_time=1776836814,
        ),
        baseline=baseline,
        index=0,
        current_count=15,
    ) is False
    assert management_entry_is_newer(
        ManagementEntryComponent(
            object_id="export/newer-but-not-top",
            create_time=1776840001,
        ),
        baseline=baseline,
        index=1,
        current_count=15,
    ) is False


def test_resolve_management_status_reads_known_status_markers() -> None:
    assert resolve_management_status("先替平台执行 审核中", ["已发表", "审核中", "处理中"]) == "审核中"
    assert resolve_management_status("没有状态", ["已发表", "审核中", "处理中"]) is None

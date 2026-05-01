# Seedance Post-Generation Cover Package

This reference defines the fixed cover workflow that must follow video generation when the output will be published across multiple platforms.

## Delivery Rule

For each finished video, always deliver exactly two cover files:

- `cover-vertical-3x4.png`
- `cover-horizontal-4x3.png`

Specs:

- Vertical: `1080x1440`
- Horizontal: `1440x1080`
- Format: `PNG`

## Source Frame Rule

Do not rely on AI-generated Chinese text inside the original video frame and do not use the original actor reference image as the cover background.

Use one clear still from the generated final video:

- face sharp
- eyes open
- mouth shape natural
- no motion blur
- no subtitle bar baked into the chosen crop
- if the strongest face frame still carries burned-in subtitle residue, crop out the lower subtitle region first and build the cover from the cleaned crop rather than using the dirty frame directly

## Subject Rule

- The main subject must be `大陈`
- Use a real office environment
- Avoid stage, livestream, fake-backdrop, or over-designed poster feel
- Prefer half-body or close-up
- Keep the face as the core visual anchor

## Composition Rule

- Put the face and upper body in the middle-to-upper region
- Reserve roughly the bottom `30%` for text treatment
- Do not let key facial features fall into the title band zone
- Keep the frame clean rather than busy

## Layout Rule

For 大陈 / AI员工 Seedance content packages, the layout must follow the migration pack permanently:

- canonical source: `smb://BSJT168._smb._tcp.local/BSJT 共享给我/AI专用/[Codex]Mac部署/视频制作/大陈AI短视频生产迁移包-20260428`
- canonical script when mounted: `project/scripts/generate_simple_video_covers.py`
- lower-middle rounded dark translucent information card, not a plain full-width strip
- main title centered in gold/white dimensional art type with dark stroke
- subtitle under the main title, one line only
- no platform auto cover, AI recommended cover, generic poster template, or unstyled raw frame

Stable visual priority:

- `大陈真实脸 + AI员工大字标题 + 老板收益/动作承诺`

Not:

- decorative sticker pile
- explosion text
- cluttered icon overlays
- video subtitle strips reused as cover title

## Copy Rule

Main title:

- `6-10` Chinese characters
- direct
- readable at thumbnail size
- should usually include `AI员工` or a very close replacement cue

Subtitle:

- `4-8` Chinese characters
- one line only
- complements the main title instead of repeating it

Preferred copy direction:

- result sentence
- replacement sentence
- boss-benefit sentence

Avoid:

- long explanatory sentences
- abstract product language like `智能营销` or `数字化升级`
- pure function labels with no owner benefit

## Recommended Title Patterns

Platform-execution angle:

- `AI员工上岗了` + `自动跑平台`
- `AI员工开始跑平台` + `不用自己硬扛`

Boss-pain angle:

- `AI员工替你盯运营` + `老板先下班`
- `AI员工帮你接手内容` + `省下运营时间`

## Do Not Do This

- do not use more than one main-title line
- do not make the office background louder than the subject
- do not use a blurry or distorted face
- do not reuse subtitle strips from the video as the final cover title
- do not turn the cover into a generic tool poster

## Practical Workflow

1. Finish the Seedance video.
2. Download the final `mp4`.
3. Review several clear candidate frames.
4. Pick the strongest still with clean facial expression.
5. Export both `3:4` and `4:3` crops.
6. Add the fixed lower-third title treatment.
7. Save both files as PNG.
8. Verify that every platform publish package explicitly points to these cover files.
9. Only then hand off to publishing.

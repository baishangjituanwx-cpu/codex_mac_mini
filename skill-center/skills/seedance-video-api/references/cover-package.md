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

Use a stable, repeatable layout:

- dark semi-transparent bottom information band
- main title centered in large white type
- subtitle under the main title in a smaller yellow-gold tone
- optional small orange rounded label at lower left if a version tag is needed

Stable visual priority:

- `真人脸 + 大字标题`

Not:

- decorative sticker pile
- explosion text
- cluttered icon overlays

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
8. Only then hand off to publishing.

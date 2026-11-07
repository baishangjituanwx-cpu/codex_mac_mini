#!/usr/bin/env ruby
require "yaml"

skill_dir = File.expand_path("..", __dir__)
skill_md = File.join(skill_dir, "SKILL.md")
openai_yaml = File.join(skill_dir, "agents", "openai.yaml")
references_dir = File.join(skill_dir, "references")

required_refs = [
  "platform-notes.md",
  "cover-playbook.md",
  "cover-template-matrix.md",
  "cover-prompt-kit.md",
]

def fail!(msg)
  warn("FAIL: #{msg}")
  exit(1)
end

def assert(condition, msg)
  fail!(msg) unless condition
end

skill_text = File.read(skill_md)
frontmatter = skill_text[/\A---\n(.*?)\n---/m, 1]
assert(frontmatter, "SKILL.md frontmatter missing")
skill_data = YAML.safe_load(frontmatter)
assert(skill_data["name"] == "platform-cover-ops", "unexpected skill name")
assert(skill_data["description"].to_s.include?("cover workflows"), "description missing cover workflow wording")

yaml_data = YAML.load_file(openai_yaml)
assert(yaml_data.dig("interface", "display_name"), "openai.yaml missing display_name")
assert(yaml_data.dig("interface", "short_description"), "openai.yaml missing short_description")

required_refs.each do |name|
  path = File.join(references_dir, name)
  assert(File.exist?(path), "missing reference file #{name}")
  assert(skill_text.include?(name), "SKILL.md does not reference #{name}")
end

playbook = File.read(File.join(references_dir, "cover-playbook.md"))
%w[微博 百家号 知乎 今日头条 / 头条号 抖音 小红书 微信视频号 快手].each do |platform|
  assert(playbook.include?(platform), "cover-playbook missing platform #{platform}")
end
%w[封面改法 推荐文案 裁切安全区 实际执行顺序].each do |section|
  count = playbook.scan(section).length
  assert(count >= 8, "cover-playbook expected at least 8 '#{section}' sections, got #{count}")
end

matrix = File.read(File.join(references_dir, "cover-template-matrix.md"))
%w[AI\ 产品 营销内容 人物口播 产品演示].each do |section|
  count = matrix.scan(section).length
  assert(count >= 9, "cover-template-matrix expected at least 9 '#{section}' sections, got #{count}")
end
%w[微博 百家号 知乎 今日头条 / 头条号 抖音 小红书 微信视频号 快手].each do |platform|
  assert(matrix.include?(platform), "cover-template-matrix missing platform #{platform}")
end

prompt_kit = File.read(File.join(references_dir, "cover-prompt-kit.md"))
[
  "通用主 Prompt",
  "通用负面 Prompt",
  "AI 产品",
  "营销内容",
  "人物口播",
  "产品演示",
  "四套常用字位模板",
].each do |needle|
  assert(prompt_kit.include?(needle), "cover-prompt-kit missing '#{needle}'")
end

puts "OK: platform-cover-ops structure validated"

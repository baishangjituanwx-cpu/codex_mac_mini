#!/usr/bin/env ruby
require "yaml"

skill_dir = File.expand_path("..", __dir__)
skill_md = File.join(skill_dir, "SKILL.md")
yaml_path = File.join(skill_dir, "agents", "openai.yaml")
refs = File.join(skill_dir, "references")

def fail!(msg)
  warn("FAIL: #{msg}")
  exit(1)
end

text = File.read(skill_md)
frontmatter = text[/\A---\n(.*?)\n---/m, 1] or fail!("missing frontmatter")
data = YAML.safe_load(frontmatter)
fail!("wrong skill name") unless data["name"] == "dachen-founder-flywheel"
fail!("description missing founder-IP wording") unless data["description"].to_s.include?("founder-IP")
yaml = YAML.load_file(yaml_path)
fail!("missing interface") unless yaml["interface"].is_a?(Hash)

required_refs = [
  "flywheel-operating-system.md",
  "daily-automation-spec.md",
  "weekly-content-calendar.md",
  "review-scorecard.md",
]
required_refs.each do |name|
  path = File.join(refs, name)
  fail!("missing #{name}") unless File.exist?(path)
  fail!("SKILL.md missing reference #{name}") unless text.include?(name)
end

puts "OK: dachen-founder-flywheel structure validated"

#!/usr/bin/env ruby
require "json"

abort("usage: preflight_cover_briefs.rb <briefs.json>") unless ARGV.length == 1

path = ARGV[0]
data = JSON.parse(File.read(path))

MAX_COPY = {
  "weibo" => 10,
  "baijiahao" => 14,
  "zhihu" => 12,
  "toutiao" => 14,
  "douyin" => 10,
  "xiaohongshu" => 14,
  "wechat_channels" => 12,
  "kuaishou" => 12,
}

def warn_line(lines, platform, msg)
  lines << "WARN #{platform}: #{msg}"
end

def ok_line(lines, platform, msg)
  lines << "OK   #{platform}: #{msg}"
end

lines = []
failures = 0

unless data.is_a?(Array) && data.length == 8
  abort("FAIL: expected 8 platform briefs, got #{data.is_a?(Array) ? data.length : data.class}")
end

data.each do |item|
  platform = item["platform"] || "unknown"
  required = %w[
    platform
    content_type
    current_content
    primary_copy
    alternate_copies
    layout_template
    subject
    safe_zone
    execution_steps
  ]
  missing = required.reject { |k| item.key?(k) }
  if missing.any?
    warn_line(lines, platform, "missing fields: #{missing.join(', ')}")
    failures += 1
    next
  end

  max_len = MAX_COPY.fetch(platform, 14)
  copy_len = item["primary_copy"].to_s.length
  if copy_len > max_len
    warn_line(lines, platform, "primary_copy too long #{copy_len}/#{max_len}")
    failures += 1
  else
    ok_line(lines, platform, "primary_copy length #{copy_len}/#{max_len}")
  end

  alts = item["alternate_copies"]
  if !alts.is_a?(Array) || alts.length < 2
    warn_line(lines, platform, "need at least 2 alternate copies")
    failures += 1
  else
    ok_line(lines, platform, "alternate copies #{alts.length}")
  end

  safe = item["safe_zone"]
  %w[left right top bottom center].each do |key|
    unless safe.key?(key)
      warn_line(lines, platform, "safe_zone missing #{key}")
      failures += 1
    end
  end
  if safe["center"].to_i < 60
    warn_line(lines, platform, "safe center too small #{safe['center']}")
    failures += 1
  else
    ok_line(lines, platform, "safe center #{safe['center']}")
  end

  steps = item["execution_steps"]
  if !steps.is_a?(Array) || steps.length < 4
    warn_line(lines, platform, "execution steps too short")
    failures += 1
  else
    ok_line(lines, platform, "execution steps #{steps.length}")
  end
end

puts lines.join("\n")
puts "---"
if failures.zero?
  puts "PASS: cover briefs preflight passed"
  exit(0)
else
  puts "FAIL: cover briefs preflight found #{failures} issue(s)"
  exit(1)
end

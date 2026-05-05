# frozen_string_literal: true
# One-off: regenerate docs HTML + feed snippet from _post when full jekyll build fails (sass/OSX).
require "bundler/setup"
require "cgi"
require "json"
require "kramdown"

blog = File.expand_path("..", __dir__)
Dir.chdir(blog)

md_path = "_posts/business/2026-05-03-创新药投资-在迷雾中寻找确定性.md"
html_path = "docs/商业/2026/05/03/创新药投资-在迷雾中寻找确定性.html"
feed_path = "docs/feed.xml"

raw = File.read(md_path, encoding: "UTF-8")
body_md = raw.sub(/\A---.*?---\s*\n/m, "")
new_body_html = Kramdown::Document.new(body_md, input: "GFM").to_html.strip + "\n"

desc_plain = new_body_html.gsub(/<[^>]+>/, " ").gsub(/\s+/, " ").strip
desc_esc = CGI.escapeHTML(desc_plain)

html = File.read(html_path, encoding: "UTF-8")
unless html.sub!(/(<div class="asset-body">\n)(.*)(\n    <\/div>\n  <\/div>\n\n  <div class="asset-footer">)/m, "\\1#{new_body_html}\\3")
  warn "asset-body replace failed"
  exit 1
end

html.sub!(/<meta name="description" content="[^"]*"/, %(<meta name="description" content="#{desc_esc}"))
html.sub!(/(<!-- Begin Jekyll SEO tag v2\.8\.0 -->[\s\S]*?<meta name="description" content=")[^"]*(")/m, "\\1#{desc_esc}\\2")
html.sub!(/<meta property="og:description" content="[^"]*"/, %(<meta property="og:description" content="#{desc_esc}"))

html.sub!(/<meta property="article:published_time" content="[^"]+"/,
          %(<meta property="article:published_time" content="2026-05-05T12:00:00+08:00"))

ld_start = html.index('<script type="application/ld+json">')
if ld_start
  brace_i = html.index("{", ld_start)
  depth = 0
  j_end = nil
  (brace_i..html.length - 1).each do |k|
    case html[k]
    when "{"
      depth += 1
    when "}"
      depth -= 1
      if depth.zero?
        j_end = k
        break
      end
    end
  end
  if j_end
    j = JSON.parse(html[brace_i..j_end])
    j["description"] = desc_plain
    j["datePublished"] = "2026-05-05T12:00:00+08:00"
    j["dateModified"] = "2026-05-05T12:00:00+08:00"
    html[ld_start..html.index("</script>", ld_start) + "</script>".length - 1] =
      %(<script type="application/ld+json">\n#{JSON.generate(j)}\n</script>)
  end
end

html.sub!(/<abbr class="published" title="[^"]+"/, %(<abbr class="published" title="2026-05-05T12:00:00+08:00"))
html.sub!(/(\<abbr class="published" title="2026-05-05T12:00:00\+08:00"\>\s*\n\s*)\d{4}年\d{2}月\d{2}日/) do
  "#{Regexp.last_match(1)}2026年05月05日"
end

html.sub!(%r{<li>发表日期：\d{4}年\d{2}月\d{2}日</li>}, "<li>发表日期：2026年05月05日</li>")

File.write(html_path, html)

feed = File.read(feed_path, encoding: "UTF-8")
escaped_body = CGI.escapeHTML(new_body_html)

feed.sub!(
  %r{(<title>创新药投资：在迷雾中寻找确定性</title>\s*<description>)([\s\S]*?)(</description>\s*<pubDate>)([^<]+)(</pubDate>)},
  "\\1#{escaped_body}\\3Tue, 05 May 2026 12:00:00 +0800\\5"
)

now_rfc = Time.now.getlocal("+08:00").strftime("%a, %d %b %Y %H:%M:%S %z")
feed.sub!(%r{<pubDate>[^<]+</pubDate>\n\s*<lastBuildDate>[^<]+</lastBuildDate>},
          "<pubDate>#{now_rfc}</pubDate>\n    <lastBuildDate>#{now_rfc}</lastBuildDate>")

File.write(feed_path, feed)

puts "OK: #{html_path}, #{feed_path}"

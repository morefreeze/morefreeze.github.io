module Jekyll
  module LanguageSwitcher
    def current_page_language(page)
      return 'cn' unless page.respond_to?(:basename)
      basename = page.basename.to_s
      basename.include?('_en') ? 'en' : 'cn'
    end

    def has_english_version(page)
      return false unless page.respond_to?(:basename)
      basename = page.basename.to_s
      !basename.include?('_en')
    end

    def has_chinese_version(page)
      return false unless page.respond_to?(:basename)
      basename = page.basename.to_s
      basename.include?('_en')
    end
  end
end

Liquid::Template.register_filter(Jekyll::LanguageSwitcher)
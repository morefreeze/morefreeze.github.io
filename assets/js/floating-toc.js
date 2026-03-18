(function() {
  'use strict';

  const TOC_CONFIG = {
    hideDelay: 300,
    tocSelector: '.floating-toc',
    hintSelector: '.floating-toc-hint'
  };

  class FloatingTOC {
    constructor() {
      this.toc = null;
      this.hint = null;
      this.tocList = null;
      this.isVisible = false;
      this.hideTimeout = null;
      this.isScrolling = false;
      this.headings = [];
      this.activeHeadingId = null;

      this.init();
    }

    init() {
      if (this.isHomePage()) return;
      if (!this.hasFloatTOCTag()) return;
      this.createTOC();
      if (!this.tocList) return;

      this.bindEvents();
      this.buildIntersectionObserver();
      this.updateActiveHeading();
    }

    isHomePage() {
      const path = window.location.pathname;
      return path === '/' || path === '/index.html' || path.endsWith('/');
    }

    hasFloatTOCTag() {
      const content = document.querySelector('.post-content, .content, article');
      if (!content) return false;
      return content.querySelectorAll('h1, h2, h3, h4, h5, h6').length >= 2;
    }

    createTOC() {
      const headings = this.extractHeadings();
      if (headings.length === 0) return;

      this.headings = headings;
      const html = this.generateTOCHTML(headings);

      const tocWrapper = document.createElement('div');
      tocWrapper.innerHTML = `
        <div class="floating-toc-hint" title="展开目录">
          <span class="floating-toc-hint-icon">≡</span>
        </div>
        <div class="floating-toc">
          <div class="floating-toc-header">
            <span class="floating-toc-title">目录</span>
            <button class="floating-toc-close" aria-label="关闭目录">&times;</button>
          </div>
          <div class="floating-toc-content">
            <ul class="floating-toc-list">${html}</ul>
          </div>
        </div>
      `;

      document.body.appendChild(tocWrapper);
      this.toc = document.querySelector(TOC_CONFIG.tocSelector);
      this.hint = document.querySelector(TOC_CONFIG.hintSelector);
      this.tocList = this.toc.querySelector('.floating-toc-list');
    }

    extractHeadings() {
      const content = document.querySelector('.post-content, .content, article');
      if (!content) return [];

      const elements = content.querySelectorAll('h1, h2, h3, h4, h5, h6');
      const headings = [];
      elements.forEach((el, index) => {
        if (!el.id) el.id = 'heading-' + index;
        headings.push({
          id: el.id,
          text: el.textContent.trim(),
          level: parseInt(el.tagName.charAt(1))
        });
      });
      return headings;
    }

    generateTOCHTML(headings) {
      return headings.map(h => {
        const levelClass = `toc-h${h.level}`;
        return `<li><a href="#${h.id}" class="${levelClass}" data-id="${h.id}">${this.escapeHTML(h.text)}</a></li>`;
      }).join('');
    }

    escapeHTML(str) {
      const div = document.createElement('div');
      div.textContent = str;
      return div.innerHTML;
    }

    bindEvents() {
      // 悬停 hint tab 展开
      this.hint.addEventListener('mouseenter', () => this.showTOC());

      // TOC 鼠标进入，取消延迟收起
      this.toc.addEventListener('mouseenter', () => this.cancelHide());

      // TOC 鼠标离开，延迟收起
      this.toc.addEventListener('mouseleave', () => this.scheduleHide());

      // × 按钮点击关闭
      this.toc.querySelector('.floating-toc-close').addEventListener('click', () => this.hideTOC());

      // TOC 列表点击跳转
      this.tocList.addEventListener('click', (e) => {
        e.preventDefault();
        const link = e.target.closest('a');
        if (link) {
          const target = document.getElementById(link.dataset.id);
          if (target) {
            const offsetPosition = target.getBoundingClientRect().top + window.pageYOffset - 80;
            window.scrollTo({ top: offsetPosition, behavior: 'smooth' });
            this.hideTOC();
          }
        }
      });

      window.addEventListener('scroll', () => this.handleScroll());
    }

    showTOC() {
      this.cancelHide();
      this.toc.classList.add('visible');
      this.hint.classList.add('hidden');
      this.isVisible = true;
    }

    hideTOC() {
      this.toc.classList.remove('visible');
      this.hint.classList.remove('hidden');
      this.isVisible = false;
    }

    scheduleHide() {
      this.cancelHide();
      this.hideTimeout = setTimeout(() => this.hideTOC(), TOC_CONFIG.hideDelay);
    }

    cancelHide() {
      if (this.hideTimeout) {
        clearTimeout(this.hideTimeout);
        this.hideTimeout = null;
      }
    }

    handleScroll() {
      if (!this.isScrolling) {
        this.isScrolling = true;
        requestAnimationFrame(() => {
          this.updateActiveHeading();
          this.isScrolling = false;
        });
      }
    }

    updateActiveHeading() {
      if (this.headings.length === 0) return;
      const scrollY = window.scrollY;
      let activeId = null;
      for (let i = this.headings.length - 1; i >= 0; i--) {
        const heading = document.getElementById(this.headings[i].id);
        if (heading && heading.offsetTop <= scrollY + 100) {
          activeId = this.headings[i].id;
          break;
        }
      }
      if (activeId !== this.activeHeadingId) {
        this.activeHeadingId = activeId;
        this.updateActiveLink();
      }
    }

    updateActiveLink() {
      this.tocList.querySelectorAll('a').forEach(link => {
        link.classList.toggle('active', link.dataset.id === this.activeHeadingId);
      });
    }

    buildIntersectionObserver() {
      if (!('IntersectionObserver' in window)) return;
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            this.activeHeadingId = entry.target.id;
            this.updateActiveLink();
          }
        });
      }, { rootMargin: '-80px 0px -80% 0px' });

      this.headings.forEach(h => {
        const el = document.getElementById(h.id);
        if (el) observer.observe(el);
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new FloatingTOC());
  } else {
    new FloatingTOC();
  }
})();

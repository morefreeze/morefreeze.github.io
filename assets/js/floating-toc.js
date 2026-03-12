(function() {
  'use strict';

  const TOC_CONFIG = {
    triggerZoneWidth: 0.1,
    hideDelay: 300,
    scrollThreshold: 50,
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
      this.lastScrollY = 0;
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

      const headings = content.querySelectorAll('h1, h2, h3, h4, h5, h6');
      return headings.length >= 2;
    }

    createTOC() {
      const headings = this.extractHeadings();
      if (headings.length === 0) return;

      this.headings = headings;
      const html = this.generateTOCHTML(headings);

      const tocWrapper = document.createElement('div');
      tocWrapper.innerHTML = `
        <div class="floating-toc-hint ${html ? 'has-toc' : ''}" title="显示目录"></div>
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
        if (!el.id) {
          el.id = 'heading-' + index;
        }
        headings.push({
          id: el.id,
          text: el.textContent.trim(),
          level: parseInt(el.tagName.charAt(1))
        });
      });

      return headings;
    }

    generateTOCHTML(headings) {
      if (headings.length === 0) return '';

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
      let mouseInTriggerZone = false;
      let mouseInTOC = false;

      // 获取导航栏高度（Bootstrap navbar 通常至少 50px 高）
      const getNavbarHeight = () => {
        const navbar = document.querySelector('.site-nav');
        if (navbar) {
          return navbar.offsetHeight;
        }
        return 50; // 默认 50px 作为导航栏高度
      };

      const navbarHeight = getNavbarHeight();

      document.addEventListener('mousemove', (e) => {
        const inTriggerZone = e.clientX <= window.innerWidth * TOC_CONFIG.triggerZoneWidth && e.clientY > navbarHeight;
        const inTOC = this.toc && this.toc.contains(e.relatedTarget);

        if (inTriggerZone && !mouseInTriggerZone) {
          mouseInTriggerZone = true;
          this.showTOC();
        } else if (!inTriggerZone && !inTOC && mouseInTriggerZone) {
          mouseInTriggerZone = false;
          this.scheduleHideTOC();
        }

        if (inTOC) mouseInTOC = true;
      });

      this.toc.addEventListener('mouseenter', () => {
        mouseInTOC = true;
        this.cancelHideTOC();
      });

      this.toc.addEventListener('mouseleave', () => {
        mouseInTOC = false;
        this.scheduleHideTOC();
      });

      const closeBtn = this.toc.querySelector('.floating-toc-close');
      closeBtn.addEventListener('click', () => this.hideTOC());

      this.tocList.addEventListener('click', (e) => {
        e.preventDefault();
        const link = e.target.closest('a');
        if (link) {
          const id = link.dataset.id;
          const target = document.getElementById(id);
          if (target) {
            const headerOffset = 80;
            const elementPosition = target.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

            window.scrollTo({
              top: offsetPosition,
              behavior: 'smooth'
            });

            this.hideTOC();
          }
        }
      });

      window.addEventListener('scroll', () => this.handleScroll());
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
      const links = this.tocList.querySelectorAll('a');
      links.forEach(link => {
        link.classList.remove('active');
        if (link.dataset.id === this.activeHeadingId) {
          link.classList.add('active');
        }
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

    showTOC() {
      if (this.hideTimeout) {
        clearTimeout(this.hideTimeout);
        this.hideTimeout = null;
      }
      this.toc.classList.add('visible');
      this.hint.classList.remove('visible');
      this.isVisible = true;
    }

    hideTOC() {
      this.toc.classList.remove('visible');
      this.hint.classList.add('visible');
      this.isVisible = false;
    }

    scheduleHideTOC() {
      this.cancelHideTOC();
      this.hideTimeout = setTimeout(() => {
        this.hideTOC();
      }, TOC_CONFIG.hideDelay);
    }

    cancelHideTOC() {
      if (this.hideTimeout) {
        clearTimeout(this.hideTimeout);
        this.hideTimeout = null;
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new FloatingTOC());
  } else {
    new FloatingTOC();
  }
})();

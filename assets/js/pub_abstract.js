// Progressive enhancement: on phones, long publication abstracts are clamped to
// a few lines with a "Show more" toggle so a card is not a wall of text.
// On wider screens, and if this script never runs, the full abstract shows.
(function () {
    var MOBILE = '(max-width: 767.98px)';
    var CLAMP_CLASS = 'is-collapsed';
    var EXPANDED_CLASS = 'is-expanded';

    function isMobile() {
        return window.matchMedia(MOBILE).matches;
    }

    function teardown(el) {
        el.classList.remove(CLAMP_CLASS, EXPANDED_CLASS);
        var next = el.nextElementSibling;
        if (next && next.classList.contains('pub-abstract-toggle')) {
            next.remove();
        }
    }

    function setup(el) {
        teardown(el);
        if (!isMobile()) {
            return;
        }
        // Hidden copies (the other responsive variant) have no layout box.
        el.classList.add(CLAMP_CLASS);
        if (el.clientHeight === 0 || el.scrollHeight - el.clientHeight < 4) {
            el.classList.remove(CLAMP_CLASS);
            return;
        }
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'pub-abstract-toggle';
        btn.textContent = 'Show more';
        btn.setAttribute('aria-expanded', 'false');
        btn.addEventListener('click', function () {
            var expanded = el.classList.toggle(EXPANDED_CLASS);
            el.classList.toggle(CLAMP_CLASS, !expanded);
            btn.textContent = expanded ? 'Show less' : 'Show more';
            btn.setAttribute('aria-expanded', expanded ? 'true' : 'false');
        });
        el.insertAdjacentElement('afterend', btn);
    }

    function run() {
        document.querySelectorAll('.pub-abstract').forEach(setup);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', run);
    } else {
        run();
    }

    var mq = window.matchMedia(MOBILE);
    if (mq.addEventListener) {
        mq.addEventListener('change', run);
    } else if (mq.addListener) {
        mq.addListener(run);
    }
})();

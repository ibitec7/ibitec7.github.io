// Theme control for the academic homepage.
//
// The chosen theme is stored in localStorage and applied by an inline script in
// <head> so the page never flashes the wrong theme. Until a reader picks one
// explicitly, the page follows the operating system setting.
(function () {
    var KEY = 'theme';
    var root = document.documentElement;

    function stored() {
        try { return localStorage.getItem(KEY); } catch (e) { return null; }
    }

    function prefersDark() {
        return !!(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
    }

    function effective() {
        return root.getAttribute('data-theme') || (prefersDark() ? 'dark' : 'light');
    }

    function apply(theme, persist) {
        root.setAttribute('data-theme', theme);
        if (persist) {
            try { localStorage.setItem(KEY, theme); } catch (e) { /* private mode */ }
        }
        var dark = theme === 'dark';
        var buttons = document.querySelectorAll('[data-theme-toggle]');
        for (var i = 0; i < buttons.length; i++) {
            buttons[i].setAttribute('aria-pressed', dark ? 'true' : 'false');
            buttons[i].setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
            buttons[i].setAttribute('title', dark ? 'Switch to light theme' : 'Switch to dark theme');
        }
    }

    // Exposed so any element can drive the theme: onclick="toggleTheme()".
    window.toggleTheme = function () {
        apply(effective() === 'dark' ? 'light' : 'dark', true);
    };

    function init() {
        var preferred = stored() || (prefersDark() ? 'dark' : 'light');
        apply(root.getAttribute('data-theme') || preferred, false);
        var buttons = document.querySelectorAll('[data-theme-toggle]');
        for (var i = 0; i < buttons.length; i++) {
            buttons[i].addEventListener('click', function (event) {
                event.preventDefault();
                window.toggleTheme();
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    if (window.matchMedia) {
        var query = window.matchMedia('(prefers-color-scheme: dark)');
        var onChange = function () {
            if (!stored()) { apply(prefersDark() ? 'dark' : 'light', false); }
        };
        if (query.addEventListener) { query.addEventListener('change', onChange); }
        else if (query.addListener) { query.addListener(onChange); }
    }
})();

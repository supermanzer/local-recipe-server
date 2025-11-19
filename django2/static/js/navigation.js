// Function to set active tab based on current route
function setActiveTab() {
    const path = window.location.pathname;
    const tabs = document.querySelector('md-tabs');
    if (!tabs) return;

    // Remove active from all tabs
    tabs.querySelectorAll('md-primary-tab').forEach(tab => {
        tab.removeAttribute('active');
    });

    // Set active based on current path
    if (path === '/') {
        tabs.querySelector('md-primary-tab[data-route="/"]').setAttribute('active', '');
    } else if (path.startsWith('/recipes')) {
        tabs.querySelector('md-primary-tab[data-route="/recipes"]').setAttribute('active', '');
    } else if (path.startsWith('/info')) {
        tabs.querySelector('md-primary-tab[data-route="/info"]').setAttribute('active', '');
    }
}

// Run when the page loads
document.addEventListener('DOMContentLoaded', setActiveTab);

// Handle navigation
document.querySelector('md-tabs')?.addEventListener('click', (e) => {
    const tab = e.target.closest('md-primary-tab');
    if (tab) {
        const route = tab.getAttribute('data-route');
        if (route) {
            window.location.href = route;
        }
    }
});
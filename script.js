// Asset download functionality
document.addEventListener('DOMContentLoaded', function() {
    const downloadButtons = document.querySelectorAll('.download-btn');
    
    downloadButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Prevent download if button is disabled
            if (this.disabled || this.classList.contains('disabled')) {
                e.preventDefault();
                return;
            }
            
            e.preventDefault();
            const assetName = this.getAttribute('data-asset');
            
            if (!assetName) {
                console.error('No asset name specified');
                return;
            }
            
            downloadAsset(assetName, this);
        });
    });
});

function downloadAsset(assetName, buttonElement) {
    // Show loading state
    const originalText = buttonElement.textContent;
    buttonElement.classList.add('loading');
    buttonElement.disabled = true;
    
    // Construct the asset path
    const assetPath = `assets/${assetName}`;
    
    // Create a temporary anchor element to trigger download
    const link = document.createElement('a');
    link.href = assetPath;
    link.download = assetName;
    link.style.display = 'none';
    
    // Append to body, click, and remove
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Simulate download delay (remove this if you want instant feedback)
    setTimeout(() => {
        // Remove loading state
        buttonElement.classList.remove('loading');
        buttonElement.disabled = false;
        
        // Show success feedback
        showDownloadFeedback(buttonElement, 'Downloaded!');
        
        // Reset button text after 2 seconds
        setTimeout(() => {
            buttonElement.textContent = originalText;
        }, 2000);
    }, 500);
}

function showDownloadFeedback(button, message) {
    const originalText = button.textContent;
    button.textContent = message;
    button.style.backgroundColor = '#10b981'; // Success green
    
    setTimeout(() => {
        button.style.backgroundColor = '';
    }, 2000);
}

// Copy color values to clipboard functionality
document.addEventListener('DOMContentLoaded', function() {
    const copyButtons = document.querySelectorAll('.copy-btn');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation(); // Prevent any parent click handlers
            const textToCopy = this.getAttribute('data-copy');
            
            if (!textToCopy) {
                console.error('No data-copy attribute found');
                return;
            }
            
            // Use the Clipboard API if available
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    showCopyButtonFeedback(this);
                }).catch(err => {
                    console.error('Failed to copy:', err);
                    fallbackCopyTextToClipboard(textToCopy, this);
                });
            } else {
                fallbackCopyTextToClipboard(textToCopy, this);
            }
        });
    });
    
    // Make entire color rows clickable
    const copyableRows = document.querySelectorAll('.copyable-row');
    
    copyableRows.forEach(row => {
        row.addEventListener('click', function(e) {
            // Don't trigger if clicking directly on the button (it has its own handler)
            if (e.target.closest('.copy-btn')) {
                return;
            }
            
            const textToCopy = this.getAttribute('data-copy');
            const button = this.querySelector('.copy-btn');
            
            if (!textToCopy) {
                console.error('No data-copy attribute found');
                return;
            }
            
            // Use the Clipboard API if available
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    if (button) {
                        showCopyButtonFeedback(button);
                    }
                }).catch(err => {
                    console.error('Failed to copy:', err);
                    fallbackCopyTextToClipboard(textToCopy, button || this);
                });
            } else {
                fallbackCopyTextToClipboard(textToCopy, button || this);
            }
        });
    });
});

function fallbackCopyTextToClipboard(text, element) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showCopyFeedback(element);
    } catch (err) {
        console.error('Fallback: Failed to copy', err);
    }
    
    document.body.removeChild(textArea);
}

function showCopyButtonFeedback(button) {
    button.classList.add('copied');
    
    // Change icon to Lucide checkmark temporarily
    const svg = button.querySelector('svg');
    if (svg) {
        const originalHTML = svg.innerHTML;
        svg.innerHTML = `
            <polyline points="20 6 9 17 4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        `;
        
        setTimeout(() => {
            svg.innerHTML = originalHTML;
            button.classList.remove('copied');
        }, 2000);
    } else {
        setTimeout(() => {
            button.classList.remove('copied');
        }, 2000);
    }
}

function showCopyFeedback(element) {
    const originalText = element.textContent;
    element.textContent = 'Copied!';
    element.style.color = '#10b981';
    
    setTimeout(() => {
        element.textContent = originalText;
        element.style.color = '';
    }, 2000);
}

// Horizontal Tab Navigation Functionality
document.addEventListener('DOMContentLoaded', function() {
    const tabNavigation = document.getElementById('tabNavigation');
    const tabLinks = document.querySelectorAll('.tab-link');
    const sections = document.querySelectorAll('.guideline-section');

    // Make navigation sticky on scroll
    function handleStickyNav() {
        const header = document.querySelector('header');
        const headerHeight = header ? header.offsetHeight : 0;
        const scrollPosition = window.pageYOffset;
        
        if (scrollPosition > headerHeight) {
            tabNavigation.classList.add('sticky');
        } else {
            tabNavigation.classList.remove('sticky');
        }
    }

    // Smooth scrolling for tab links
    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const header = document.querySelector('header');
                const tabNav = document.getElementById('tabNavigation');
                const headerHeight = header ? header.offsetHeight : 0;
                const tabNavHeight = tabNav ? tabNav.offsetHeight : 0;
                const offsetTop = targetSection.offsetTop - headerHeight - tabNavHeight - 20;
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Update active tab link based on scroll position
    function updateActiveTab() {
        const header = document.querySelector('header');
        const tabNav = document.getElementById('tabNavigation');
        const headerHeight = header ? header.offsetHeight : 0;
        const tabNavHeight = tabNav ? tabNav.offsetHeight : 0;
        const scrollPosition = window.pageYOffset + headerHeight + tabNavHeight + 100;
        
        // Check if we're near the bottom of the page
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
        const scrollBottom = window.pageYOffset + windowHeight;
        const isNearBottom = scrollBottom >= documentHeight - 50; // 50px threshold

        let current = '';

        // If near bottom, select the last section
        if (isNearBottom && sections.length > 0) {
            const lastSection = sections[sections.length - 1];
            current = lastSection.getAttribute('id');
        } else {
            // Otherwise, find the section based on scroll position
            sections.forEach(section => {
                const sectionTop = section.offsetTop;
                const sectionHeight = section.offsetHeight;
                
                if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                    current = section.getAttribute('id');
                }
            });
        }

        tabLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    }

    // Update on scroll
    window.addEventListener('scroll', function() {
        handleStickyNav();
        updateActiveTab();
    });
    
    // Initial updates
    handleStickyNav();
    updateActiveTab();
});

// Set current year in footer
document.addEventListener('DOMContentLoaded', function() {
    const yearElement = document.getElementById('currentYear');
    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }
});

// Smooth scrolling for intro list links
document.addEventListener('DOMContentLoaded', function() {
    const introLinks = document.querySelectorAll('.intro-list a');
    
    introLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const header = document.querySelector('header');
                const tabNav = document.getElementById('tabNavigation');
                const headerHeight = header ? header.offsetHeight : 0;
                const tabNavHeight = tabNav ? tabNav.offsetHeight : 0;
                const offsetTop = targetSection.offsetTop - headerHeight - tabNavHeight - 20;
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Back to Top Button
document.addEventListener('DOMContentLoaded', function() {
    const backToTopButton = document.getElementById('backToTop');
    
    if (!backToTopButton) return;
    
    // Show/hide button based on scroll position
    function toggleBackToTopButton() {
        if (window.pageYOffset > 300) {
            backToTopButton.classList.add('visible');
        } else {
            backToTopButton.classList.remove('visible');
        }
    }
    
    // Scroll to top when button is clicked
    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // Check scroll position on scroll
    window.addEventListener('scroll', toggleBackToTopButton);
    
    // Initial check
    toggleBackToTopButton();
});


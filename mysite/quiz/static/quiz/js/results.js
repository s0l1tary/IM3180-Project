document.addEventListener('DOMContentLoaded', function() {
    const oldProgress = document.getElementById('oldProgress');
    const gainProgress = document.getElementById('gainProgress');
    const prevBadge = document.getElementById('prevBadge');
    const gainBadge = document.getElementById('gainBadge');
    const totalBadge = document.getElementById('totalBadge');
    
    setTimeout(() => {
        // Animate progress bars
        if (oldProgress) {
            const oldWidth = oldProgress.getAttribute('data-width');
            oldProgress.style.width = oldWidth + '%';
        }
        
        if (gainProgress) {
            const gainWidth = gainProgress.getAttribute('data-width');
            gainProgress.style.width = gainWidth + '%';
        }
        
        // Animate badges with stagger
        setTimeout(() => {
            prevBadge.style.opacity = '1';
            prevBadge.style.transform = 'translateY(0)';
        }, 600);
        
        setTimeout(() => {
            gainBadge.style.opacity = '1';
            gainBadge.style.transform = 'translateY(0)';
        }, 900);
        
        setTimeout(() => {
            totalBadge.style.opacity = '1';
            totalBadge.style.transform = 'translateY(0)';
        }, 1200);
        
        // Add glow effect to gain bar when animation completes
        setTimeout(() => {
            if (gainProgress) {
                gainProgress.style.animation = 'glow 2s ease-in-out infinite';
            }
        }, 1700);
        
    }, 200);
});
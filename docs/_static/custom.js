// Hide class prefix from method names in sidebar
document.addEventListener('DOMContentLoaded', function() {
    const methodLinks = document.querySelectorAll('li.toctree-l4 a code span.pre');

    methodLinks.forEach(function(span) {
        const fullText = span.textContent;
        // Match pattern like "ClassName.method_name()"
        const match = fullText.match(/\.([^.()]+\(\))/);

        if (match) {
            // Extract just the method name with parentheses
            span.textContent = match[1];
        }
    });
});


function updatePrice(val) {
    const priceLabel = document.getElementById('priceLabel');
    if (priceLabel) priceLabel.innerText = val;
    applyFilters();
}

function applyFilters() {
    const searchInput = document.getElementById('searchInput');
    const priceRange = document.getElementById('priceRange');
    const cards = document.querySelectorAll('.menu-card');

    if (!searchInput || !priceRange) return;

    const search = searchInput.value.toLowerCase();
    const maxPrice = parseInt(priceRange.value);

    cards.forEach(card => {
        const name = card.getAttribute('data-name');
        const price = parseInt(card.getAttribute('data-price'));

        const matchesSearch = name.includes(search);
        const matchesPrice = price <= maxPrice;

        if (matchesSearch && matchesPrice) {
            card.style.display = "flex";
        } else {
            card.style.display = "none";
        }
    });
}

function showNotification(message) {
    const note = document.createElement('div');
    note.className = 'notification';
    note.innerText = message;
    document.body.appendChild(note);
    setTimeout(() => note.remove(), 2500);
}
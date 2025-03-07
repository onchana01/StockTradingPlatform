function toggleLimitPrice(select) {
    const limitPriceField = document.getElementById('id_limit_price').parentElement;
    if (select.value === 'MARKET') {
        limitPriceField.style.display = 'none';
    } else {
        limitPriceField.style.display = 'block';
    }
}
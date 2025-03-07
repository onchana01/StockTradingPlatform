function toggleLimitPrice(select) {
    const limitPriceField = document.getElementById('id_limit_price').parentElement;
    if (select.value === 'MARKET') {
        limitPriceField.style.display = 'none';
    } else {
        limitPriceField.style.display = 'block';
    }
}

function toggleAdvancedFields(select) {
    const limitPriceField = document.getElementById('id_limit_price').parentElement;
    const strikePriceField = document.getElementById('id_strike_price').parentElement;
    const expirationDateField = document.getElementById('id_expiration_date').parentElement;
    if (select.value === 'MARKET') {
        limitPriceField.style.display = 'none';
        strikePriceField.style.display = 'none';
        expirationDateField.style.display = 'none';
    } else if (select.value === 'LIMIT' || select.value === 'STOP_LOSS') {
        limitPriceField.style.display = 'block';
        strikePriceField.style.display = 'none';
        expirationDateField.style.display = 'none';
    } else {
        limitPriceField.style.display = 'block';
        strikePriceField.style.display = 'block';
        expirationDateField.style.display = 'block';
    }
}
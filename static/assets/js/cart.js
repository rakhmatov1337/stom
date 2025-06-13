document.addEventListener('DOMContentLoaded', function() {

    // CSRF token tekshiruv
    const csrfInput = document.querySelector('input[name=csrfmiddlewaretoken]');
    if (!csrfInput) {
        alert("CSRF token topilmadi! Iltimos, sahifani to‘liq yuklang.");
        return;
    }
    const csrfToken = csrfInput.value;

    // Har bir cart item uchun listenerlar
    document.querySelectorAll('.cart-product-item').forEach((item) => {
        const productId = item.getAttribute('data-product-id');
        const costHolder = item.querySelector('.cart-product-cost');
        const unitPrice = parseInt(costHolder.getAttribute('data-unit-price'));
        const span = item.querySelector('span');

        // + tugmasi
        item.querySelector('.cart_increment').addEventListener('click', () => {
            let count = parseInt(span.textContent);
            count++;
            updateQuantity(productId, count, span, costHolder, unitPrice, item);
        });

        // - tugmasi
        item.querySelector('.cart_decrement').addEventListener('click', () => {
            let count = parseInt(span.textContent);
            count = Math.max(count - 1, 0);
            updateQuantity(productId, count, span, costHolder, unitPrice, item);
        });
    });

    // AJAX orqali quantity yangilash
    function updateQuantity(productId, count, span, costHolder, unitPrice, item) {
        fetch('/cart/update/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: new URLSearchParams({
                product_id: productId,
                quantity: count
            })
        })
        .then((response) => {
            if (!response.ok) {
                throw new Error("HTTP status " + response.status);
            }
            return response.json();
        })
        .then(data => {
            // O'chirish
            if (data.updated_quantity <= 0) {
                item.remove();
            } else {
                span.textContent = `${data.updated_quantity} шт.`;
                costHolder.setAttribute('data-cost', unitPrice * data.updated_quantity);
            }
            // Jami hisoblarni yangilash
            calculateCost();
        })
        .catch(error => console.error('Xato:', error));
    }

    // Hisobni qayta hisoblash
    function calculateCost() {
        let totalCost = 0;

        document.querySelectorAll('.cart-product-cost').forEach((cost) => {
            const itemCost = cost.getAttribute('data-cost') || cost.textContent.replace(/\D/g, '');
            totalCost += parseInt(itemCost);
        });

        const cartCost = document.querySelector(".cart-details.cost p:last-child");
        const cartDelivery = document.querySelector(".cart-details.delivery p:last-child");
        const cartTotal = document.querySelector(".cart-details.total p:last-child");
        const cartText = document.querySelector(".cart-text");

        // Jami narx
        cartCost.textContent = totalCost.toLocaleString() + " UZS";

        // Yetkazib berish
        let deliveryCost = 0;
        if (totalCost >= 1000000) {
            cartText.textContent = "У вас бесплатная доставка!";
            deliveryCost = 0;
        } else if (totalCost > 0) {
            cartText.textContent = "Бесплатная доставка от 1 000 000 UZS";
            deliveryCost = 30000;
        } else {
            deliveryCost = 0;
        }

        // Yakuniy narx
        cartDelivery.textContent = deliveryCost.toLocaleString() + " UZS";
        cartTotal.textContent = (totalCost + deliveryCost).toLocaleString() + " UZS";
    }

    // Dastlabki hisob
    calculateCost();
});

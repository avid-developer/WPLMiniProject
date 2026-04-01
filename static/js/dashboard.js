function drawRoundedBar(context, x, y, width, height, radius) {
    const safeHeight = Math.max(height, 4);
    const safeRadius = Math.min(radius, safeHeight / 2, width / 2);
    context.beginPath();
    context.moveTo(x + safeRadius, y);
    context.lineTo(x + width - safeRadius, y);
    context.quadraticCurveTo(x + width, y, x + width, y + safeRadius);
    context.lineTo(x + width, y + safeHeight - safeRadius);
    context.quadraticCurveTo(x + width, y + safeHeight, x + width - safeRadius, y + safeHeight);
    context.lineTo(x + safeRadius, y + safeHeight);
    context.quadraticCurveTo(x, y + safeHeight, x, y + safeHeight - safeRadius);
    context.lineTo(x, y + safeRadius);
    context.quadraticCurveTo(x, y, x + safeRadius, y);
    context.closePath();
}

function drawWeeklyChart(labels, totals, target) {
    const canvas = document.getElementById('weeklyChart');
    if (!canvas) {
        return;
    }

    const context = canvas.getContext('2d');
    const ratio = window.devicePixelRatio || 1;
    const bounds = canvas.getBoundingClientRect();
    const width = bounds.width || canvas.width || 640;
    const height = 260;

    canvas.width = width * ratio;
    canvas.height = height * ratio;
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, width, height);

    const padding = { top: 24, right: 20, bottom: 48, left: 36 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;
    const maxValue = Math.max(target || 0, ...totals, 200);
    const step = chartWidth / labels.length;
    const barWidth = Math.max(step * 0.48, 18);

    context.strokeStyle = 'rgba(31, 31, 31, 0.12)';
    context.lineWidth = 1;
    context.font = '12px "Avenir Next", "Trebuchet MS", sans-serif';
    context.fillStyle = 'rgba(31, 31, 31, 0.58)';

    for (let index = 0; index <= 4; index += 1) {
        const y = padding.top + (chartHeight / 4) * index;
        context.beginPath();
        context.moveTo(padding.left, y);
        context.lineTo(width - padding.right, y);
        context.stroke();

        const value = Math.round(maxValue - (maxValue / 4) * index);
        context.fillText(String(value), 4, y + 4);
    }

    labels.forEach((label, index) => {
        const value = totals[index];
        const normalizedHeight = maxValue ? (value / maxValue) * chartHeight : 0;
        const x = padding.left + index * step + (step - barWidth) / 2;
        const y = padding.top + chartHeight - normalizedHeight;

        context.fillStyle = '#ff7a45';
        drawRoundedBar(context, x, y, barWidth, normalizedHeight || 4, 12);
        context.fill();

        context.fillStyle = 'rgba(31, 31, 31, 0.7)';
        context.fillText(String(value), x + 2, y - 8);
        context.fillStyle = 'rgba(31, 31, 31, 0.58)';
        context.fillText(label, x - 2, height - 14);
    });

    if (target) {
        const targetY = padding.top + chartHeight - (target / maxValue) * chartHeight;
        context.strokeStyle = '#3f7d58';
        context.setLineDash([6, 6]);
        context.beginPath();
        context.moveTo(padding.left, targetY);
        context.lineTo(width - padding.right, targetY);
        context.stroke();
        context.setLineDash([]);
        context.fillStyle = '#3f7d58';
        context.fillText(`Goal ${target}`, width - 84, targetY - 8);
    }
}

$(function () {
    const $name = $('#id_meal-name');
    const $type = $('#id_meal-meal_type');
    const $quantity = $('#id_meal-quantity');
    const $unit = $('#id_meal-unit');
    const $calories = $('#id_meal-calories');
    const $preview = $('#caloriePreview');
    const chartUrl = $('#weeklyChart').data('url');
    let chartPayload = null;

    function updatePreview() {
        const mealName = ($name.val() || 'This meal').trim();
        const quantity = ($quantity.val() || '0').trim();
        const unit = ($unit.val() || 'serving').trim();
        const calories = ($calories.val() || '0').trim();
        $preview.text(`${mealName}: ${quantity} ${unit} · ${calories} kcal`);
    }

    $(".preset-btn").on('click', function () {
        const $button = $(this);
        $name.val($button.data('name'));
        $type.val($button.data('type'));
        $quantity.val($button.data('quantity'));
        $unit.val($button.data('unit'));
        $calories.val($button.data('calories'));
        updatePreview();
        $('#mealForm').find('input, select, textarea').first().trigger('focus');
    });

    $('#mealForm').on('input change', 'input, select, textarea', updatePreview);
    updatePreview();

    if (chartUrl) {
        $.getJSON(chartUrl, function (payload) {
            chartPayload = payload;
            drawWeeklyChart(payload.labels, payload.totals, payload.target);
        });
    }

    $(window).on('resize', function () {
        if (chartPayload) {
            drawWeeklyChart(chartPayload.labels, chartPayload.totals, chartPayload.target);
        }
    });
});

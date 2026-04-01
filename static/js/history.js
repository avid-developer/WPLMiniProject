$(function () {
    const $rows = $('[data-history-row]');
    const $search = $('#historySearch');
    const $count = $('#visibleMealsCount');
    const $empty = $('#historyEmptyState');

    function applySearch() {
        const query = ($search.val() || '').trim().toLowerCase();
        let visible = 0;

        $rows.each(function () {
            const $row = $(this);
            const haystack = String($row.data('search') || '');
            const match = !query || haystack.includes(query);
            $row.toggleClass('d-none', !match);
            if (match) {
                visible += 1;
            }
        });

        $count.text(visible);
        $empty.toggleClass('d-none', visible !== 0);
    }

    $search.on('input', applySearch);
    applySearch();
});

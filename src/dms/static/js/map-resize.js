window.addEventListener("map:init", function (e) {
    const map = e.detail.map;
    const resizeObserver = new ResizeObserver(() => {
        map.invalidateSize();
    });

    resizeObserver.observe(map.getContainer());
}, false);

document.addEventListener('DOMContentLoaded', function(){
    // GRID
    var msnry = new Masonry('.controlcenter__masonry__offset', {
        itemSelector: '.controlcenter__masonry__block',
        columnWidth: '.controlcenter__masonry__block--sizer',
        percentPosition: true,
        transitionDuration: 0
    });

    // TABS
    var tab_klass = 'controlcenter__widget__tab',
        tab_klass_active = tab_klass + '--active',
        tab_nodes = document.querySelectorAll('.' + tab_klass);

    [].map.call(tab_nodes, function(tab){
        tab.addEventListener('click', function(e){
            [].map.call(tab.parentNode.childNodes, function(child){
                if (child.classList){
                    child.classList.remove(tab_klass_active);
                }
            });
            tab.classList.add(tab_klass_active);
        }, false);
    });
}, false);

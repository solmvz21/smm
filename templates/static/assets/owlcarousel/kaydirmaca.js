            $(document).ready(function() {
              var owl = $('.owl-carousel');
              owl.owlCarousel({
                margin: 10,
                nav: true,
                loop: true,
                responsive: {
                  0: {
                    items: 1
                  },
                  600: {
                    items: 2
                  },
                  1000: {
                    items: 4
                  }
                }
              })
            });

            
var owl = $('.mustu');
owl.owlCarousel({
    items:4,
    loop:true,
    margin:10,
    autoplay:true,
    autoplayTimeout:4000,
    autoplayHoverPause:true,
responsive: {
                  0: {
                    items: 1,
autoplay:true,
                  },
                  600: {
                    items: 2,
autoplay:true,
                  },
                  1000: {
                    items: 4
                  }
                }
});

var owl = $('.yorumalan');
owl.owlCarousel({
    items:1,
    loop:true,
    margin:10,
    autoplay:true,
    autoplayTimeout:4000,
    autoplayHoverPause:true,
responsive: {
                  0: {
                    items: 1,
autoplay:true,
                  },
                  600: {
                    items: 1,
autoplay:true,
                  },
                  1000: {
                    items: 1
                  }
                }
});


var owl = $('.mobil');
owl.owlCarousel({
    items:4,
    loop:true,
    margin:10,
    autoplay:false,
    autoplayTimeout:4000,
    autoplayHoverPause:true,
responsive: {
                  0: {
                    items: 1,
autoplay:true,
                  },
                  600: {
                    items: 2,
autoplay:true,
                  },
                  1000: {
                    items: 4
                  }
                }
});


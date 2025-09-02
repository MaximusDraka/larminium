document.addEventListener("DOMContentLoaded", function () {
  const humorCarouselEl = document.querySelector('#humorCarousel');

  if (humorCarouselEl && typeof mdb !== 'undefined') {
    new mdb.Carousel(humorCarouselEl, {
      interval: 5000,
      ride: 'carousel',
      touch: true,
      keyboard: true,
      wrap: true
    });
  }
});
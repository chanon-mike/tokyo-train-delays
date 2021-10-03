var scrollToTopBtn = document.querySelector("#scrollToTopBtn");

function scrollToTop() {
    // scroll to top logic
    document.documentElement.scrollTo({
        top: 0
    });
}

function handleScroll() {
    // Do something on scroll
    var scrollTotal = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    if (document.documentElement.scrollTop / scrollTotal > 0.4) {
        // Show button
        scrollToTopBtn.classList.add("showBtn");
    } else {
        // Hide button
        scrollToTopBtn.classList.remove("showBtn");
    }
}

scrollToTopBtn.addEventListener("click", scrollToTop);
document.addEventListener("scroll", handleScroll);
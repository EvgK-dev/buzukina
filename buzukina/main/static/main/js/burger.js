//Menu БУРГЕР 

let unlock = true; 
const header__burger = document.querySelector(".header__burger"); 

if (header__burger != null) {
	const header__menu = document.querySelector(".header__menu"); 
	const body = document.querySelector("body"); 

	header__burger.addEventListener("click", function (e) {
		if (unlock) {
            body_lock(); 
			header__burger.classList.toggle("_active"); 
			header__menu.classList.toggle("_active"); 
		}
	});

	header__menu.addEventListener("click", function() {
		if (body.classList.contains('_lock')) { 
			body.classList.remove("_lock"); 
		}
		header__burger.classList.remove("_active");
		header__menu.classList.remove("_active");
	});
};

//запрещает скролить
function body_lock() {
    let body = document.querySelector("body"); 
    if (body.classList.contains('_lock')) { 
        body.classList.remove("_lock"); 
    } else {
        body.classList.add("_lock");
    }
}

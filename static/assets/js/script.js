var dom_observer = new MutationObserver(function (mutation) {
    var overlay = document.querySelectorAll('.modal-backdrop.fade.show');
    if (overlay.length > 0) {
        overlay.forEach((lay, i) => {
            if (i > 1) {
                lay.remove();
            }
        });
    }
    setTimeout(() => {
        var popup = document.querySelector('.modal.fade.show');
        if (popup) {
            popup.style.cssText = '';
        }
        if (popup == null) {
            overlay.forEach(lay => {
                lay.remove();
            });
        }
    }, 400)
});



var signup_card_toggle_p = document.querySelectorAll('.signup_card_toggle_p');
var free_account_section = document.querySelector('.free-account-section');
var business_account_section = document.querySelector('.business-account-section');
var choose_section = document.querySelector('.choose_section');

var su_btn = document.querySelector('.signun-popup-btn');
if (su_btn) {
    su_btn.addEventListener('click', () => {
        business_account_section.classList.add('hidden');
        free_account_section.classList.add('hidden');
        choose_section.classList.remove('hidden');
    })
}

signup_card_toggle_p.forEach(parent => {
    var signup_card_btn = parent.querySelectorAll('.signup-card-btn');
    var submit = parent.querySelector('.signup-card-submit');
    signup_card_btn.forEach(ele => {
        ele.addEventListener('click', () => {
            signup_card_btn.forEach(all => all.classList.remove('signup-card-active'))
            ele.classList.add('signup-card-active');
            submit.classList.add('bg-[#205a42]', 'cursor-pointer');
            submit.disabled = false;
            submit.onclick = function () {
                if (ele.getAttribute('data-link') == 'free') {
                    free_account_section.classList.remove('hidden');
                    choose_section.classList.add('hidden');
                } else {
                    business_account_section.classList.remove('hidden');
                    choose_section.classList.add('hidden');
                }
            }
        })
    })
});
document.addEventListener('DOMContentLoaded', () => {
    var business_account_next_step = document.querySelector('.business-account-next-step');
    var business_account_section_2 = document.querySelector('.business-account-section_2')
    if (business_account_next_step) {
        business_account_next_step.addEventListener('click', () => {
            var inps = business_account_section.querySelectorAll('input');
            var email_inps = business_account_section.querySelectorAll('input[type="email"]');
            var password_inps = business_account_section.querySelectorAll('.password-show-p input');
            inps.forEach(inp => {
                if (inp.value.trim() == '') {
                    inp.classList.add('error');
                } else {
                    inp.classList.remove('error');
                }
            });

            var phone_num_p_select = business_account_section.querySelector('.phone_num_p select');
            var phone_num_p_inp = business_account_section.querySelector('.phone_num_p input');

            if (password_inps[0].value != '' && password_inps[1].value != '') {
                if (password_inps[0].value == password_inps[1].value) {
                    if (password_inps[0].value.length > 7 && password_inps[1].value.length > 7) {
                        password_inps[0].classList.remove('error');
                        password_inps[1].classList.remove('error');
                    }
                } else {
                    password_inps[0].classList.add('error');
                    password_inps[1].classList.add('error');
                }

            }

            email_inps.forEach(inp => {
                if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(inp.value) == false) {
                    inp.classList.add('error');
                } else {
                    // inp.classList.add('error');
                    // phone_num_p_inp.classList.add('error')
                    var data = {
                        email: inp.value,
                        phone: `${phone_num_p_select.value}${phone_num_p_inp.value}`
                    };
                    fetch('/api/validate_user/', {
                        method: 'POST', // or 'PUT'
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data),
                    })
                        .then((response) => response.json())
                        .then((data) => {
                            console.log(data);
                            if (data.success) {
                                inp.classList.remove('error');
                                phone_num_p_inp.classList.remove('error');
                                var error = business_account_section.querySelectorAll('input.error');
                                var div_error = business_account_section.querySelectorAll('div.error');
                                console.log(error, div_error);
                                if (error.length == 0 && div_error.length == 0) {
                                    business_account_section_2.classList.remove('hidden');
                                    business_account_section.classList.add('hidden')
                                }
                            } else {
                                if (data.message.includes('email')) {
                                    Toast.fire({
                                        icon: 'error',
                                        title: 'Email Already Exist!'
                                    });
                                    inp.classList.add('error');
                                }

                                if (data.message.includes('number')) {
                                    Toast.fire({
                                        icon: 'error',
                                        title: 'Phone Number Already Exist!'
                                    });
                                    phone_num_p_inp.classList.add('error')
                                }
                            }
                        })
                        .catch((error) => {
                            console.error('Error:', error);
                        });
                }
            });

        });


        var step_back_btn = document.querySelector('.step_back_btn');
        step_back_btn.addEventListener('click', () => {
            business_account_section_2.classList.add('hidden');
            business_account_section.classList.remove('hidden')
        })
    }

    var back_buttons = document.querySelectorAll('.back_button');
    back_buttons.forEach(back_button => {
        back_button.addEventListener('click', () => {
            var onNext = document.querySelector('.business-account-section_2:not(.hidden)')
            if (onNext) {
                business_account_section_2.classList.add('hidden');
                business_account_section.classList.remove('hidden')
            } else {
                choose_section.classList.remove('hidden');
                business_account_section.classList.add('hidden');
                business_account_section_2.classList.add('hidden');
                free_account_section.classList.add('hidden');
            }
        })
    })

})

document.addEventListener('DOMContentLoaded', () => {
    var business_license_document = document.querySelector('.business_license_document');
    var business_signup_final_btn = document.querySelector('.business_signup_final_btn');
    if (business_signup_final_btn) {
        business_signup_final_btn.addEventListener('click', () => {
            if (business_license_document.value == '') {
                Toast.fire({
                    icon: 'error',
                    title: 'Upload License Document!'
                });
            } else {
                business_signup_final_btn.type = 'submit';
                business_signup_final_btn.click();
            }
        })
    }
})


var header = document.querySelector('.header-dynamic-height');
var devare_header_height = document.querySelectorAll('.devare-header-height');
if (window.innerWidth > 540) {
    devare_header_height.forEach(ele => {
        var height = header.clientHeight;
        var total = ele.getAttribute('data-height');
        ele.style.cssText = `min-height:calc(${parseInt(total)}vh - ${parseInt(height)}px)`
    })
}

var password_show_p = document.querySelectorAll('.password-show-p');
password_show_p.forEach(parent => {
    var inp = parent.querySelector('.password-show');
    var icon = parent.querySelector('.password-show-icon');

    icon.addEventListener('click', () => {
        if (inp.type == 'password') {
            inp.type = 'text';
            icon.classList.add('show')
        } else {
            inp.type = 'password'
            icon.classList.remove('show')
        }
    })
});

var nav_openers = document.querySelectorAll('.nav_opener');
var navbar_mobile = document.querySelector('.navbar_mobile')
nav_openers.forEach(nav_opener => {
    nav_opener.addEventListener('click', () => {
        navbar_mobile.classList.toggle('hidden')
    })
})
try {
    
var swiper = new Swiper(".card-slider-1", {
    slidesPerView: "auto",
    spaceBetween: 20,
    // pagination: {
    //     el: ".slider-1-paggination",
    // },
    pagination: false,

    navigation: {
        nextEl: ".slider-1-next",
        prevEl: ".slider-1-prev",
    },
    autoplay: true,
    centeredSlides: true,
    loop: true,
    breakpoints: {
        0: {
            pagination: false,
            spaceBetween: 8,
        },

        661: {
            // pagination: {
            //     el: ".slider-1-paggination",
            // },
            pagination: false,
            spaceBetween: 20,
        },
    }

});

var swiper = new Swiper(".card-slider-2", {
    slidesPerView: "3",
    spaceBetween: 20,
    // pagination: {
    //     el: ".slider-2-paggination",
    // },
    pagination: false,
    navigation: {
        nextEl: ".slider-2-next",
        prevEl: ".slider-2-prev",
    },
    autoplay: true,
    breakpoints: {
        0: {
            slidesPerView: 2,
            spaceBetween: 8,
            pagination: false,
        },
        370: {
            slidesPerView: 2,

        },
        661: {
            slidesPerView: 3,
        },
    }
});

var swiper = new Swiper(".category_slider", {
    slidesPerView: 9,
    spaceBetween: 10,
    navigation: {
        nextEl: ".category-2-next",
        prevEl: ".category-2-prev",
    },
    breakpoints: {
        0: {
            slidesPerView: 3,
        },
        540: {
            slidesPerView: 4,
        },
        640: {
            slidesPerView: 6,
        },
        1280: {
            slidesPerView: 9,
        }
    },
});

var swiper = new Swiper('.banner-slider', {
    spaceBetween: 10,
    navigation: {
        nextEl: ".banner-slider-next",
        prevEl: ".banner-slider-prev",
    },
    breakpoints: {
        0: {
            // pagination: {
            //     el: ".banner-slider-paggination",
            // },
            pagination: false,

        },
        640: {
            pagination: false
        },
    },
    effect: 'fade',
    speed: 1400,
    loop: true,
    autoplay: true
});

var swiper__ = new Swiper(".mySwiper_", {
    spaceBetween: 10,
    slidesPerView: 'auto',
    freeMode: true,
    watchSlidesProgress: true,
});

var swiper2 = new Swiper(".mySwiper_thumb", {
    spaceBetween: 10,
    navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev",
    },
    thumbs: {
        swiper: swiper__,
    },
    autoplay: true,
});

var swiper = new Swiper(".category-slider", {
    slidesPerView: 'auto',
    spaceBetween: 10,
    autoplay: true,
});
} catch (error) {
    
}

var counters = document.querySelectorAll('.counter');
counters.forEach(counter => {
    var minus = counter.querySelector('.counter_minus');
    var plus = counter.querySelector('.counter_plus');
    var value = counter.querySelector('.counter_value');
    var total = value.getAttribute('data-total')

    total = parseInt(total)
    var current = parseInt(value.innerHTML);

    minus.addEventListener('click', () => {
        if (current > 0) {
            current--
            value.innerHTML = current
        }
    })

    plus.addEventListener('click', () => {
        if (current < total) {
            current++;
            // console.log(current);
            value.innerHTML = current
        }
    })
})

var radio_select_p = document.querySelectorAll('.radio-select-parent');
radio_select_p.forEach(p => {
    p.addEventListener('click', () => {
        var radio_select_options = p.querySelector('.radio-select-options');
        var inp = p.querySelector('input');

        if (radio_select_options.classList.contains('radio_selected')) {
            // radio_select_options.classList.remove('radio_selected');
            inp.checked = false;
        } else {
            // radio_select_options.classList.add('radio_selected');
            inp.checked = true;
        }
    })
})

var filters_show = document.querySelector('.filters_show');
if (filters_show) {
    var filters_bar = document.querySelector('.filters_bar');
    var close_btn_filter = document.querySelector('.close_btn_filter')
    filters_show.addEventListener('click', () => {
        filters_bar.style.cssText = '';
        filters_bar.classList.add('filters_bar_active');
    })
    if(close_btn_filter){

        close_btn_filter.addEventListener('click', () => {
            filters_bar.classList.remove('filters_bar_active');
        })
    }
}


var sticky_sidebar = document.querySelectorAll('.top-sticky-dynamic');
var nav = document.querySelector('header');

if (sticky_sidebar.length > 0) {
    sticky_sidebar.forEach(sidebar => {
        sidebar.style.cssText = `height:calc(100vh - ${nav.clientHeight + 40}px);top:${nav.clientHeight + 20}px;`;
    })
}


var create_category = document.querySelector('.create_category');

if (create_category) {
    create_category.addEventListener('click', () => {
        var category_name = document.querySelector('.category_name');
        var category_status = document.querySelector('.category_status');
        var category_close = document.querySelector('.category_close');
        var category_spawner = document.querySelector('.category_spawner');

        // if (category_status.value.trim() == '' || category_name.value.trim() == '') {
        //     alert('Please fill all the fields!')
        // } else {

        //     var unique_id = Date.now();

        //     var div = document.createElement('div');

        //     div.innerHTML = `
        //     <div data-category-id="${unique_id}" class="cursor-pointer category_tab rounded-full py-1 px-3 border flex items-center gap-2">
        //         <h1 class="text-sm">${category_name.value}</h1>
        //         <svg data-bs-target="#edit_cat" data-bs-toggle="modal" width="1.25rem" height="1.25rem" viewBox="0 0 17 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        //             <circle cx="8.31441" cy="7.84126" r="7.76753" fill="#E7E7E7" />
        //             <path
        //                 d="M5.65729 10.829C5.6118 10.8289 5.56683 10.8194 5.52523 10.801C5.48363 10.7826 5.44631 10.7557 5.41566 10.7221C5.38444 10.6888 5.36063 10.6492 5.34576 10.6061C5.3309 10.5629 5.32534 10.517 5.32943 10.4716L5.40975 9.58806L9.12048 5.87763L10.2801 7.03726L6.57038 10.7474L5.68712 10.8277C5.67721 10.8286 5.66725 10.8291 5.65729 10.829ZM10.5116 6.8054L9.35228 5.64577L10.0477 4.95019C10.0781 4.9197 10.1143 4.89551 10.1541 4.879C10.1939 4.8625 10.2366 4.854 10.2796 4.854C10.3227 4.854 10.3654 4.8625 10.4052 4.879C10.445 4.89551 10.4811 4.9197 10.5116 4.95019L11.207 5.64577C11.2375 5.67623 11.2617 5.7124 11.2782 5.75221C11.2947 5.79202 11.3031 5.8347 11.3031 5.87779C11.3031 5.92089 11.2947 5.96357 11.2782 6.00338C11.2617 6.04319 11.2375 6.07936 11.207 6.10982L10.5119 6.80507L10.5116 6.8054Z"
        //                 fill="#555555" />
        //         </svg>
        //     </div>
        // `;
        //     category_spawner.appendChild(div);

        //     var new_div = document.createElement('div');
        //     new_div.innerHTML = `
        //     <div data-category-id="${unique_id}" class="flex gap-6 flex-wrap subcategory_spawner hidden" data-subcategory-id="2">
        //         <div data-bs-target="#addSubCategory" data-bs-toggle="modal"
        //             class="subcategory_opener min-h-[16rem] cursor-pointer text-center rounded-lg admin-card-hover p-3 min-w-[16rem] w-fit bg-white flex flex-col gap-4 items-center justify-center">
        //             <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        //                 <path
        //                     d="M20.0026 36.6668V20.0002M20.0026 20.0002V3.3335M20.0026 20.0002H36.6693M20.0026 20.0002H3.33594"
        //                     stroke="#555555" stroke-width="5" stroke-linecap="round" />
        //             </svg>

        //             <h1>Add Subcategory</h1>
        //         </div>
        //     </div>
        // `;

        //     var subcat_area = document.querySelector('.subcat_area')
        //     subcat_area.appendChild(new_div)

        //     category_fn();


        //     category_close.click();
        // }
    })
    var category_fn = () => {

        var category_tab = document.querySelectorAll('.category_tab');
        category_tab.forEach((tab) => {
            tab.addEventListener('click', () => {
                var subcategory_spawner = document.querySelectorAll('.subcategory_spawner')
                var subcategory_spawner_active = document.querySelector(`.subcategory_spawner[data-category-id="${tab.getAttribute("data-category-id")}"]`);
                subcategory_spawner.forEach(all => {
                    all.classList.add('hidden');
                });
                subcategory_spawner_active.classList.remove('hidden')

                category_tab.forEach(all => { all.classList.remove('category_tab_active') });
                tab.classList.add('category_tab_active')

            })
        })


        var subcategory_opener_id = document.querySelector('.category_tab').getAttribute('data-category-id');
        var subcategory_opener = document.querySelectorAll('.subcategory_opener');
        subcategory_opener.forEach(card => {
            card.onclick = () => {
                var parent = card.closest('.subcategory_spawner');
                subcategory_opener_id = parent.getAttribute('data-category-id');
            }
        });

        var subcategory_btn = document.querySelector('.subcategory_btn');
        subcategory_btn.onclick = () => {
            var subcategory_name = document.querySelector('.subcategory_name');
            var subcategory_type = document.querySelector('.subcategory_type');
            var subcategory_status = document.querySelector('.subcategory_status');
            var subcategory_image = document.querySelector('.subcategory_image');

            console.log(subcategory_name.value, subcategory_type.value, subcategory_image.value);

            if (subcategory_opener_id != '') {
                if (subcategory_name.value.trim() == '' || subcategory_type.value.trim() == '' || subcategory_status.value.trim() == '' || subcategory_image.value.trim() == '') {
                    alert('fill all the fields!')
                } else {
                    var spawner = document.querySelector(`.subcategory_spawner[data-category-id="${subcategory_opener_id}"]`);
                    var div = document.createElement('div');
                    div.classList.add('devare_btn_p')
                    div.innerHTML = `
                <div
                class="text-center rounded-lg admin-card-hover p-4 min-w-[16rem] w-fit bg-white flex flex-col gap-3">
                <div class="flex items-center justify-between">
                    <div
                        class="rounded-full py-1 px-3 border border-[#05D672] bg-[#E7FFF3] text-sm text-[#05D672]">
                        ${subcategory_status.value}</div>
                    <div class="flex items-center gap-2">
                        <div
                            class="devare_btn cursor-pointer h-[2rem] w-[2rem] rounded-full border flex items-center justify-center">
                            <svg width="1.25rem" height="1.25rem" viewBox="0 0 9 9" fill="none"
                                xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M3.51298 1.45849H4.99012C4.99012 1.26261 4.91231 1.07475 4.7738 0.936243C4.63529 0.797733 4.44743 0.71992 4.25155 0.71992C4.05567 0.71992 3.86781 0.797733 3.7293 0.936243C3.59079 1.07475 3.51298 1.26261 3.51298 1.45849ZM3.0206 1.45849C3.0206 1.13202 3.15028 0.818925 3.38113 0.588077C3.61198 0.357228 3.92508 0.227539 4.25155 0.227539C4.57802 0.227539 4.89111 0.357228 5.12196 0.588077C5.35281 0.818925 5.4825 1.13202 5.4825 1.45849H7.94441C8.0097 1.45849 8.07232 1.48443 8.11849 1.5306C8.16466 1.57677 8.1906 1.63939 8.1906 1.70468C8.1906 1.76998 8.16466 1.83259 8.11849 1.87876C8.07232 1.92493 8.0097 1.95087 7.94441 1.95087H7.42544L6.83753 7.04406C6.79598 7.40408 6.62351 7.73627 6.35296 7.9774C6.08241 8.21854 5.73265 8.3518 5.37024 8.35182H3.13286C2.77044 8.3518 2.42068 8.21854 2.15013 7.9774C1.87958 7.73627 1.70712 7.40408 1.66556 7.04406L1.07766 1.95087H0.55869C0.493397 1.95087 0.430777 1.92493 0.384608 1.87876C0.338438 1.83259 0.3125 1.76998 0.3125 1.70468C0.3125 1.63939 0.338438 1.57677 0.384608 1.5306C0.430777 1.48443 0.493397 1.45849 0.55869 1.45849H3.0206ZM3.75917 3.42801C3.75917 3.36272 3.73323 3.3001 3.68706 3.25393C3.64089 3.20776 3.57827 3.18182 3.51298 3.18182C3.44768 3.18182 3.38506 3.20776 3.33889 3.25393C3.29272 3.3001 3.26679 3.36272 3.26679 3.42801V6.3823C3.26679 6.44759 3.29272 6.51021 3.33889 6.55638C3.38506 6.60255 3.44768 6.62849 3.51298 6.62849C3.57827 6.62849 3.64089 6.60255 3.68706 6.55638C3.73323 6.51021 3.75917 6.44759 3.75917 6.3823V3.42801ZM4.99012 3.18182C4.92483 3.18182 4.86221 3.20776 4.81604 3.25393C4.76987 3.3001 4.74393 3.36272 4.74393 3.42801V6.3823C4.74393 6.44759 4.76987 6.51021 4.81604 6.55638C4.86221 6.60255 4.92483 6.62849 4.99012 6.62849C5.05541 6.62849 5.11803 6.60255 5.1642 6.55638C5.21037 6.51021 5.23631 6.44759 5.23631 6.3823V3.42801C5.23631 3.36272 5.21037 3.3001 5.1642 3.25393C5.11803 3.20776 5.05541 3.18182 4.99012 3.18182Z"
                                    fill="#555555" />
                            </svg>
                        </div>
                        <div
                        data-bs-target="#editSubCat" data-bs-toggle="modal"
                            class="cursor-pointer h-[2rem] w-[2rem] rounded-full border flex items-center justify-center">
                            <svg width="1.25rem" height="1.25rem" viewBox="0 0 8 7" fill="none"
                                xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M1.0587 6.56892C1.01064 6.56884 0.963126 6.55875 0.919176 6.53931C0.875227 6.51986 0.835803 6.49148 0.803413 6.45597C0.770437 6.42076 0.745274 6.37898 0.729574 6.33336C0.713874 6.28774 0.707992 6.23931 0.712314 6.19126L0.797178 5.25785L4.71754 1.3378L5.9427 2.56295L2.02337 6.48265L1.09022 6.56754C1.07974 6.5685 1.06922 6.56896 1.0587 6.56892ZM6.18724 2.31799L4.96243 1.09284L5.69711 0.357965C5.72928 0.325751 5.76748 0.300195 5.80954 0.282759C5.85158 0.265322 5.89666 0.256348 5.94218 0.256348C5.9877 0.256348 6.03277 0.265322 6.07482 0.282759C6.11687 0.300195 6.15508 0.325751 6.18724 0.357965L6.92192 1.09284C6.95413 1.12502 6.97968 1.16323 6.99711 1.2053C7.01454 1.24736 7.02351 1.29244 7.02351 1.33798C7.02351 1.38351 7.01454 1.4286 6.99711 1.47066C6.97968 1.51272 6.95413 1.55093 6.92192 1.58311L6.18759 2.31764L6.18724 2.31799Z"
                                    fill="#555555" />
                            </svg>
                        </div>
                    </div>
                </div>
                <div class="p-2 w-fit h-fit mx-auto rounded-full border border-[#205a42]">
                    <div class="h-[6rem] w-[6rem] overflow-hidden rounded-full">
                        <img class="object-cover w-full h-full"
                            src='${URL.createObjectURL(subcategory_image.files[0])}' />
                    </div>
                </div>
                <h2 class="font-semibold">${subcategory_name.value}</h2>
                <p class="text-[#555555] text-sm">1200 Deals</p>
            </div>
                `;
                    spawner.appendChild(div);
                    subcategory_name.value = '';
                    subcategory_type.value = '';
                    subcategory_status.value = '';
                    subcategory_image.value = '';
                    document.querySelector('.subcat_close').click();
                    document.querySelectorAll('.devare_btn').forEach(del => {
                        del.onclick = function () {
                            del.closest('.devare_btn_p').remove();
                        }
                    });

                }
            } else {
                console.error('subcategory_opener_id not found !!!');
            }

        };
        document.querySelectorAll('.devare_btn').forEach(del => {
            del.onclick = function () {
                del.closest('.devare_btn_p').remove();
            }
        });
    }
    category_fn();
}
if (document.querySelectorAll('.devare_btn').length > 0) {
    document.querySelectorAll('.devare_btn').forEach(del => {
        del.onclick = function () {
            del.closest('.devare_btn_p').remove();
        }
    });
}

var business_tabs = document.querySelectorAll('.business_tab');
if (business_tabs.length > 0) {
    business_tabs.forEach(business_tab => {
        business_tab.addEventListener('click', () => {
            business_tabs.forEach(all => {
                all.classList.remove('business_tab_active')
            });
            business_tab.classList.add('business_tab_active');
            var data_div = document.querySelector(`.business_tab_data[tab-name="${business_tab.getAttribute('tab-name')}"]`);
            document.querySelectorAll(`.business_tab_data`).forEach(all => { all.classList.add('hidden') })
            data_div.classList.remove('hidden');
        })
    })
}


var steps = document.querySelectorAll('.deal_parent_p');

// if (steps.length > 0) {
//     steps.forEach(step => {
//         var step_one_form = step.querySelector('.step-one-form');
//         var step_two_form = step.querySelector('.step-two-form');
//         var step_three_form = step.querySelector('.step-three-form');

//         var step_one_bar = step.querySelector('.step-one');
//         var step_two_bar = step.querySelector('.step-two');
//         var step_three_bar = step.querySelector('.step-three');

//         var deal_creator_form = step.querySelector('.deal_creator_form');


//         // var step_one_btn = step.querySelector('.step-one-btn');

//         // step_one_btn.addEventListener('click', () => {

//         //     var inps = step_two_form.querySelectorAll('input:not([type=hidden]');
//         //     var selects = step_two_form.querySelectorAll('select');
//         //     var deal_description = step_two_form.querySelector('.deal_description');
//         //     var files = step_two_form.querySelectorAll('input[type=file]');
//         //     var dates = step_two_form.querySelectorAll('input[type=date]');

//         //     inps.forEach(inp => {
//         //         if (inp.required) {
//         //             if (inp.value.trim() == '') {
//         //                 inp.classList.add('error')
//         //             } else {
//         //                 inp.classList.remove('error')
//         //             }
//         //         }
//         //     });


//         //     if (deal_description.value.trim() == '') {
//         //         deal_description.classList.add('error')
//         //     } else {
//         //         deal_description.classList.remove('error')
//         //     }

//         //     selects.forEach(select => {
//         //         if (select.value.trim() == '') {
//         //             select.classList.add('error')
//         //         } else {
//         //             select.classList.remove('error')
//         //         }
//         //     });

//         //     files.forEach(file => {
//         //         if (file.required) {
//         //             if (file.value.trim() == '') {
//         //                 file.classList.add('error')
//         //             } else {
//         //                 file.classList.remove('error')
//         //             }
//         //         }
//         //     });

//         //     // dates
//         //     var str_date = new Date(dates[0].value);
//         //     var end_date = new Date(dates[1].value);

//         //     if (str_date && end_date) {
//         //         if (str_date.getTime() > end_date.getTime()) {
//         //             Toast.fire({
//         //                 icon: 'error',
//         //                 title: 'End date should be greater than start date!'
//         //             });
//         //             dates[0].classList.add('error')
//         //             dates[1].classList.add('error')
//         //         } else {
//         //             dates[0].classList.remove('error')
//         //             dates[1].classList.remove('error')
//         //         }
//         //     }

//         //     if (edit_deal_page) {
//         //         files.forEach(file => {
//         //             file.classList.remove('error')
//         //         });
//         //     }






//         // });

//         var step_two_btn = step.querySelector('.step-two-btn');

//         step_two_btn.addEventListener('click', () => {

//             var inps = step_two_form.querySelectorAll('input:not([type=hidden]');
//             var textareas = step_two_form.querySelectorAll('textarea');




//             var selects = step_two_form.querySelectorAll('select');
//             var deal_description = step_two_form.querySelector('.deal_description');
//             var files = step_two_form.querySelectorAll('input[type=file]');
//             var dates = step_two_form.querySelectorAll('input[type=date]');

//             inps.forEach(inp => {
//                 if (inp.required) {
//                     if (inp.value.trim() == '') {
//                         inp.classList.add('error')
//                     } else {
//                         inp.classList.remove('error')
//                     }
//                 }
//             });


//             if (deal_description.value.trim() == '') {
//                 deal_description.classList.add('error')
//             } else {
//                 deal_description.classList.remove('error')
//             }

//             selects.forEach(select => {
//                 if (select.value.trim() == '') {
//                     select.classList.add('error')
//                 } else {
//                     select.classList.remove('error')
//                 }
//             });

//             files.forEach(file => {
//                 if (file.required) {
//                     if (file.value.trim() == '') {
//                         file.classList.add('error')
//                     } else {
//                         file.classList.remove('error')
//                     }
//                 }
//             });

//             // dates
//             var str_date = new Date(dates[0].value);
//             var end_date = new Date(dates[1].value);

//             if (str_date && end_date) {
//                 if (str_date.getTime() > end_date.getTime()) {
//                     Toast.fire({
//                         icon: 'error',
//                         title: 'End date should be greater than start date!'
//                     });
//                     dates[0].classList.add('error')
//                     dates[1].classList.add('error')
//                 } else {
//                     dates[0].classList.remove('error')
//                     dates[1].classList.remove('error')
//                 }
//             }








//             inps.forEach(inp => {
//                 if (inp.value.trim() == '') {
//                     inp.classList.add('error');
//                 } else {
//                     inp.classList.remove('error');
//                 }
//             })

//             textareas.forEach((text, i) => {
//                 if (i == 0) {
//                     if (text.value.trim() == '') {
//                         text.classList.add('error')
//                     } else {
//                         text.classList.remove('error')
//                     }
//                 }
//             })

//             var errors = step.querySelectorAll('.error');

//             if (errors.length == 0) {
//                 // step_one_form.classList.add('hidden');
//                 // step_three_form.classList.remove('hidden');
//                 // step_two_bar.classList.add('step-active-fill');
//                 // step_three_bar.classList.add('step-active');
//                 var create_deal_form_p = document.querySelector('.create_deal_form_p');
//                 create_deal_form_p.submit();
//                 // var div = document.createElement('div');
//                 // div.classList.add('overlay');
//                 // body.appendChild(div)
//             }
//             else {
//                 console.log(errors)
//                 errors[0].scrollIntoView();;
//             }


//         });

//         var deal_step_back = document.querySelector('.deal_step_back');
//         if (deal_step_back) {
//             deal_step_back.addEventListener('click', () => {
//                 step_one_form.classList.add('hidden');
//                 step_two_form.classList.remove('hidden');
//             })
//         }

//     })


// }

var img_preview = document.querySelector('.img_preview');
if (img_preview) {
    var img_upload = document.querySelector('.img_upload');
    img_upload.addEventListener('input', () => {
        img_preview.src = URL.createObjectURL(img_upload.files[0])
    })

    var remove_img = document.querySelector('.remove_img');
    if (remove_img) {
        remove_img.addEventListener('click', () => {
            img_preview.src = 'https://www.underseaproductions.com/wp-content/uploads/2013/11/dummy-image-square.jpg';
            img_upload.value = ''
        })
    }


};

// var time_counter = document.querySelector('.time_counter');
// if (time_counter) {

//     // Set the date we're counting down to
//     var countDownDate = new Date(time_counter.getAttribute('data-date')).getTime();

//     // Update the count down every 1 second
//     var x = setInterval(function () {

//         // Get today's date and time
//         var now = new Date().getTime();

//         // Find the distance between now and the count down date
//         var distance = countDownDate - now;

//         // Time calculations for days, hours, minutes and seconds
//         var days = Math.floor(distance / (1000 * 60 * 60 * 24));
//         var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
//         var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
//         var seconds = Math.floor((distance % (1000 * 60)) / 1000);

//         // Output the result in an element with id="demo"

//         var counter_days = document.querySelector('.counter_days');
//         var counter_hrs = document.querySelector('.counter_hrs');
//         var counter_mins = document.querySelector('.counter_mins');
//         var counter_secs = document.querySelector('.counter_secs');

//         counter_days.innerText = days > 0 ? days : '00';
//         counter_hrs.innerText = hours > 0 ? hours : '00';
//         counter_mins.innerText = minutes > 0 ? minutes : '00';
//         counter_secs.innerText = seconds > 0 ? seconds : '00';


//         // If the count down is over, write some text 
//         if (distance < 0) {
//             clearInterval(x);
//         }
//     }, 1000);
// }




// var img_renders_p = document.querySelectorAll('.img_render');
// document.addEventListener('DOMContentLoaded', () => {
//     img_renders_p.forEach((img_render, i) => {
//         var img_render_inp = img_render.querySelector('.img_render_inp');

//         img_render_inp.addEventListener('input', () => {
//             var img_rendered = img_render.querySelectorAll('.img_rendered');

//             if (img_rendered.length > 0) {
//                 img_rendered.forEach(img => {
//                     img.remove();
//                 })
//             }

//             var div = document.createElement('div');
//             div.classList = `rounded-md h-[7rem] w-[7rem] img_rendered overflow-hidden relative`;
//             div.innerHTML = `<div class='absolute top-2 right-2 img_del z-1 cursor-pointer'>
//                 <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
//                     <path d="M12 0.625C5.6625 0.625 0.625 5.6625 0.625 12C0.625 18.3375 5.6625 23.375 12 23.375C18.3375 23.375 23.375 18.3375 23.375 12C23.375 5.6625 18.3375 0.625 12 0.625ZM16.3875 17.6875L12 13.3L7.6125 17.6875L6.3125 16.3875L10.7 12L6.3125 7.6125L7.6125 6.3125L12 10.7L16.3875 6.3125L17.6875 7.6125L13.3 12L17.6875 16.3875L16.3875 17.6875Z" fill="#205a42"></path>
//                 </svg>
//             </div>
//             <img src='${URL.createObjectURL(img_render_inp.files[0])}' class='h-full w-full object-cover' />`
//             img_render.appendChild(div);


//             var img_del = document.querySelector('.img_del');
//             img_del.addEventListener('click', () => {
//                 var img_rendered = img_render.querySelector('.img_rendered');
//                 if (img_rendered) {
//                     img_rendered.remove();
//                 }
//                 img_render_inp.value = '';
//             })
//         })
//     });
//     var img_dels = document.querySelectorAll('.img_del');
//     img_dels.forEach((img_del, i) => {
//         img_del.addEventListener('click', () => {
//             var img_rendered = document.querySelectorAll('.img_rendered');
//             if (img_rendered.length > 0) {
//                 img_rendered.forEach(img => {
//                     img.remove();
//                 })
//             }
//             document.querySelector("img_render_inp")[i].value = '';
//         })
//     })
// })




var img_renders_name = document.querySelectorAll('.img_render');
document.addEventListener('DOMContentLoaded', () => {
    img_renders_name.forEach((img_render, i) => {
        var img_render_inp = img_render.querySelector('.img_render_inp');
        if (img_render_inp) {
            img_render_inp.addEventListener('input', () => {
                var img_rendered = img_render.querySelectorAll('.img_rendered');
                if (img_rendered.length > 0) {
                    img_rendered.forEach(img => {
                        img.remove();
                    })
                }
                if (Array.from(img_render_inp.files).length <= 4) {
                    Array.from(img_render_inp.files).forEach(file => {
                        if (file.type.includes('image')) {

                            var div = document.createElement('div');
                            div.classList = `mt-3 mr-3 inline-block rounded-md h-[7rem] w-[7rem] img_rendered overflow-hidden relative`;
                            div.innerHTML = `<div class='absolute top-2 right-2 img_del z-1 cursor-pointer'>
                            
                            </div>
                            <img src='${URL.createObjectURL(file)}' class='h-full w-full object-cover' />`
                            // <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            //     <path d="M12 0.625C5.6625 0.625 0.625 5.6625 0.625 12C0.625 18.3375 5.6625 23.375 12 23.375C18.3375 23.375 23.375 18.3375 23.375 12C23.375 5.6625 18.3375 0.625 12 0.625ZM16.3875 17.6875L12 13.3L7.6125 17.6875L6.3125 16.3875L10.7 12L6.3125 7.6125L7.6125 6.3125L12 10.7L16.3875 6.3125L17.6875 7.6125L13.3 12L17.6875 16.3875L16.3875 17.6875Z" fill="#205a42"></path>
                            // </svg>
                            img_render.appendChild(div);

                            // var img_del = document.querySelector('.img_del');

                            // img_del.addEventListener('click', () => {
                            //     var img_rendered = img_render.querySelector('.img_rendered');
                            //     if (img_rendered) {
                            //         img_rendered.remove();
                            //     }
                            //     img_render_inp.value = '';
                            // })

                        } else {
                            var div = document.createElement('div');
                            div.classList = `img_rendered text-sm mt-[0.5rem]`;
                            div.innerHTML = `<p>${file.name}</p>`
                            img_render.appendChild(div);
                        }
                    })
                } else {
                    Toast.fire({
                        icon: 'error',
                        title: 'You can add upto 4 images!'
                    });
                    img_render_inp.value = ''
                }
            })
        }
    });
})

var all_country_code = document.querySelectorAll('.all_country_code');
var all_codes = [{ "country": "Afghanistan", "code": "93", "iso": "AF" },
{ "country": "Albania", "code": "355", "iso": "AL" },
{ "country": "Algeria", "code": "213", "iso": "DZ" },
{ "country": "American Samoa", "code": "1-684", "iso": "AS" },
{ "country": "Andorra", "code": "376", "iso": "AD" },
{ "country": "Angola", "code": "244", "iso": "AO" },
{ "country": "Anguilla", "code": "1-264", "iso": "AI" },
{ "country": "Antarctica", "code": "672", "iso": "AQ" },
{ "country": "Antigua and Barbuda", "code": "1-268", "iso": "AG" },
{ "country": "Argentina", "code": "54", "iso": "AR" },
{ "country": "Armenia", "code": "374", "iso": "AM" },
{ "country": "Aruba", "code": "297", "iso": "AW" },
{ "country": "Australia", "code": "61", "iso": "AU" },
{ "country": "Austria", "code": "43", "iso": "AT" },
{ "country": "Azerbaijan", "code": "994", "iso": "AZ" },
{ "country": "Bahamas", "code": "1-242", "iso": "BS" },
{ "country": "Bahrain", "code": "973", "iso": "BH" },
{ "country": "Bangladesh", "code": "880", "iso": "BD" },
{ "country": "Barbados", "code": "1-246", "iso": "BB" },
{ "country": "Belarus", "code": "375", "iso": "BY" },
{ "country": "Belgium", "code": "32", "iso": "BE" },
{ "country": "Belize", "code": "501", "iso": "BZ" },
{ "country": "Benin", "code": "229", "iso": "BJ" },
{ "country": "Bermuda", "code": "1-441", "iso": "BM" },
{ "country": "Bhutan", "code": "975", "iso": "BT" },
{ "country": "Bolivia", "code": "591", "iso": "BO" },
{ "country": "Bosnia and Herzegovina", "code": "387", "iso": "BA" },
{ "country": "Botswana", "code": "267", "iso": "BW" },
{ "country": "Brazil", "code": "55", "iso": "BR" },
{ "country": "British Indian Ocean Territory", "code": "246", "iso": "IO" },
{ "country": "British Virgin Islands", "code": "1-284", "iso": "VG" },
{ "country": "Brunei", "code": "673", "iso": "BN" },
{ "country": "Bulgaria", "code": "359", "iso": "BG" },
{ "country": "Burkina Faso", "code": "226", "iso": "BF" },
{ "country": "Burundi", "code": "257", "iso": "BI" },
{ "country": "Cambodia", "code": "855", "iso": "KH" },
{ "country": "Cameroon", "code": "237", "iso": "CM" },
{ "country": "Canada", "code": "1", "iso": "CA" },
{ "country": "Cape Verde", "code": "238", "iso": "CV" },
{ "country": "Cayman Islands", "code": "1-345", "iso": "KY" },
{ "country": "Central African Republic", "code": "236", "iso": "CF" },
{ "country": "Chad", "code": "235", "iso": "TD" },
{ "country": "Chile", "code": "56", "iso": "CL" },
{ "country": "China", "code": "86", "iso": "CN" },
{ "country": "Christmas Island", "code": "61", "iso": "CX" },
{ "country": "Cocos Islands", "code": "61", "iso": "CC" },
{ "country": "Colombia", "code": "57", "iso": "CO" },
{ "country": "Comoros", "code": "269", "iso": "KM" },
{ "country": "Cook Islands", "code": "682", "iso": "CK" },
{ "country": "Costa Rica", "code": "506", "iso": "CR" },
{ "country": "Croatia", "code": "385", "iso": "HR" },
{ "country": "Cuba", "code": "53", "iso": "CU" },
{ "country": "Curacao", "code": "599", "iso": "CW" },
{ "country": "Cyprus", "code": "357", "iso": "CY" },
{ "country": "Czech Republic", "code": "420", "iso": "CZ" },
{ "country": "Democratic Republic of the Congo", "code": "243", "iso": "CD" },
{ "country": "Denmark", "code": "45", "iso": "DK" },
{ "country": "Djibouti", "code": "253", "iso": "DJ" },
{ "country": "Dominica", "code": "1-767", "iso": "DM" },
{ "country": "East Timor", "code": "670", "iso": "TL" },
{ "country": "Ecuador", "code": "593", "iso": "EC" },
{ "country": "Egypt", "code": "20", "iso": "EG" },
{ "country": "El Salvador", "code": "503", "iso": "SV" },
{ "country": "Equatorial Guinea", "code": "240", "iso": "GQ" },
{ "country": "Eritrea", "code": "291", "iso": "ER" },
{ "country": "Estonia", "code": "372", "iso": "EE" },
{ "country": "Ethiopia", "code": "251", "iso": "ET" },
{ "country": "Falkland Islands", "code": "500", "iso": "FK" },
{ "country": "Faroe Islands", "code": "298", "iso": "FO" },
{ "country": "Fiji", "code": "679", "iso": "FJ" },
{ "country": "Finland", "code": "358", "iso": "FI" },
{ "country": "France", "code": "33", "iso": "FR" },
{ "country": "French Polynesia", "code": "689", "iso": "PF" },
{ "country": "Gabon", "code": "241", "iso": "GA" },
{ "country": "Gambia", "code": "220", "iso": "GM" },
{ "country": "Georgia", "code": "995", "iso": "GE" },
{ "country": "Germany", "code": "49", "iso": "DE" },
{ "country": "Ghana", "code": "233", "iso": "GH" },
{ "country": "Gibraltar", "code": "350", "iso": "GI" },
{ "country": "Greece", "code": "30", "iso": "GR" },
{ "country": "Greenland", "code": "299", "iso": "GL" },
{ "country": "Grenada", "code": "1-473", "iso": "GD" },
{ "country": "Guam", "code": "1-671", "iso": "GU" },
{ "country": "Guatemala", "code": "502", "iso": "GT" },
{ "country": "Guernsey", "code": "44-1481", "iso": "GG" },
{ "country": "Guinea", "code": "224", "iso": "GN" },
{ "country": "Guinea-Bissau", "code": "245", "iso": "GW" },
{ "country": "Guyana", "code": "592", "iso": "GY" },
{ "country": "Haiti", "code": "509", "iso": "HT" },
{ "country": "Honduras", "code": "504", "iso": "HN" },
{ "country": "Hong Kong", "code": "852", "iso": "HK" },
{ "country": "Hungary", "code": "36", "iso": "HU" },
{ "country": "Iceland", "code": "354", "iso": "IS" },
{ "country": "India", "code": "91", "iso": "IN" },
{ "country": "Indonesia", "code": "62", "iso": "ID" },
{ "country": "Iran", "code": "98", "iso": "IR" },
{ "country": "Iraq", "code": "964", "iso": "IQ" },
{ "country": "Ireland", "code": "353", "iso": "IE" },
{ "country": "Isle of Man", "code": "44-1624", "iso": "IM" },
{ "country": "Israel", "code": "972", "iso": "IL" },
{ "country": "Italy", "code": "39", "iso": "IT" },
{ "country": "Ivory Coast", "code": "225", "iso": "CI" },
{ "country": "Jamaica", "code": "1-876", "iso": "JM" },
{ "country": "Japan", "code": "81", "iso": "JP" },
{ "country": "Jersey", "code": "44-1534", "iso": "JE" },
{ "country": "Jordan", "code": "962", "iso": "JO" },
{ "country": "Kazakhstan", "code": "7", "iso": "KZ" },
{ "country": "Kenya", "code": "254", "iso": "KE" },
{ "country": "Kiribati", "code": "686", "iso": "KI" },
{ "country": "Kosovo", "code": "383", "iso": "XK" },
{ "country": "Kuwait", "code": "965", "iso": "KW" },
{ "country": "Kyrgyzstan", "code": "996", "iso": "KG" },
{ "country": "Laos", "code": "856", "iso": "LA" },
{ "country": "Latvia", "code": "371", "iso": "LV" },
{ "country": "Lebanon", "code": "961", "iso": "LB" },
{ "country": "Lesotho", "code": "266", "iso": "LS" },
{ "country": "Liberia", "code": "231", "iso": "LR" },
{ "country": "Libya", "code": "218", "iso": "LY" },
{ "country": "Liechtenstein", "code": "423", "iso": "LI" },
{ "country": "Lithuania", "code": "370", "iso": "LT" },
{ "country": "Luxembourg", "code": "352", "iso": "LU" },
{ "country": "Macao", "code": "853", "iso": "MO" },
{ "country": "Macedonia", "code": "389", "iso": "MK" },
{ "country": "Madagascar", "code": "261", "iso": "MG" },
{ "country": "Malawi", "code": "265", "iso": "MW" },
{ "country": "Malaysia", "code": "60", "iso": "MY" },
{ "country": "Maldives", "code": "960", "iso": "MV" },
{ "country": "Mali", "code": "223", "iso": "ML" },
{ "country": "Malta", "code": "356", "iso": "MT" },
{ "country": "Marshall Islands", "code": "692", "iso": "MH" },
{ "country": "Mauritania", "code": "222", "iso": "MR" },
{ "country": "Mauritius", "code": "230", "iso": "MU" },
{ "country": "Mayotte", "code": "262", "iso": "YT" },
{ "country": "Mexico", "code": "52", "iso": "MX" },
{ "country": "Micronesia", "code": "691", "iso": "FM" },
{ "country": "Moldova", "code": "373", "iso": "MD" },
{ "country": "Monaco", "code": "377", "iso": "MC" },
{ "country": "Mongolia", "code": "976", "iso": "MN" },
{ "country": "Montenegro", "code": "382", "iso": "ME" },
{ "country": "Montserrat", "code": "1-664", "iso": "MS" },
{ "country": "Morocco", "code": "212", "iso": "MA" },
{ "country": "Mozambique", "code": "258", "iso": "MZ" },
{ "country": "Myanmar", "code": "95", "iso": "MM" },
{ "country": "Namibia", "code": "264", "iso": "NA" },
{ "country": "Nauru", "code": "674", "iso": "NR" },
{ "country": "Nepal", "code": "977", "iso": "NP" },
{ "country": "Netherlands", "code": "31", "iso": "NL" },
{ "country": "Netherlands Antilles", "code": "599", "iso": "AN" },
{ "country": "New Caledonia", "code": "687", "iso": "NC" },
{ "country": "New Zealand", "code": "64", "iso": "NZ" },
{ "country": "Nicaragua", "code": "505", "iso": "NI" },
{ "country": "Niger", "code": "227", "iso": "NE" },
{ "country": "Nigeria", "code": "234", "iso": "NG" },
{ "country": "Niue", "code": "683", "iso": "NU" },
{ "country": "North Korea", "code": "850", "iso": "KP" },
{ "country": "Northern Mariana Islands", "code": "1-670", "iso": "MP" },
{ "country": "Norway", "code": "47", "iso": "NO" },
{ "country": "Oman", "code": "968", "iso": "OM" },
{ "country": "Pakistan", "code": "92", "iso": "PK" },
{ "country": "Palau", "code": "680", "iso": "PW" },
{ "country": "Palestine", "code": "970", "iso": "PS" },
{ "country": "Panama", "code": "507", "iso": "PA" },
{ "country": "Papua New Guinea", "code": "675", "iso": "PG" },
{ "country": "Paraguay", "code": "595", "iso": "PY" },
{ "country": "Peru", "code": "51", "iso": "PE" },
{ "country": "Philippines", "code": "63", "iso": "PH" },
{ "country": "Pitcairn", "code": "64", "iso": "PN" },
{ "country": "Poland", "code": "48", "iso": "PL" },
{ "country": "Portugal", "code": "351", "iso": "PT" },
{ "country": "Qatar", "code": "974", "iso": "QA" },
{ "country": "Republic of the Congo", "code": "242", "iso": "CG" },
{ "country": "Reunion", "code": "262", "iso": "RE" },
{ "country": "Romania", "code": "40", "iso": "RO" },
{ "country": "Russia", "code": "7", "iso": "RU" },
{ "country": "Rwanda", "code": "250", "iso": "RW" },
{ "country": "Saint Barthelemy", "code": "590", "iso": "BL" },
{ "country": "Saint Helena", "code": "290", "iso": "SH" },
{ "country": "Saint Kitts and Nevis", "code": "1-869", "iso": "KN" },
{ "country": "Saint Lucia", "code": "1-758", "iso": "LC" },
{ "country": "Saint Martin", "code": "590", "iso": "MF" },
{ "country": "Saint Pierre and Miquelon", "code": "508", "iso": "PM" },
{ "country": "Saint Vincent and the Grenadines", "code": "1-784", "iso": "VC" },
{ "country": "Samoa", "code": "685", "iso": "WS" },
{ "country": "San Marino", "code": "378", "iso": "SM" },
{ "country": "Sao Tome and Principe", "code": "239", "iso": "ST" },
{ "country": "Saudi Arabia", "code": "966", "iso": "SA" },
{ "country": "Senegal", "code": "221", "iso": "SN" },
{ "country": "Serbia", "code": "381", "iso": "RS" },
{ "country": "Seychelles", "code": "248", "iso": "SC" },
{ "country": "Sierra Leone", "code": "232", "iso": "SL" },
{ "country": "Singapore", "code": "65", "iso": "SG" },
{ "country": "Sint Maarten", "code": "1-721", "iso": "SX" },
{ "country": "Slovakia", "code": "421", "iso": "SK" },
{ "country": "Slovenia", "code": "386", "iso": "SI" },
{ "country": "Solomon Islands", "code": "677", "iso": "SB" },
{ "country": "Somalia", "code": "252", "iso": "SO" },
{ "country": "South Africa", "code": "27", "iso": "ZA" },
{ "country": "South Korea", "code": "82", "iso": "KR" },
{ "country": "South Sudan", "code": "211", "iso": "SS" },
{ "country": "Spain", "code": "34", "iso": "ES" },
{ "country": "Sri Lanka", "code": "94", "iso": "LK" },
{ "country": "Sudan", "code": "249", "iso": "SD" },
{ "country": "Suriname", "code": "597", "iso": "SR" },
{ "country": "Svalbard and Jan Mayen", "code": "47", "iso": "SJ" },
{ "country": "Swaziland", "code": "268", "iso": "SZ" },
{ "country": "Sweden", "code": "46", "iso": "SE" },
{ "country": "Switzerland", "code": "41", "iso": "CH" },
{ "country": "Syria", "code": "963", "iso": "SY" },
{ "country": "Taiwan", "code": "886", "iso": "TW" },
{ "country": "Tajikistan", "code": "992", "iso": "TJ" },
{ "country": "Tanzania", "code": "255", "iso": "TZ" },
{ "country": "Thailand", "code": "66", "iso": "TH" },
{ "country": "Togo", "code": "228", "iso": "TG" },
{ "country": "Tokelau", "code": "690", "iso": "TK" },
{ "country": "Tonga", "code": "676", "iso": "TO" },
{ "country": "Trinidad and Tobago", "code": "1-868", "iso": "TT" },
{ "country": "Tunisia", "code": "216", "iso": "TN" },
{ "country": "Turkey", "code": "90", "iso": "TR" },
{ "country": "Turkmenistan", "code": "993", "iso": "TM" },
{ "country": "Turks and Caicos Islands", "code": "1-649", "iso": "TC" },
{ "country": "Tuvalu", "code": "688", "iso": "TV" },
{ "country": "U.S. Virgin Islands", "code": "1-340", "iso": "VI" },
{ "country": "Uganda", "code": "256", "iso": "UG" },
{ "country": "Ukraine", "code": "380", "iso": "UA" },
{ "country": "United Arab Emirates", "code": "971", "iso": "AE" },
{ "country": "United Kingdom", "code": "44", "iso": "GB" },
{ "country": "United States", "code": "1", "iso": "US" },
{ "country": "Uruguay", "code": "598", "iso": "UY" },
{ "country": "Uzbekistan", "code": "998", "iso": "UZ" },
{ "country": "Vanuatu", "code": "678", "iso": "VU" },
{ "country": "Vatican", "code": "379", "iso": "VA" },
{ "country": "Venezuela", "code": "58", "iso": "VE" },
{ "country": "Vietnam", "code": "84", "iso": "VN" },
{ "country": "Wallis and Futuna", "code": "681", "iso": "WF" },
{ "country": "Western Sahara", "code": "212", "iso": "EH" },
{ "country": "Yemen", "code": "967", "iso": "YE" },
{ "country": "Zambia", "code": "260", "iso": "ZM" },
{ "country": "Zimbabwe", "code": "263", "iso": "ZW" }]
all_country_code.forEach((country) => {
    country.innerHTML = '';
    all_codes.forEach(single => {
        var option = document.createElement('option');
        option.value = '+' + single.code;
        option.innerText = '+' + single.code;
        if (single.code == '971') {
            option.selected = true;
        }
        country.appendChild(option)
    })
})


var video = document.querySelectorAll('.video-tag-grid');
var video_play = document.querySelectorAll('.play');
var video_pause = document.querySelectorAll('.pause');

video_pause.forEach(btn => {
    btn.style.cssText = `display:none`;
})

video_play.forEach((btn, i) => {
    btn.addEventListener('click', () => {
        video[i].play();
        btn.style.cssText = `display:none`;
        video_pause[i].style.cssText = `display:block`;
    })
})
video_pause.forEach((btn, i) => {
    btn.addEventListener('click', () => {
        video[i].pause();
        btn.style.cssText = `display:none`
        video_play[i].style.cssText = `display:block`
    })
})


var devareBtn_ClickHandler = (btn) => {
    var devare_deal = document.querySelectorAll('.devare_deal');
    devare_deal.forEach(btn => {
        btn.addEventListener('click', () => {
            var deal_p = btn.closest('.deal_p');
            var is_created = deal_p.querySelector('.created_field')
            if (is_created) {
                deal_p.remove();
            }
            else {

                deal_p.classList.add('hidden')
                var del_inp = document.createElement('input')
                del_inp.setAttribute('type', 'hidden')
                del_inp.setAttribute('name', 'is_devared')
                del_inp.classList.add('is_devared')
                deal_p.appendChild(del_inp)
            }

            // deal_p.remove();
        })
    })
}


document.addEventListener('DOMContentLoaded', () => {

    setTimeout(() => {
        devareBtn_ClickHandler()

        var deal_add_btn_border = document.querySelector('.deal_add_btn_border');
        if (deal_add_btn_border) {
            deal_add_btn_border.addEventListener('click', () => {
                setTimeout(() => {
                    devareBtn_ClickHandler()
                    discont()
                }, 400);
            })
        }
    }, 1000);

    function discont() {
        var discount_percentage = document.querySelectorAll('.discount-field');
        if (discount_percentage.length > 0) {
            discount_percentage.forEach(inp => {
                inp.addEventListener('input', () => {
                    if (inp.value > 100) {
                        inp.value = 100;
                    }
                    if (inp.value < 0) {
                        inp.value = 0;
                    }
                })
            })
        }
    }
    discont()
})




var input_files = document.querySelectorAll('input[type=file]')
if (input_files.length > 0) {
    input_files.forEach(inp => {
        inp.addEventListener('input', () => {
            var accept = inp.getAttribute('accept');
            if (accept) {
                if (accept.includes('image')) {
                    Array.from(inp.files).forEach(file => {
                        if (file.size > 3000000) {
                            Toast.fire({
                                icon: 'error',
                                title: 'Image size should be less than 3MB!'
                            });
                            inp.value = '';
                            var img_rendered = document.querySelector('.img_rendered')
                            img_rendered.remove();
                        }
                    })
                }
                if (accept.includes('video')) {
                    Array.from(inp.files).forEach(file => {
                        if (file.size > 23000000) {
                            Toast.fire({
                                icon: 'error',
                                title: 'Video size should be less than 23MB!'
                            });
                            inp.value = '';
                            var img_rendered = document.querySelector('.img_rendered')
                            if (img_rendered) {
                                img_rendered.remove();
                            }
                        }
                    })
                }
            }
        })
    })
}

var forgot_password_inp = document.querySelector('.forgot_password_inp')
var forgot_password_btn = document.querySelector('.forgot_password_btn');
var forgot_password_btn_h = document.querySelector('.forgot_password_btn_h');
if (forgot_password_btn) {
    forgot_password_btn.addEventListener('click', () => {
        if (forgot_password_inp.value.trim() != '') {
            if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(forgot_password_inp.value) == false) {
                forgot_password_inp.classList.add('error');
            } else {
                forgot_password_inp.classList.remove('error');
                fetch('verify_email_for_new_password').then(resp => resp.json()).then(data => {
                    console.log(data);
                })
            }
        } else {
            forgot_password_inp.classList.add('error');
        }

        var verify_email_for_new_password = document.querySelector('.verify_email_for_new_password')
        if (!(forgot_password_inp.classList.contains('error'))) {
            verify_email_for_new_password.submit();
        }

        var forgot_p_form = document.querySelector('.forgot_p_form');

        var error = forgot_p_form.querySelectorAll('.error');
        console.log(error);

        // if(error.length == 0){
        //     forgot_password_btn_h.click();
        // }
    })
}


var password_p = document.querySelectorAll('.password_p');
if (password_p.length > 0) {
    password_p.forEach(parent => {
        var password_ = document.querySelector('.password_');
        var password_confirm = document.querySelector('.password_confirm');
        var password_btn = document.querySelector('.password_btn');
        password_btn.disabled = true
        function password_check() {
            if (password_.value.trim() != '' && password_confirm.value.trim() != '') {
                if (password_.value != password_confirm.value) {
                    password_.classList.add('error');
                    password_confirm.classList.add('error');
                    password_btn.disabled = true;
                } else {
                    password_.classList.remove('error');
                    password_confirm.classList.remove('error');
                    password_btn.disabled = false;
                }
            }
        };

        password_.addEventListener('input', password_check)
        password_confirm.addEventListener('input', password_check)
    })
}

var counter_resend = document.querySelector('.counter_resend');
if (counter_resend) {
    var resend_btn = document.querySelector('.resend_btn');

    var interval = setInterval(() => {
        if (+counter_resend.innerText > 0) {
            (counter_resend.innerText) = (+counter_resend.innerText) - 1
        }
        else {
            resend_btn.classList.remove('hidden');
            counter_resend.parentElement.parentElement.classList.add('hidden')
            clearInterval(interval)
        }
    }, 1000);
}



var textare_max = document.querySelectorAll('.text-area-max-length textarea');
textare_max.forEach(text => {
    text.maxLength = 250;
    text.rows = 6;
});

// setTimeout(() => {
//     var preloader = document.querySelector('.preloader');
//     preloader.remove();
// }, 1400);


var free_account_signup_form = document.querySelector('.free_account_signup');
if (free_account_signup_form) {
    var inps = free_account_signup_form.querySelectorAll('input');
    var form_submit = free_account_signup_form.querySelector('.form_submit');
    var email = free_account_signup_form.querySelector('input[type="email"]')
    var number = free_account_signup_form.querySelector('input[type="number"]')
    var select = free_account_signup_form.querySelector('select')

    form_submit.addEventListener('click', () => {
        inps.forEach(inp => {
            if (inp.value.trim() == '') {
                inp.classList.add('error');
            }
            else {
                inp.classList.remove('error');
            }
        });

        if (number.value.length > 7 && number.value.length < 13) {
            number.classList.remove('error')
        } else {
            number.classList.add('error')
        }

        var password_1 = free_account_signup_form.querySelectorAll('.password-show-p input')[0]
        var password_2 = free_account_signup_form.querySelectorAll('.password-show-p input')[1]

        if (password_1.value.trim() != '') {
            if (password_1.value.length > 7 && password_2.value.length > 7 && password_1.value == password_2.value) {
                password_1.classList.remove('error')
                password_2.classList.remove('error')
            } else {
                password_1.classList.add('error')
                password_2.classList.add('error')
                Toast.fire({
                    icon: 'error',
                    title: 'Password must be same and 8 characters long!'
                });
            }
        }


        if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(email.value) == false) {
            email.classList.add('error');
        } else {
            email.classList.add('error');
            number.classList.add('error')
            var data = {
                email: email.value,
                phone: `${select.value}${number.value}`
            };
            fetch('/api/validate_user/', {
                method: 'POST', // or 'PUT'
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            })
                .then((response) => response.json())
                .then((data) => {
                    console.log(data);
                    if (data.success) {
                        email.classList.remove('error');
                        number.classList.remove('error')
                    } else {
                        if (data.message.includes('email')) {
                            Toast.fire({
                                icon: 'error',
                                title: 'Email Already Exist!'
                            });
                            email.classList.add('error');
                            number.classList.remove('error')

                        }

                        if (data.message.includes('number')) {
                            Toast.fire({
                                icon: 'error',
                                title: 'Phone Number Already Exist!'
                            });
                            number.classList.add('error')
                            email.classList.remove('error');
                        }
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        }





        setTimeout(() => {
            var errors = free_account_signup_form.querySelectorAll('.error')
            console.log(errors);
            if (errors.length == 0) {
                free_account_signup_form.submit();
            }
        }, 200);
    })


}

var all_multi = document.querySelectorAll(".multi_select_")
all_multi.forEach(multi => {
    new TomSelect(multi, {
        maxItems: 123
    });
})


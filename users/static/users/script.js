//Referenced this video to embed google maps into our website:
//Source: https://www.youtube.com/watch?v=4U_AAGHzTok&ab_channel=GreatStack

function myMap() {
    const markers = [
    {
        locationName: "Shannon Library" ,
        lat:38.0364566,
        lng:-78.5053683,
        address: '160 McCormick Rd, <br> Charlottesville, <br> VA 22904'
    },
    {
        locationName: "Rice Hall" ,
        lat:38.0316188,
        lng:-78.5196006,
        address: "85 Engineer's Way, <br> Charlottesville, <br> VA 22903"
    },
    {
        locationName: "Gibbons House" ,
        lat:38.0331636,
        lng:-78.514679,
        address: '425 Tree House Dr, <br> Charlottesville, <br> VA 22904'
    },
    {
        locationName: "Student Health and Wellness" ,
        lat:38.0301536,
        lng:-78.503874,
        address: '550 Brandon Ave, <br> Charlottesville, <br> VA 22903'
    }
    ];

    var mapProp= {
        center:new google.maps.LatLng(38.0341423,-78.5111598),
        zoom:15,
        disableDefaultUI: true,
        styles:
        [
    {
        "featureType": "water",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#e9e9e9"
            },
            {
                "lightness": 17
            }
        ]
    },
    {
        "featureType": "landscape",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#f5f5f5"
            },
            {
                "lightness": 20
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#ffffff"
            },
            {
                "lightness": 17
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "geometry.stroke",
        "stylers": [
            {
                "color": "#ffffff"
            },
            {
                "lightness": 29
            },
            {
                "weight": 0.2
            }
        ]
    },
    {
        "featureType": "road.arterial",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#ffffff"
            },
            {
                "lightness": 18
            }
        ]
    },
    {
        "featureType": "road.local",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#ffffff"
            },
            {
                "lightness": 16
            }
        ]
    },
    {
        "featureType": "poi",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#f5f5f5"
            },
            {
                "lightness": 21
            }
        ]
    },
    {
        "featureType": "poi.park",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#dedede"
            },
            {
                "lightness": 21
            }
        ]
    },
    {
        "elementType": "labels.text.stroke",
        "stylers": [
            {
                "visibility": "on"
            },
            {
                "color": "#ffffff"
            },
            {
                "lightness": 16
            }
        ]
    },
    {
        "elementType": "labels.text.fill",
        "stylers": [
            {
                "saturation": 36
            },
            {
                "color": "#333333"
            },
            {
                "lightness": 40
            }
        ]
    },
    {
        "elementType": "labels.icon",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "transit",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#f2f2f2"
            },
            {
                "lightness": 19
            }
        ]
    },
    {
        "featureType": "administrative",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#fefefe"
            },
            {
                "lightness": 20
            }
        ]
    },
    {
        "featureType": "administrative",
        "elementType": "geometry.stroke",
        "stylers": [
            {
                "color": "#fefefe"
            },
            {
                "lightness": 17
            },
            {
                "weight": 1.2
            }
        ]
    }
]
};
    var map = new google.maps.Map(document.getElementById("googleMap"),mapProp);
    const fetchMarker = "https://icons.iconarchive.com/icons/icons-land/flat-vector-map-marker/48/Marker-1-PushPin-Green-icon.png";
    /**
    *Loop through all markers and add it to the current map
    */
    for (let i = 0; i<markers.length; i++){
        const marker = new google.maps.Marker({
        position: { lat: markers[i].lat, lng:markers[i].lng},
        map:map,
        icon: fetchMarker,
        title: markers[i].locationName
        });

        const infoWindow = new google.maps.InfoWindow({
            content: `<strong>${markers[i].locationName}</strong><br>${markers[i].address}`
        });

        marker.addListener("click", () => {
            infoWindow.open(map, marker);
        });

    }


}
const loginPopup = document.querySelector(".login-popup");
const close = document.querySelector(".close");

document.addEventListener("DOMContentLoaded", function () {
    const loginPopup = document.querySelector(".login-popup");
    const close = document.querySelector(".close");

    if (!loginPopup || !close) {
        return;
    }

    function showPopup() {
        const timeLimit = 3;
        let i = 0;
        const timer = setInterval(function () {
            i++;
            if (i === timeLimit) {
                clearInterval(timer);
                loginPopup.classList.add("show");
            }
            console.log(i);
        }, 1000);
    }

    window.addEventListener("load", showPopup);

    close.addEventListener("click", function () {
        loginPopup.classList.remove("show");
    });

    window.onclick = function (event) {
        if (event.target === loginPopup) {
            loginPopup.classList.remove("show");
        }
    };
});

document.addEventListener("DOMContentLoaded", function () {
    let openPopupBtn = document.getElementById("openPopup");
    let modalContent = document.getElementById("modal-content");

    openPopupBtn.addEventListener("click", function (event) {
        event.preventDefault();

        fetch(openPopupBtn.href, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(response => response.text())
        .then(data => {
            modalContent.innerHTML = data;
        })
        .catch(error => console.error("Error loading form:", error));
    });
});

function myFunction() {
  document.getElementById("myDropdown").classList.toggle("show");
}

//source: https://www.w3schools.com/howto/howto_js_filter_dropdown.asp
function filterFunction() {
  var input, filter, ul, li, a, i;
  input = document.getElementById("myInput");
  filter = input.value.toUpperCase();
  div = document.getElementById("myDropdown");
  a = div.getElementsByTagName("a");
  for (i = 0; i < a.length; i++) {
    txtValue = a[i].textContent || a[i].innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      a[i].style.display = "";
    } else {
      a[i].style.display = "none";
    }
  }
}

   gsap.to("#text", {
    duration: 5,
    attr: { startOffset: "0%" },
    ease: "linear",
    repeat: -1
  });

   AOS.init({
        duration: 3000,
        once: false,
    });
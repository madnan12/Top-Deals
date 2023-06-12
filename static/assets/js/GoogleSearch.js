

let myMap = document.createElement('div')
const GoogleAPiPlace = (text_search, success, fail) => {
    let lat;
    let lng;
    try {
        navigator.geolocation.getCurrentPosition((position) => {
            lat = position.coords.latitude
            lng = position.coords.longitude
        })

        var user_location = new google.maps.LatLng(lat, lng);

        
        var map = new google.maps.Map(
            myMap, 
            { center: user_location, zoom: 5 }
        );

        var request = {
            query: text_search,
            fields: ['name', 'geometry', 'formatted_address'],
        };

        var service = new google.maps.places.PlacesService(map);

        service.textSearch(request, function (results, status) {
            if (status === google.maps.places.PlacesServiceStatus.OK) {
                success && success(results)
                try{
                    // map.setCenter(results[0].geometry.location);
                }
                catch{}
            }
            else{
                fail && fail(status, 'No Result Found')
            }
        });

    }
    catch (err){

        console.log(err)
    }
}


var watercolor = L.tileLayer('http://{s}.tile.stamen.com/watercolor/{z}/{x}/{y}.jpg');
var labels = L.tileLayer('http://{s}.tile.stamen.com/toner-labels/{z}/{x}/{y}.jpg');

var map = L.mapbox.map('map','fabmud.hd0kn6ee', {minZoom: 1, maxZoom: 5});

//map.addLayer(watercolor);
//map.addLayer(labels);

var addressPoints = [
[35.777325, -78.641205, "Raleigh"],
[35.795149, -78.784027, "Cary"],
[35.910910, -79.054565, "Chapel Hill"],
[35.999841, -78.908997, "Durham"],
[35.980952, -78.514862, "Wake Forest"],
[35.230646, -80.838470, "Charlotte"],


[34.264061, -6.578296, "DARDAR SAAD (KENITRA, Morocco)"],
[47.408867, 4.717312, 'Tarek Ziadé (Turcey, 21, France)'],
[45.523452, -122.676207, 'Jeff Bryner (Portland, Oregon, United States)'],
[1.352083, 103.819836,'Victor Neo (Singapore)'],
[22.572646, 88.363895, 'Kaustav Das Modak (Kolkata, West Bengal, India)'],
//[undefined,undefined, 'Anurag Sharma'],
[-14.235004,-51.925280, 'Pedro Markun (Brazil)'],
[31.968599, -99.901813, 'Rabimba Karanjai (Texas, United States)'],
[44.314844, -85.602364, 'Donovan Preston (MI, United States)'],
[27.700000, 85.333333, 'Nootan Ghimire (Kathmandu, Nepal)'],
[37.090240, -95.712891, 'Vishwanathan Krishnamoorthy (United States)'],
[-6.249028, 106.996952, 'Rizky Ariestiyansyah (Bekasi, Indonesia)'],
[37.090240, -95.712891, 'Yuan Wang (United States)'],
[43.653226, -79.383184, 'Gabriel Luong (Toronto, Ontario, Canada)']
];

var clusters = L.markerClusterGroup({
    iconCreateFunction: function(cluster) {
        return new L.DivIcon({ html: '<div class="moz-marker">' + cluster.getChildCount() + '</div>' });
    }
});

for (var i = 0; i < addressPoints.length; i++) {
	var a = addressPoints[i];
	var title = a[2];
	var marker = L.marker(new L.LatLng(a[0], a[1]), { title: title });
	marker.bindPopup(title);
	clusters.addLayer(marker);
}

map.addLayer(clusters);
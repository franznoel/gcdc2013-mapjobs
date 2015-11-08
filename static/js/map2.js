var service;
var markersArray = [];
var map = new google.maps.Map(document.getElementById('map-canvas'),{
  zoom: 12,
  mapTypeId: google.maps.MapTypeId.ROADMAP,
  disableDefaultUI : true,
});

function initialize() {
  // Markers Class
  var Marker = function() {
    this.add = function(listings,type) {
      if (listings.length > 0) {
        var marker, i; 
        for (i=0;i<listings.length;i++) {
          var geopoint = listings[i].geopoint.split(",");
          var image = '/img/'+type+'.png';
          var latLng = new google.maps.LatLng(parseFloat(geopoint[0]),parseFloat(geopoint[1]));
          marker = new google.maps.Marker({ position:latLng, map:map, icon:image, clickable:true });
          google.maps.event.addListener(marker,'click',function(marker,i) {
            return function() {
              marker.showInfoWindow(map,marker);
            }
          });
          markersArray.push(marker);
        }
      }
    }
    
    this.showInfoWindow = function(map,marker) {
      var contentString = this.getInfoWindowContent();
      infowindow = new google.maps.InfoWindow({ content : contentString, });
      infowindow.open(map,marker);
    }
    
    this.remove = function() {
      for (var i = 0; i < markersArray.length; i++) {
        markersArray[i].setMap(null);
      }
      markersArray = [];
    }
   
    this.getInfoWindowContent = function() {
      var html ='';
      html+='<div>Hello</div>';
      return html;
    }
  }  // Marker class end
  
  // Detect browser location
  if (navigator.geolocation) {
    browserSupportFlag = true;
    navigator.geolocation.getCurrentPosition(function(position) {
      initialLocation = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
      map.setCenter(initialLocation);
    }, function() {
      handleNoGeolocation(browserSupportFlag);
    });
  } else { // Browser doesn't support Geolocation
    browserSupportFlag = false;
    handleNoGeolocation(browserSupportFlag);
  }
  
  
}
google.maps.event.addDomListener(window, 'load', initialize);

var param = function(name,value) {
  this.name=name;
  this.value=value;
}

var callback = function(response, status) {
  console.log(response);
}
  

// Search Maps
var searchMaps = function() {
  var data = new Array();
  var formParams = $('#search-form').serializeArray();
  for(var i=0;i<formParams.length;i++){
    data[data.length]=new param(formParams[i].name,formParams[i].value);
  }
  $('#s').val();
  $.ajax({
    url : "/search",
    dataType : "json",
    type : "POST",
    data : data,
    success : function(data,status) {
      var i;
      mark = new Marker();
      mark.remove();
      mark.add(data.jobs,'jobs');
      mark.add(data.resumes,'resumes');
      mark.add(data.profiles,'profiles');
    }
  });
}

//--------------- List 
var setList = function(entity) {
  $.ajax({
    postType : "GET",
    url : "/" + entity,
    success : function(data,status) {
      var html = '';
      html+= '<ul class="list-group">';
      for (var i=0 ; i<data.length; i++) {
        html+='<li class="list-group-item">';
        html+='<h4 class="list-group-item-heading">' + data[i].position + '</h4>';
        html+='<p class="list-group-item-text">' +  minimizeDescription(data[i].description) + '</p>';
        html+='</li>';
        // $('#jobs').html(data[i]);
      }
      html+='</ul>';
      $('#'+entity).html(html);
    }
  });
  // $('#jobs').html(html);
}

var refreshList = function() {
  setList('resumes');
  setList('jobs');
}

var minimizeDescription = function(description) {
  var text_length = 100;
  if (description!=null) {
    if (description.length > text_length) data = description.substring(0,text_length);
    else data = description;
    return data + "...";
  }
}

setTimeout(refreshList(),1000);





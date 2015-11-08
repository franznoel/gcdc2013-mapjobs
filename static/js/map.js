var service;
var markersArray = [];
var mapOptions = {
  zoom: 12,
  mapTypeId: google.maps.MapTypeId.ROADMAP,
  disableDefaultUI : true,
};
var map = new google.maps.Map(document.getElementById('map-canvas'),mapOptions);

function initialize() {
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

var marker_remove = function() {
  for (var i = 0; i < markersArray.length; i++) {
    markersArray[i].setMap(null);
  }
  markersArray = [];
}
    
var param = function(name,value) {
  this.name=name;
  this.value=value;
}

var callback = function(response, status) {
  console.log(response);
}

var getInfoWindowContent = function() {
  var html ='';
  html+='<div>Hello</div>';
  return html;
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
      marker_remove();
      marker_add(data.jobs,'jobs');
      marker_add(data.resumes,'resumes');
      marker_add(data.profiles,'profiles');
      populateList(data.jobs,'jobs');
      populateList(data.resumes,'resumes');
      populateList(data.profiles,'profiles');
      $('#results').show();
    }
  });
}

var marker_add = function(listings,type) {
  if (listings.length > 0) {
    var marker, i; 
    var data = "Hello";
    
    var bounds = new google.maps.LatLngBounds();
    
    for (i=0; i<listings.length; i++) {
      var geopoint = listings[i].geopoint.split(",");
      var image = '/img/'+type+'.png';
      
      var myLatLng = new google.maps.LatLng(parseFloat(geopoint[0]),parseFloat(geopoint[1]))
      
      marker = new google.maps.Marker({
        position : myLatLng,
        map : map,
        icon : image,
        clickable : true,
      });
      
      google.maps.event.addListener(marker,'click',(function(marker,i) {
        var infowindow = new google.maps.InfoWindow({maxWidth : 500});
        return function() {
          infowindow.close();
          console.log(listings);
          html ='';
          if (listings[0].position=="" || listings[0].position==null) { // If profile
            html+='<h4>Profile: '+ listings[0].lastname + ', '+ listings[0].firstname + '</h4>';
            html+='<p><a href="'+ listings[0].link + '" target="_blank">More info</a></p>';
          } else if (listings[0].company=="" || listings[0].company==null) { // If Resumes
            html+='<h4>Resume: '+ listings[0].position + '</h4>';
            html+='<p>'+ listings[0].description + '</p>';
            html+='<p><a href="'+ listings[0].link + '" target="_blank">More info</a></p>';
          } else { // Else Jobs
            html+='<h4>Job: '+ listings[0].position + ' (' + listings[0].company + ')</h4>';
            html+='<p>'+ listings[0].description + '</p>';
            html+='<p><a href="'+ listings[0].link + '" target="_blank">More info</a></p>';
          }
          infowindow.setContent(html);
          infowindow.open(map, marker);
        }
      })(marker, i));
      
      google.maps.event.addListener(map, 'zoom_changed', function() {
        var zoomChangeBoundsListener = google.maps.event.addListener(map, 'bounds_changed', function(event) {
          if (this.getZoom() > 12 && this.initialZoom == true) {
              this.setZoom(12);
              this.initialZoom = false;
          }
          google.maps.event.removeListener(zoomChangeBoundsListener);
        });
      });
      
      bounds.extend(myLatLng);
      markersArray.push(marker);
    }
    map.initialZoom = true;
    map.fitBounds(bounds);
  }
}

//--------------- List
var populateList = function(data,entity) {
  if(data.length<=0) { // If there is no data
    console.log(entity + " is null");
    var html = '';
    if (entity=="resumes") {
      html+= '<div class="alert alert-danger">';
      html+= 'There are no <b>Resumes</b> found. Please try to check <b>Jobs</b>';
    } else if (entity=="jobs") {
      html+= '<div class="alert alert-danger">';
      html+= 'There are no <b>Jobs</b> found. Please try to check <b>Resumes</b>';
    }
    html+='</div>';
    $('#'+entity+'-results').removeClass('active');
  } else {
    var html = '';
    html+= '<ul class="list-group">';
    for (var i=0 ; i<data.length; i++) {
      html+='<li class="list-group-item">';
      html+='<h4 class="list-group-item-heading">' + data[i].position + '</h4>';
      html+='<p class="list-group-item-text">' +  minimizeDescription(data[i].description) + '</p>';
      html+='<a href="'+ data[i].link +'">More info</a>';
      html+='</li>';
    }
    html+='</ul>';
    $('#'+entity+'-results').addClass('active');
  }
  $('#'+entity).html(html);  
}


/*
var setList = function(entity,search) {
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
        html+='<a href="'+ data[i].link +'">More info</a>';
        html+='</li>';
      }
      html+='</ul>';
      $('#'+entity).html(html);
    }
  });
}
*/


var minimizeDescription = function(description) {
  var text_length = 100;
  if (description!=null) {
    if (description.length > text_length) data = description.substring(0,text_length);
    else data = description;
    return data + "...";
  }
}

/*
var refreshList = function() {
  setList('resumes');
  setList('jobs');
}

setTimeout(refreshList(),1000);
*/




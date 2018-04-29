// ==ClosureCompiler==
// @output_file_name app.min.js
// @compilation_level ADVANCED_OPTIMIZATIONS
// ==/ClosureCompiler==

function padLeft(str, length, padChar){
	while(str.length < length){
		str = padChar + str;
	}
	return str;
}
window.addEventListener("load", function(){
	var inputOrigin, inputDestination, btnUseGeolocation, btnSwitchOrigDest,
		btnNow,
		divPlaceFooter = document.getElementById("place-footer"),
		divUseNow = document.getElementById("use-now"),
		locationCallback = function(position){
			inputOrigin.value =
				position.coords.latitude + "," + position.coords.longitude;
		};
	if(divPlaceFooter){
		inputOrigin = document.getElementById("text-orig");
		if(inputOrigin){
			inputDestination = document.getElementById("text-dest");
			// This button sets the origin to the user's current location.
			if(navigator.geolocation){
				btnUseGeolocation = document.createElement("button");
				btnUseGeolocation.textContent =
					"Use Current Location as Origin";
				btnUseGeolocation.addEventListener("click", function(event){
					event.preventDefault();
					navigator.geolocation.getCurrentPosition(locationCallback);
				});
				divPlaceFooter.appendChild(btnUseGeolocation);
			}
			// This button swaps the origin and destination.
			if(inputDestination){
				btnSwitchOrigDest = document.createElement("button");
				btnSwitchOrigDest.textContent = "Reverse";
				btnSwitchOrigDest.addEventListener("click", function(event){
					event.preventDefault();
					var temp = inputOrigin.value;
					inputOrigin.value = inputDestination.value;
					inputDestination.value = temp;
				});
				divPlaceFooter.appendChild(btnSwitchOrigDest);
			}
		}
	}
	if(divUseNow){
		// This button sets the "day" field to the current of the week and the
		// "when" field to the current time.
		btnNow = document.createElement("button");
		btnNow.textContent = "Now";
		btnNow.addEventListener("click", function(event){
			event.preventDefault();
			var now = new Date(),
			select_day = document.getElementById("select_day"),
				time_when = document.getElementById("time_when");
			select_day.children[now.getDay()].selected = true;
			time_when.value =
				padLeft(now.getHours().toString(), 2, '0') + ':' +
				padLeft(now.getMinutes().toString(), 2, '0');
		});
		divUseNow.appendChild(btnNow);
	}
});
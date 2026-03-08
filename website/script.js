fetch("../cheapest_flight.json")
.then(response => response.json())
.then(data => {

document.getElementById("flight").innerHTML = `
Route: ${data.origin} → ${data.destination} <br>
Date: ${data.date} <br>
Price: €${data.price}
`

})

fetch("cheapest_flight.json")
.then(response => response.json())
.then(data => {

document.getElementById("flight").innerHTML = `
Origin: ${data.origin} <br>
Destination: ${data.destination} <br>
Flight date: ${data.flight_date} <br>
Price: €${data.price} <br>
Check date: ${data.check_date}
`

})
.catch(error => {
console.log("Error loading JSON:", error)
})

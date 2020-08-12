// submit a new song request
async function submitRequest()
{
    console.log("Submitting Song Request");

    // get form data
    var inputs = document.querySelectorAll("#new_rq input, textarea");
    var song = inputs[0].value;
    var artist = inputs[1].value;
    var album = inputs[2].value;
    var name = inputs[3].value;
    var message = inputs[4].value;
    var form_json = { 'song': song, 'artist': artist, 'album': album, 'name': name, 'message': message };

    var api = "https://log.wmtu.fm/api/2.0/request";
    var http_headers = {'Content-Type': 'application/json'};
    await fetch(api, {
            method: 'POST', 
            mode: 'no-cors', 
            headers: http_headers, 
            body: JSON.stringify(form_json) })
        .then(function(response) { console.log("Response: " + response); })
        .catch(function(err) { console.log(err); });

    queryAPI(5);
}

// gather requests and display them
function requestBuilder(data)
{
    // selecter for the json data from the API
    var data_select = ['rq_id', 'timestamp', 'song', 'artist', 'album', 'rq_name', 'rq_message'];

    // create a new table body
    var old_body = document.getElementById("requests_body");
    var new_body = document.createElement('tbody');
    new_body.id = "requests_body";

    // add in new rows from the json data
    for (var i = data.length - 1; i >= 0; i--)
    {
        var row_html = "";
        data_select.forEach(function (item, index) 
            { row_html = row_html + '<td>' + data[i][item] + '</td>'; });

        var new_row = new_body.insertRow(0);
        new_row.innerHTML = row_html;
    }

    // remove old table body and replace it with the new data
    old_body.remove();
    document.getElementById("requests").appendChild(new_body);
}

// query the API for new requests
function queryAPI(n)
{
    var url = "https://log.wmtu.fm/api/2.0/log?type=request&n=" + n;

    // fetch json data from the API
    // then send it to the view builder
    fetch(url, {mode: 'no-cors'})
        .then(function(response) { return response.json(); })
        .then(function(data) { requestBuilder(data); })
        .catch(function(err) { console.log(err); });
}

// run things on start up
queryAPI(5);
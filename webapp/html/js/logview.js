// builds the log view and displays it on the page
function logViewBuilder(query_type, data)
{
    var start_build = luxon.DateTime.local();
    console.log("Build Start: " + start_build.toFormat('HH:mm:ss.u').toString());

    // header column names for the table
    var col_names = {
        'song': ['ID', 'Timestamp', 'Song', 'Artist', 'Album', 'Genre', 'Artwork'],
        'discrepancy': ['ID', 'Timestamp', 'Song', 'Artist', 'DJ Name', 'Word', 'Button Hit'],
        'request': ['ID', 'Timestamp', 'Song', 'Artist', 'Album', 'Requester', 'Message']};

    // generate the html code for the header row
    header_html = "";
    col_names[query_type].forEach(function (column, index) {
        header_html = header_html + '<th scope="col">' + column + '</th>'; });
    
    // get the table head element
    var table_header = document.getElementById("log_view_head");
    // remove the existing header data
    table_header.deleteRow(0);
    // add in the new header
    var new_header_row = table_header.insertRow(0);
    new_header_row.innerHTML = header_html;

    // selecter for the json data from the API
    var data_select = {
        'song': ['play_id', 'timestamp', 'song', 'artist', 'album', 'genre', 'artwork'],
        'discrepancy': ['dis_id', 'timestamp', 'song', 'artist', 'dj_ame', 'word', 'button_hit'],
        'request': ['rq_id', 'timestamp', 'song', 'artist', 'album', 'rq_name', 'rq_message']};

    // remove old table body and replace it with the new data
    document.getElementById("log_view_body").remove();
    var new_body = document.createElement('tbody');
    new_body.id = "log_view_body";
    document.getElementById("log_view_table").appendChild(new_body);

    // add in new rows from the json data
    var show_art = document.getElementById("show_art").checked;
    for (var i = data.length - 1; i >= 0; i--)
    {
        var row_html = "";
        data_select[query_type].forEach(function (item, index) 
        {
            if (item == "artwork") 
            { 
                var img_url = data[i][item];
                if (show_art && img_url == "") { img_url = "https://log.wmtu.fm/assets/wmtu_art.png"; }

                // display art as a link or image based on the check box
                if (img_url == "") { row_html = row_html + '<td class="text-center">&nbsp;</td>'; }
                else if (show_art == false) { 
                    row_html = row_html + '<td class="text-center">'
                        + '<a href="' + img_url + '" target="_blank" class="rounded">Artwork</a></td>'; }    
                else 
                { 
                    row_html = row_html + '<td class="text-center">'
                        + '<a href="' + img_url + '" target="_blank" class="rounded">'
                        + '<img src="' + img_url + '" alt="album artwork" class="album-art rounded">'
                        + '</a></td>';
                }
            }
            else { row_html = row_html + '<td>' + data[i][item] + '</td>'; }
        });

        var new_row = new_body.insertRow(0);
        new_row.innerHTML = row_html;
    }

    var end_build = luxon.DateTime.local();
    var build_time = luxon.Interval.fromDateTimes(start_build, end_build).toDuration().toFormat('ss.SSS');
    console.log("Build End:   " + end_build.toFormat('HH:mm:ss.u').toString());
    console.log("Generated in " + build_time + 's');

    // remove loading message and show table
    document.getElementById("log_view_loading").classList.add("d-none");
    document.getElementById("log_view_table").classList.remove("d-none");
}

// queries the API with specified values
function queryAPI(query_func, query_type, ts_start, ts_end)
{
    var log_endpoint = "https://log.wmtu.fm/api/2.0/log";
    var query_args = {'type': query_type, 
                      'ts_start': ts_start, 
                      'ts_end': ts_end,
                      'desc': 'false',
                      'format': 'json' };
    var arg_keys = Object.keys(query_args);

    if (query_func == "down"){ query_args['format'] = 'csv'; }

    // build full query url string
    var arg_string = "?"
    arg_keys.forEach((arg, index) => {
        arg_string = arg_string + `${arg}=${query_args[arg]}` + "&";});
    arg_string = arg_string.substring(0, arg_string.length - 1);
    var query_url = log_endpoint + arg_string;

    console.log("Query:    " + query_url);

    // do the API query based on the specified action
    if (query_func == "down")
    {
        var a = document.createElement("a");
        a.href = query_url;
        a.setAttribute("disabled", "");
        a.click();
    }
    else
    {
        // fetch json data from the API
        // then send it to the view builder
        fetch(query_url)
            .then(function(response) { return response.json(); })
            .then(function(data) { logViewBuilder(query_type, data); })
            .catch(function(err) { console.log(err); });
    }
}

// fetches data from the form on submit
// sends query values to the API
function getFormData(submit_btn)
{
    // use luxon for dates
    var DateTime = luxon.DateTime;
    var Interval = luxon.Interval;

    // get the function type from button press
    var query_func = submit_btn.value;

    // get form date & time values
    var inputs = document.querySelectorAll("#log_query select, input");
    var query_type = inputs[0].value;
    var start_date = inputs[1].value;
    var start_time = inputs[2].value;
    var end_date = inputs[3].value;
    var end_time = inputs[4].value;
    var show_art = inputs[5].checked;
    
    // format time
    if (start_time == "") {start_time = "00:00:00";} else {start_time = start_time + ":00";}
    if (end_time == "") {end_time = "23:59:59";} else {end_time = end_time + ":00";}

    // create timestamps for the api query
    ts_start = start_date + "+" + start_time;
    ts_end = end_date + "+" + end_time;

    // verify provided timestamps
    // make sure end ts actually comes after the start ts
    var ts_start_ISO = DateTime.fromISO(start_date + "T" + start_time);
    var ts_end_ISO   = DateTime.fromISO(end_date + "T" + end_time);
    if (ts_start_ISO >= ts_end_ISO)
    {
        alert("Please provide a starting date and time BEFORE the ending date and time!");
        return false;
    }

    // only allow downloads for intervals longer than a week
    // do some inital set up for the table view
    if (query_func == "view" && Interval.fromDateTimes(ts_start_ISO, ts_end_ISO).length('days') <= 7)
    {
        // hide the table and put a loading message
        document.getElementById("log_view").scrollIntoView();
        document.getElementById("log_view_table").classList.add("d-none");
        document.getElementById("log_view_loading").classList.remove("d-none");       
    }
    else
    {
        alert("Please use the download function for time periods longer than a week!");
        return false;
    }

    console.log("Function: " + query_func);
    console.log("Type:     " + query_type);
    console.log("Start TS: " + ts_start);
    console.log("End TS:   " + ts_end);
    console.log("Show Art: " + show_art);

    queryAPI(query_func, query_type, ts_start, ts_end);
}

// load the last few played songs as a default view for the log viewer
// this will run on page load
function defaultLogView()
{
    var url = "https://log.wmtu.fm/api/2.0/log?n=10";

    // fetch json data from the API
    // then send it to the view builder
    fetch(url)
        .then(function(response) { return response.json(); })
        .then(function(data) { logViewBuilder("song", data); })
        .catch(function(err) { console.log(err); });
}

// run things on start up
defaultLogView();
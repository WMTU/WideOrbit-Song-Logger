// music player 
function wmtuPlay()
{
    // sound object for Howler.js
    var sound = new Howl
    ({
        src: ['https://stream.wmtu.fm/wmtu-live'],
        ext: ['mp3'],
        mobileAutoEnable: true,
        preload: true,
        autoplay: false,
        volume: 1,
        html5: true
    });

    // play and stop the stream on div button click
    function stream()
    {
        if ( stream_id == null || sound.state() == "unloaded" || sound.playing(stream_id) == false )
        {
            console.log("Playing stream...");
            stream_id = sound.play();
            document.getElementById("play_btn_icon").setAttribute('data-feather', "pause");
            feather.replace();
        }
        else
        {
            console.log("Stopping stream...");
            stream_id = sound.stop();
            sound.unload();
            document.getElementById("play_btn_icon").setAttribute('data-feather', "play");
            feather.replace();
        }
    }

    var stream_id = null;
    document.getElementById("play_btn").addEventListener('click', event => { stream(); });
}

// builds the log view and displays it on the page
function logViewBuilder(query_type, data)
{
    // selecter for the json data from the API
    var data_select = {'song': ['song', 'artist', 'album', 'artwork']};

    // set now playing info
    np_img = "../assets/wmtu_art.png"
    if (data[0]['artwork'] != "") { np_img = data[0]['artwork']; }
    document.getElementById('np_art').setAttribute('src', np_img);
    document.getElementById('np_song').textContent = data[0]['song'];
    document.getElementById('np_artist').textContent = data[0]['artist'];
    document.getElementById('np_album').textContent = data[0]['album'];

    // create a new table body
    var old_body = document.getElementById("log_view_body");
    var new_body = document.createElement('tbody');
    new_body.id = "log_view_body";

    // add in new rows from the json data
    var show_art = true;
    for (var i = data.length - 1; i > 0; i--)
    {
        var row_html = "";
        data_select[query_type].forEach(function (item, index) 
        {
            if (item == "artwork") 
            { 
                var img_url = data[i][item];
                if (show_art && img_url == "") { img_url = "../assets/wmtu_art.png"; }

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

    // swap old body for new body
    document.getElementById("log_view_table").replaceChild(new_body, old_body);
}

// queries the API with specified values
var cur_song = "";
var cur_artist = "";
var cur_album = "";
function queryAPI()
{
    n = 6;
    var query_url = "https://log.wmtu.fm/api/2.0/log?delay=false&n=" + n;

    // fetch json data from the API
    // then send it to the view builder
    fetch(query_url, {mode: 'no-cors'})
        .then(function(response) { return response.json(); })
        .then(function(data) { 
            if (data[0]['song'] != cur_song || data[0]['artist'] != cur_artist || data[0]['album'] != cur_album) 
            { 
                cur_song = data[0]['song'];
                console.log("NP Song:   " + cur_song);
                cur_artist = data[0]['artist'];
                console.log("NP Artist: " + cur_artist);
                cur_album = data[0]['album'];
                console.log("NP Album:  " + cur_album);
                logViewBuilder("song", data); 
            }
        })
        .catch(function(err) { console.log(err); });

    setTimeout(queryAPI,5000);
}

// start things on page load
queryAPI(); // initial playlist fetch
wmtuPlay(); // start up the audio player functions
feather.replace(); // load feather icons
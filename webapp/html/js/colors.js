// This is a really basic js script to simply color the page background
// We are using randomColor to generate a color
// https://github.com/davidmerfield/randomColor

// gets a new color using randomColor
function newColor()
{
    var color = randomColor({luminosity: 'light'});
    //console.log("Color: " + color);

    return color;
}

// sets a specified color to the body bg
function setBGColor(color)
{
    document.body.style.backgroundColor = color;
}

// alternates between new colors
// sets the colors as the body bg
// uses CSS transitions for smooth color transition
function rainbowBG(duration)
{
    setBGColor(newColor());
    setTimeout(rainbowBG, duration * 1000, duration);
}

// set the duration of colors in seconds
transition_time = 5;
document.body.style.transition = 'background ' + transition_time + 's';

rainbowBG(transition_time);

// logic.js
// PURPOSE: logic for the html client



const COOKIE_NAME = "verySecureCookie"
const BODY_CONTENT = `<h3 >3010-eeter system:</h3>
<div id="FillContent">
    <form id="log in" onsubmit="return false">
        <div>
            <label for="Username">User name:</label>
        <div>
        <div>
            <input type="text" size="15" id="Username" name="Username">
        </div>
        
        <div style="margin-top: 5px;">
            <label for="Password">Password:</label>
        </div>
            
        <div>
            <input type="text" size="15" id="Password" name="Password">
        </div>
        <div style="margin-top: 5px;">
            <input type="submit" value="Log in" onclick="apiPost('/api/login', 'log in', getTweetPage)">
        </div>
        <div id="badCredentials" style="color: red; display: none;">
            <p>Wrong username or password!</p>
        </div>
    </form>
</div>`

const TWEET_PAGE = `<h3 >3010-eeter system:</h3>
<div>
<form id="tweetForm" onsubmit="return false">
    <label for="tweetInput">New tweet</label>
    <input type="text" size="30" id="tweetInput" name="tweetInput">
    <input type="submit" value="Send it!" onclick="apiPost('/api/tweet', 'tweetForm', getUpdateTweets)">
</form>
</div>
<div>
<input type="submit" value="Logout" onclick="apiDelete('/api/login', logOutClicked)">
</div>
<h1>Tweets</h1>
<div id="tweets">
</div>`

// API functions
function apiPost(url, form, callback)
{
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() 
    {
        
        if (this.readyState == 4 && this.status == 200 )
        {
            callback(this.responseText);
        }

        else if (this.readyState == 4 && this.status == 401)
        {
            document.getElementById("badCredentials").style.display = "block"; //change later so it is handled in a function
        }
    };

    var data = getFormData(form);

    xmlhttp.open("POST", url, true);
    console.log("Sending data: " + JSON.stringify(data));
    xmlhttp.withCredentials = true; //so that the cookie is sent
    xmlhttp.send(JSON.stringify(data));
}

function apiGet(url, callback)
{
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() 
    {
        if (this.readyState == 4 && this.status == 200) 
        {   
            callback(this.responseText);
        }

        else if (this.readyState == 4 && this.status == 401) //if the cookie is not valid for login and client tried getting something needed for log in, give the main page
        {
            document.getElementById("bodyContent").innerHTML = BODY_CONTENT;
        }
      };

    xmlhttp.open("GET", url, true);
    xmlhttp.withCredentials = true; //so that the cookie is sent
    xmlhttp.send();
}

function apiDelete(url, callback)
{
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() 
    {
        if (this.readyState == 4 && this.status == 200) 
        {
            callback();
        }
      };

    xmlhttp.open("DELETE", url, true);
    xmlhttp.withCredentials = true; //so that the cookie is sent
    xmlhttp.send();
}


function getTweetPage() //calls a get api request to get the tweets and then calls the callback function to load the tweet page
{
    apiGet('/api/tweet', tweetPage);
}

function getUpdateTweets() //calls a get api request to get the tweets and then calls the callback function to update tweets on the page
{
    apiGet('/api/tweet', updateTweets);
}

// callback functions
function tweetPage(xmlhttpResponse)
{
    document.getElementById("bodyContent").innerHTML = TWEET_PAGE;
    document.getElementById("tweets").innerHTML = jsonTweetToHtml(xmlhttpResponse);
}


function updateTweets(xmlhttpResponse)
{
    document.getElementById("tweets").innerHTML = jsonTweetToHtml(xmlhttpResponse);
}

//converts the json string of tweets into html elements
function jsonTweetToHtml(tweets)
{
    var tweetHtml = "";
    console.log(tweets)
    tweets = tweets.split('\n')
    tweets.splice(tweets.length-1,1)//remove the empty one
    console.log(tweets)
    tweets.forEach(function(tweet) {
        console.log(tweet.trim())
        tweet = JSON.parse(tweet);
        if(tweet.button == true) //put delete button only if the server called this is the tweet of the same user
        {
            tweetHtml += `
            <div>
                <p style='display:inline-block; margin-right: 20px;'>
                ${tweet.tweet}
                </p>
                <p style='display:inline-block; margin-right: 20px;'>
                ${tweet.username}
                </p>
                <button  onclick="apiDelete('api/tweet/${tweet.uuid}', getUpdateTweets)">Delete</button>
            </div>`
        }

        else 
        {
            tweetHtml += `
            <div>
                <p style='display:inline-block; margin-right: 20px;'>
                ${tweet.tweet}
                </p>
                <p style='display:inline-block; margin-right: 20px;'>
                ${tweet.username}
                </p>
            </div>`
        }
        
    });
    return tweetHtml;
}


function logOutClicked()
{
    document.getElementById("bodyContent").innerHTML = BODY_CONTENT;
}



//miscalleneous functions
function getFormData(form) //returns data from forms in a json format
{
    var formElement = document.getElementById(form);
    var data = {};
    if(form == "log in")
    {
        data = 
        {
            'username': formElement.Username.value,
            'password': formElement.Password.value
        }
    }

    else if(form == "tweetForm")
    {
        data = 
        {
            'tweet': formElement.tweetInput.value
        }
        console.log(formElement.tweetInput.value)
    }

    return data;
}

function checkCookie() // checks if the cookie is valid and if it is, tries to auto log in by getting the tweet page, if not give log in page
{
    cookies = document.cookie;
    if(cookies.includes(COOKIE_NAME))
    {
        cookies.split(";").forEach(function(cookie) {
            var cookie = cookie.split("=");
            if(cookie[0].trim() === COOKIE_NAME)
            {
                var cookieValue = cookie[1];
                if(cookieValue) // if cookie is not empty try to auto log in (keep the session)
                {
                    getTweetPage();
                }
            }
        })
    }

    else
    {
        document.getElementById("bodyContent").innerHTML = BODY_CONTENT;
    }
}
let interval;
let minutes;
let seconds;
function startTimerETC() {
    minutes = 0;
    seconds = 10;

    intervalTimer();
}

function startTimerITC() {
    minutes = 0;
    seconds = 30;

    if (!interval) {
        interval = setInterval(function () {
            if (seconds === 0) {
                if (minutes === 0) {
                    console.log("neyz called how many 1");
                    stopTimer();
                    $("#div-mergely").hide();
                    gotToNextPage1();
                    return;
                } else {
                    minutes--;
                    seconds = 59;
                }
            } else {
                seconds--;
            }
            document.getElementById("timer").innerText = formatTime(minutes, seconds);
        }, 1000);
    }
}
function startSecondTimerITC() {

    logData("set Time clicked - experiment", "set Time clicked - experiment");
    // Avoid multiple intervals running at once
    document.getElementById("timerForm").style.display ="flex";
    document.getElementById("setTimer").style.display ="none";

    document.getElementById("timerForm").addEventListener("submit", function(event) {

        event.preventDefault();

        $("#div-mergely").show();
        document.getElementById('div-mergely').scrollIntoView({behavior: 'smooth'});
        extractMergely();

        // const hoursInput = parseInt(document.getElementById("hours").value) || 0;
        // Calculate the total time in seconds
        /*const totalTimeInSeconds = hoursInput * 3600 + minutesInput * 60;
        minutes = Math.floor(totalTimeInSeconds / 60);
        seconds = totalTimeInSeconds % 60;*/

        minutes = parseInt(document.getElementById("minutes").value) || 0;
        seconds = 0;

        logData("set Time submitted - experiment", minutes);

        // Update the timer display
        document.getElementById("timer").innerText = formatTime(minutes, seconds);

        intervalTimer();
    });
}

function intervalTimer() {
    // Start the timer

    if (!interval) {
        interval = setInterval(function () {
            if (seconds === 0) {
                if (minutes === 0) {
                    stopTimer();
                    gotToNextPage2();
                    console.log("neyz called how many 2");
                    return;
                } else {
                    minutes--;
                    seconds = 59;
                }
            } else {
                seconds--;
            }
            document.getElementById("timer").innerText = formatTime(minutes, seconds);
        }, 1000);
    }
}

function StartHourMinuteTimer() {
    let minutes = document.getElementById("minutes").value;

    console.log("hours value: ", document.getElementById("minutes").value);

    if(minutes === ""){
        alert("Enter minutes");
        return
    }
    document.getElementById("timerForm").style.display ="none";
    // document.getElementById("timer-wrapper-ITC").style.display ="block";
    document.getElementById("timeRemaining").style.display ="block";
    // document.getElementById("setTimer").style.display ="none";
}

function stopTimer() {
    clearInterval(interval);
    interval = null;
}

function resetTimer() {
    stopTimer();
    minutes = 0;
    seconds = 10;
    document.getElementById("timer").innerText = formatTime(minutes, seconds);
}

function formatTime(minutes, seconds) {
    return (minutes < 10 ? "0" : "") + minutes + ":" + (seconds < 10 ? "0" : "") + seconds;
}
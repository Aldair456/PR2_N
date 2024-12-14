document.addEventListener("DOMContentLoaded", function() {
    const videoFeed = document.getElementById("videoFeed");
    const startButton = document.getElementById("startButton");
    const stopButton = document.getElementById("stopButton");

    startButton.addEventListener("click", function() {
        fetch("/start_camera", { method: "POST" })
            .then(response => response.json())
            .then(data => {
                console.log(data.status);
                videoFeed.src = "/video_feed";
            });
    });

    stopButton.addEventListener("click", function() {
        fetch("/stop_camera", { method: "POST" })
            .then(response => response.json())
            .then(data => {
                console.log(data.status);
                videoFeed.src = "";
                videoFeed.srcObject = null;
            });
    });
});

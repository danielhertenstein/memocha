// Code adapted from: https://github.com/webrtc/samples/blob/gh-pages/src/content/getusermedia/record/js/main.js

var video = document.querySelector('video');

var record_button = document.querySelector('button#record');
var upload_button = document.querySelector('button#upload');
record_button.onclick = toggleRecording;

var constraints = {
    audio: true,
    video: true
};

function handleSuccess(stream) {
    record_button.disabled = false;
    console.log('getUserMedia() got stream: ', stream);
    window.stream = stream;
    if (window.URL) {
        video.src = window.URL.createObjectURL(stream);
    } else {
        video.src = stream;
    }
}

function handleError(error) {
    console.log('navigator.getUserMedia error: ', error)
}

navigator.mediaDevices.getUserMedia(constraints).
    then(handleSuccess).catch(handleError);

function toggleRecording() {
    if (record_button.textContent === 'Start Recording') {
        startRecording();
    } else {
        stopRecording();
        record_button.textContent = 'Start Recording';
        upload_button.disabled = false;
    }
}
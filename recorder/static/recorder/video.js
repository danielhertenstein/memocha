// Code adapted from: https://github.com/webrtc/samples/blob/gh-pages/src/content/getusermedia/record/js/main.js

var recordedBlobs;
var mediaRecorder;

var video = document.querySelector('video');

var record_button = document.querySelector('button#record');
var upload_button = document.querySelector('button#upload');
record_button.onclick = toggleRecording;
upload_button.onclick = upload;

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

function startRecording() {
    recordedBlobs = [];
    try {
        mediaRecorder = new MediaRecorder(window.stream);
    } catch(e) {
        console.error('Exception while creating MediaRecorder: ' + e);
        return;
    }
    console.log('Created MediaRecorder', mediaRecorder);
    recordButton.textContent = 'Stop Recording';
    upload_button.disabled = true;
    mediaRecorder.onstop = handleStop;
    mediaRecorder.ondataavailable = handleDataAvailable;
    mediaRecorder.start(10); // 10ms blobs of data
    console.log('MediaRecorder started', mediaRecorder);
}

function stopRecording() {
    mediaRecorder.stop();
    console.log('Recorded Blobs: ', recordedBlobs);
}

function handleDataAvailable(event) {
    if (event.data && event.data.size > 0) {
        recordedBlobs.push(event.data);
    }
}

function handleStop(event) {
    console.log('Recorder stopped: ', event);
}

function upload() {
    // Fill in.
}
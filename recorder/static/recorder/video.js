// Code adapted from: https://github.com/webrtc/samples/blob/gh-pages/src/content/getusermedia/record/js/main.js

var recordedBlobs;
var mediaRecorder;

var video = document.querySelector('video');

var recordButton = document.querySelector('button#record');
recordButton.onclick = toggleRecording;

var constraints = {
    audio: true,
    video: true
};

function handleSuccess(stream) {
    recordButton.disabled = false;
    console.log('getUserMedia() got stream: ', stream);
    window.stream = stream;
    if (window.URL) {
        video.src = window.URL.createObjectURL(stream);
    } else {
        video.src = stream;
    }
    video.muted = true;
}

function handleError(error) {
    console.log('navigator.getUserMedia error: ', error)
}

navigator.mediaDevices.getUserMedia(constraints).
    then(handleSuccess).catch(handleError);

function toggleRecording() {
    if (recordButton.textContent === 'Start Recording') {
        startRecording();
    } else {
        stopRecording();
        recordButton.textContent = 'Upload';
        recordButton.onclick = upload;
        tracks = stream.getTracks();
        for (var i = 0; i < tracks.length; i++) {
            tracks[i].stop()
        }
        video.loop = true;
        video.controls = true;
        video.muted = false;
        var superBuffer = new Blob(recordedBlobs, {type: 'video/webm'});
        video.src = window.URL.createObjectURL(superBuffer);
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
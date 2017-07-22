// Code adapted from: https://github.com/webrtc/samples/blob/gh-pages/src/content/getusermedia/record/js/main.js

var recordedBlobs;
var mediaRecorder;

var form = document.querySelector('form');

var recordVideo = document.querySelector('video#recordVideo');
var playVideo = document.querySelector('video#playVideo');

var recordButton = document.querySelector('button#record');
var uploadButton = document.querySelector('button#upload');
recordButton.onclick = toggleRecording;
uploadButton.onclick = upload;

var constraints = {
    audio: true,
    video: true
};

function handleSuccess(stream) {
    recordButton.disabled = false;
    console.log('getUserMedia() got stream: ', stream);
    window.stream = stream;
    if (window.URL) {
        recordVideo.src = window.URL.createObjectURL(stream);
    } else {
        recordVideo.src = stream;
    }
    recordVideo.muted = true;
    playVideo.style.display = 'none';
}

function handleError(error) {
    console.log('navigator.getUserMedia error: ', error)
}

navigator.mediaDevices.getUserMedia(constraints).
    then(handleSuccess).catch(handleError);

function handleDataAvailable(event) {
    if (event.data && event.data.size > 0) {
        recordedBlobs.push(event.data);
    }
}

function handleStop(event) {
    console.log('Recorder stopped: ', event);
}

function toggleRecording() {
    if (recordButton.textContent === 'Start Recording'
        || recordButton.textContent === 'Record Again') {
        playVideo.pause();
        playVideo.currentTime = 0;
        playVideo.style.display = 'none';
        tracks = stream.getTracks();
        for (var i = 0; i < tracks.length; i++) {
            tracks[i].enabled = true;
        }
        recordVideo.style.display = '';
        startRecording();
    } else {
        stopRecording();
        recordButton.textContent = 'Record Again';
        recordVideo.style.display = 'none';
        tracks = stream.getTracks();
        for (var i = 0; i < tracks.length; i++) {
            tracks[i].enabled = false;
        }
        playVideo.controls = true;
        playVideo.style.display = '';
        var superBuffer = new Blob(recordedBlobs, {type: 'video/webm'});
        playVideo.src = window.URL.createObjectURL(superBuffer);
        uploadButton.disabled = false;
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

function upload() {
    my_blob = new Blob(recordedBlobs, {type: 'video/webm'});
    form.file.value = my_blob;
    form.submit();
}
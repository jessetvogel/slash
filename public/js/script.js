"use strict";
window.addEventListener('DOMContentLoaded', init);
function init() {
    const hostname = window.location.hostname;
    const port = window.location.port;
    const socket = new WebSocket(`ws://${hostname}:${port}/ws`);
    socket.onopen = function (event) {
        console.log('Connection established!');
        socket.send("get");
    };
    socket.onmessage = function (event) {
        console.log('Message from server:', event.data);
    };
    socket.onerror = function (error) {
        console.log('WebSocket Error:', error);
    };
    socket.onclose = function (event) {
        console.log('Connection closed.');
    };
}

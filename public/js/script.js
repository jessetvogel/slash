import { $, create } from "./utils.js";
window.addEventListener('DOMContentLoaded', init);
class Client {
    constructor() {
        this.socket = null;
        this.onclick = this.onclick.bind(this);
    }
    connect() {
        const hostname = window.location.hostname;
        const port = window.location.port;
        this.socket = new WebSocket(`ws://${hostname}:${port}/ws`);
        console.log("Connecting to server ..");
        const client = this;
        this.socket.onopen = function (event) {
            console.log('Connection established!');
        };
        this.socket.onmessage = function (event) {
            try {
                console.info(`%c${event.data}`, 'color: gray;');
                const message = JSON.parse(event.data);
                client.handle(message);
            }
            catch (error) {
                console.error(`Failed to parse message from server!\nmessage: ${event.data}\nerror: ${error}`);
            }
        };
        this.socket.onerror = function (error) {
            console.log('WebSocket error:', error);
        };
        this.socket.onclose = function (event) {
            console.log('Connection closed.');
        };
    }
    handle(message) {
        const event = message.event;
        if (event == "create") {
            const parent = $(message.parent);
            const tag = message.tag;
            if (tag == "text") {
                parent.append(message.text);
                return;
            }
            const id = message.id;
            const elem = create(tag, { id: id });
            parent.append(elem);
            this.update(elem, message);
            return;
        }
        if (event == "remove") {
            const elem = $(message.id);
            elem.remove();
            return;
        }
        if (event == "update") {
            const elem = $(message.id);
            this.update(elem, message);
            return;
        }
        if (event == "script") {
            const script = message.script;
            eval === null || eval === void 0 ? void 0 : eval(`"use strict";(${script})`);
            return;
        }
        throw new Error(`Unknown event '${event}'`);
    }
    update(elem, message) {
        for (const attr in message) {
            if (attr == "event" || attr == "id" || attr == "parent" || attr == "tag")
                continue;
            if (attr == "style") {
                for (const [key, value] of Object.entries(message.style)) {
                    if (typeof value !== 'string')
                        throw new Error(`Invalid value for style property ${key}`);
                    elem.style.setProperty(key, value);
                }
                continue;
            }
            if (attr == "onclick") {
                if (message.onclick === true) {
                    elem.addEventListener("click", this.onclick);
                }
                else {
                    elem.removeEventListener("click", this.onclick);
                }
                continue;
            }
            throw new Error(`Unknown attribute ${attr}`);
        }
    }
    onclick(event) {
        const elem = event.currentTarget;
        if (elem instanceof HTMLElement) {
            this.send({
                event: "click",
                id: elem.id
            });
            event.stopPropagation();
        }
    }
    send(message) {
        var _a;
        (_a = this.socket) === null || _a === void 0 ? void 0 : _a.send(JSON.stringify(message));
    }
}
;
let client;
function init() {
    client = new Client();
    client.connect();
}
